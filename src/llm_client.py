from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def ask_llm(prompt, model="gpt-5-nano", system_message=None, max_tokens=512):
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    response = client.responses.create(
        model=model,
        input=messages,
        max_output_tokens=max_tokens,
        store=False,
    )
    return response.output_text.strip()
