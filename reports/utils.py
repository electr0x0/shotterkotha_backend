import os
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.conf import settings
import magic  # for mime type detection
import json
from .image_analysis import analyze_image
from google import genai

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
    try:
        API_KEY = 'AIzaSyBVLwDtAHrLoiBHqBJ-KbbIfBpwFChoEYo'
 # Make sure to set this in your environment
        client = genai.Client(api_key=API_KEY)
        
        print(image_path)

        image_path = os.path.join(settings.MEDIA_ROOT, image_path)

        
        image_file = client.files.upload(file=image_path)
        
        # Prompt engineering for detailed crime analysis
        prompt = """
        You are an expert crime scene investigator and report writer. Analyze this image and provide a detailed response in the following JSON format:
        Use this JSON schema:
        {
            "isCrime": boolean (true if image shows any crime, suspicious activity, or evidence of crime),
            "title": "A concise but descriptive title for a crime report",
            "description": "A detailed description as if writing a crime report. Include:
                - What is visible in the image
                - Any potential evidence
                - Environmental details
                - Suspicious elements
                - Potential severity of the situation
                Make it as detailed as possible while maintaining professional language.",
            "severity": "low|medium|high",
            "category": "theft|assault|fraud|vandalism|other"
        }
        
        If no crime-related content is visible, return isCrime as false with minimal other details.
        Ensure your response is valid JSON and not a string. It must be a JSON object. staring wit { and ending with }
        Make sure its not markdown with ```json or ```
        """
        
        # Generate content using the correct model and format
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, image_file]
        )


        cleaned_text = response.text.strip('`').strip()

        if cleaned_text.startswith('json\n'):
            cleaned_text = cleaned_text[5:]


        result = json.loads(cleaned_text)

        print("GOOGLE GEMINI RESPONSE", result)
        


        return result
            
    except Exception as e:
        # Handle any other errors
        error_response = {
            "isCrime": False,
            "title": "Error analyzing image",
            "description": f"An error occurred while analyzing the image: {str(e)}",
            "severity": "low",
            "category": "other"
        }
        return json.dumps(error_response)

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