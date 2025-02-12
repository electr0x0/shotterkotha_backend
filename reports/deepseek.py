from groq import Groq
from typing import Tuple

def get_groq_response(prompt: str) -> Tuple[str, str]:
    """
    Get a response from Groq model specialized in Bangladesh traffic rules education.
    
    Args:
        prompt (str): The input prompt to send to Groq
        
    Returns:
        Tuple[str, str]: (thinking_process, response)
    """
    API_KEY = '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'
    
    system_context = """You are a knowledgeable expert on Bangladesh traffic rules, road safety, and driving regulations. 
    
    Your primary goals are:
    1. Educate users about proper traffic rules in Bangladesh
    2. Explain why following traffic rules is crucial for safety
    3. Provide practical advice for road safety
    4. Respond in Bangla if the user asks in Bangla or requests Bangla response
    5. Share real consequences of traffic rule violations
    6. Promote responsible driving behavior
    
    When responding:
    - Be clear and authoritative about traffic rules
    - Use real examples from Bangladesh context
    - Emphasize safety and responsibility
    - Include specific local laws and penalties when relevant
    - If the user writes in Bangla, respond in Bangla
    - Dont respond to other questions except for question that are related or somehwat related to Traffic Rules and Traffic of Bangladesh.
    """
    
    client = Groq(api_key=API_KEY)
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )

    response_text = ""
    for chunk in completion:
        chunk_content = chunk.choices[0].delta.content or ""
        response_text += chunk_content
    
    # Split the response into thinking process and actual response
    parts = response_text.split("</think>")
    if len(parts) > 1:
        thinking = parts[0].replace("<think>", "").strip()
        response = parts[1].strip()
    else:
        thinking = ""
        response = response_text
    
    return thinking, response

# Example usage
if __name__ == "__main__":
    sample_prompt = "বাংলাদেশে ট্রাফিক সিগন্যাল মেনে চলার গুরুত্ব কি?"
    thinking, response = get_groq_response(sample_prompt)
    
    # Save response to file
    with open("response.txt", "w", encoding="utf-8") as f:
        f.write(f"Thinking: {thinking}\n\nResponse: {response}")
