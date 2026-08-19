import base64
import io
from PIL import Image

PROMPT = """Você é um assistente especializado em responder questões de múltipla escolha com precisão.

Analise a imagem e siga este formato de resposta obrigatório:

RESPOSTA: [letra ou número da alternativa correta]

EXPLICAÇÃO:
[Explique por que essa alternativa está correta e, se relevante, por que as outras estão erradas. Seja direto e técnico.]

Regras:
- Responda sempre em português
- Identifique a alternativa correta com base no conteúdo da questão
- Não invente informações que não estejam na imagem ou no seu conhecimento
- Se a imagem estiver ilegível ou incompleta, informe isso claramente"""

PROVIDERS = {
    "Anthropic": {
        "models": {
            "Haiku (rápido/barato)": "claude-haiku-4-5-20251001",
            "Sonnet (mais preciso)": "claude-sonnet-5-20251001",
        },
        "env_key": "ANTHROPIC_API_KEY",
    },
    "OpenAI": {
        "models": {
            "GPT-4o Mini (rápido/barato)": "gpt-4o-mini",
            "GPT-4o (mais preciso)": "gpt-4o",
        },
        "env_key": "OPENAI_API_KEY",
    },
    "Google": {
        "models": {
            "Gemini Flash (rápido/barato)": "gemini-1.5-flash",
            "Gemini Pro (mais preciso)": "gemini-1.5-pro",
        },
        "env_key": "GOOGLE_API_KEY",
    },
}


def _image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def ask_anthropic(image: Image.Image, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": _image_to_base64(image),
                    },
                },
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return message.content[0].text


def ask_openai(image: Image.Image, model: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{_image_to_base64(image)}"
                    },
                },
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return response.choices[0].message.content


def ask_google(image: Image.Image, model: str) -> str:
    import os
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=buffer.getvalue(), mime_type="image/png"),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        ),
    )
    return response.text


_HANDLERS = {
    "Anthropic": ask_anthropic,
    "OpenAI": ask_openai,
    "Google": ask_google,
}


def ask_question(image: Image.Image, provider: str, model: str) -> str:
    return _HANDLERS[provider](image, model)
