import os
from google import genai
import json
import mimetypes





def analyze_image(image_path: str) -> str:
    """
    Analyze an image using Gemini Vision API and return a structured JSON response.
    
    Args:
        image_path (str): Path to the image file to analyze
        
    Returns:
        str: JSON string containing crime analysis
    """
    try:
        API_KEY = 'AIzaSyBVLwDtAHrLoiBHqBJ-KbbIfBpwFChoEYo'
 # Make sure to set this in your environment
        client = genai.Client(api_key=API_KEY)
        
        print(image_path)

        
        image_file = client.files.upload(file=image_path)
        
        # Prompt engineering for detailed crime analysis
        prompt = """
        You are an expert crime scene investigator and report writer. Analyze this image and provide a detailed response in the following JSON format:
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
        Ensure your response is valid JSON.
        """
        
        # Generate content using the correct model and format
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, image_file]
        )
        
        # Ensure the response is properly formatted as JSON
        try:
            json_response = json.loads(response.text)
            return json.dumps(json_response)
        except json.JSONDecodeError:
            default_response = {
                "isCrime": False,
                "title": "Unable to analyze image",
                "description": "The image analysis produced invalid results",
                "severity": "low",
                "category": "other"
            }
            return json.dumps(default_response)
            
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

if __name__ == "__main__":
    # Example usage
    image_path = "c1.jpg"  # Replace with your image path
    description = analyze_image(image_path)
    print("\nImage Analysis:")
    print(description)