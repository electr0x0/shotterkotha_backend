from groq import Groq
from typing import Tuple

def get_groq_response(prompt: str) -> Tuple[str, str]:
    """
    Get a response from Groq model specialized in Bangladesh crime rules and emergency contacts.
    
    Args:
        prompt (str): The input prompt to send to Groq
        
    Returns:
        Tuple[str, str]: (thinking_process, response)
    """
    API_KEY = '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'
    
    system_context = """You are a helpful assistant that can answer questions on crime and criminal activities, also they can provide emergency contancts. All in the context of Bangladesh"
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