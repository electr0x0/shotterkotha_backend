import os

from google import genai



def get_gemini_response(prompt: str) -> str:
    """
    Get a response from Gemini model based on the input prompt.
    
    Args:
        prompt (str): The input prompt to send to Gemini
        
    Returns:
        str: The response from Gemini
    """
    API_KEY = 'AIzaSyBVLwDtAHrLoiBHqBJ-KbbIfBpwFChoEYo'
    
    client = genai.Client(api_key=API_KEY)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-preview-02-05", contents=prompt
    )
    
    print(response.text)

    
    return response.text

# Example usage
if __name__ == "__main__":
    sample_prompt = "Tell me a joke"
    response = get_gemini_response(sample_prompt)
    print(response)