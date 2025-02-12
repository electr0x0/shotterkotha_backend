import os
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.conf import settings
import magic  # for mime type detection
import json
from .image_analysis import analyze_image

def compress_image(image_file):
    """
    Compress and optimize image for web using Pillow.
    Returns compressed image file.
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        max_size = (1920, 1080)  # Full HD
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Create a BytesIO object to store the compressed image
        output = BytesIO()
        
        # Save the image with optimal settings
        img.save(
            output, 
            format='JPEG', 
            quality=85,  # Good balance between quality and size
            optimize=True,
            progressive=True
        )
        output.seek(0)
        
        # Create a new Django-friendly file
        return File(output, name=image_file.name)
    
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return image_file

def compress_video(video_file):
    """
    Compress video using FFmpeg.
    Returns compressed video file path.
    """
    try:
        import ffmpeg
        
        output_filename = f"compressed_{os.path.basename(video_file.name)}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'temp', output_filename)
        
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg compression settings
        stream = ffmpeg.input(video_file.temporary_file_path())
        stream = ffmpeg.output(
            stream, 
            output_path,
            **{
                'c:v': 'libx264',  # video codec
                'crf': '28',       # compression quality (23-28 is good)
                'preset': 'medium',  # compression speed
                'c:a': 'aac',      # audio codec
                'b:a': '128k',     # audio bitrate
                'maxrate': '2M',   # maximum bitrate
                'bufsize': '2M',   # buffer size
                'vf': 'scale=-2:720'  # scale to 720p
            }
        )
        
        ffmpeg.run(stream, overwrite_output=True)
        
        # Return compressed video as File object
        with open(output_path, 'rb') as f:
            compressed = File(f, name=output_filename)
            return compressed
            
    except Exception as e:
        print(f"Error compressing video: {str(e)}")
        return video_file
    finally:
        # Cleanup temporary files
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

def process_media_file(file):
    """
    Process uploaded media file based on its type.
    Returns tuple of (processed_file, media_type)
    """
    # Detect mime type
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer
    
    if mime.startswith('image/'):
        return compress_image(file), 'image'
    elif mime.startswith('video/'):
        return compress_video(file), 'video'
    else:
        raise ValueError('Unsupported media type')

def generate_image_description(image_path):
    """
    Generate AI description for an image using Gemini Vision.
    Returns the analysis as a dictionary.
    """
    try:
        analysis = analyze_image(image_path)
        # Parse the JSON response
        result = json.loads(analysis)
        return result
    except Exception as e:
        print(f"Error generating image description: {str(e)}")
        return {
            "isCrime": False,
            "title": "Error analyzing image",
            "description": "Failed to analyze image content",
            "severity": "low",
            "category": "other"
        }

def isValidCrimePost(post):
    """
    Validate if a post is a legitimate crime report by checking
    the AI analysis of attached media.
    """
    try:
        # Check all media attachments
        for media in post.media.all():
            if media.media_type == 'image':
                analysis = generate_image_description(media.file.path)
                if analysis.get('isCrime', False):
                    return True
        
        # If no images confirm crime, return False
        return False
    except Exception as e:
        print(f"Error validating crime post: {str(e)}")
        return False 