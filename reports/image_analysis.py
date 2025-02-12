import os
from google import genai





def analyze_image(image_path: str) -> dict:
    """
    Analyze an image using Gemini Vision API and return a structured JSON response.
    
    Args:
        image_path (str): Path to the image file to analyze
        
    Returns:
        dict: JSON response containing crime analysis
    """
    client = genai.Client(api_key='AIzaSyBVLwDtAHrLoiBHqBJ-KbbIfBpwFChoEYo')
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
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, image_file]
    )
    
    return response.text

if __name__ == "__main__":
    # Example usage
    image_path = "c1.jpg"  # Replace with your image path
    description = analyze_image(image_path)
    print("\nImage Analysis:")
    print(description)