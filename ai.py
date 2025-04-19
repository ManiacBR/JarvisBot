import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def estimate_tokens(messages, model="gpt-4.1-2025-04-14"):
    encoding = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += 4  # tokens base para estrutura da API
        for v in msg.values():
            total += len(encoding.encode(str(v)))
    return total

async def ask_openai(context, model="gpt-4.1-2025-04-14", max_tokens_ctx=100_000):
    ctx = context[-2000:]  # pega muitas mensagens, ajusta se quiser
    while ctx and estimate_tokens(ctx, model) > max_tokens_ctx:
        ctx.pop(0)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=ctx
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ocorreu um erro: {e}"
