import base64
import io
from PIL import Image

PROMPT_IMAGE = """Você é um assistente especializado em responder questões de múltipla escolha com precisão.

Analise a imagem e siga este formato de resposta obrigatório:

RESPOSTA: [letra ou número da alternativa correta]

EXPLICAÇÃO:
[Explique por que essa alternativa está correta e, se relevante, por que as outras estão erradas. Seja direto e técnico.]

Regras:
- Responda sempre em português
- Identifique a alternativa correta com base no conteúdo da questão
- Não invente informações que não estejam na imagem ou no seu conhecimento
- Se a imagem estiver ilegível ou incompleta, informe isso claramente"""

PROMPT_TEXT = """Você é um assistente especializado em responder questões de múltipla escolha com precisão.

Abaixo está o texto de uma questão de múltipla escolha. Siga este formato de resposta obrigatório:

RESPOSTA: [letra ou número da alternativa correta]

EXPLICAÇÃO:
[Explique por que essa alternativa está correta e, se relevante, por que as outras estão erradas. Seja direto e técnico.]

Regras:
- Responda sempre em português
- Identifique a alternativa correta com base no conteúdo da questão
- Não invente informações que não estejam no texto ou no seu conhecimento

Questão:
{text}"""

PROVIDERS = {
    "Anthropic": {
        "models": {
            "Haiku latest (rápido/barato)": "claude-haiku-4-5-latest",
            "Sonnet latest (mais preciso)": "claude-sonnet-4-5-latest",
            "Personalizado": "__custom__",
        },
        "env_key": "ANTHROPIC_API_KEY",
    },
    "OpenAI": {
        "models": {
            "GPT-4o Mini (rápido/barato)": "gpt-4o-mini",
            "GPT-4o (mais preciso)": "gpt-4o",
            "Personalizado": "__custom__",
        },
        "env_key": "OPENAI_API_KEY",
    },
    "Google": {
        "models": {
            "Gemini Flash latest (rápido/barato)": "gemini-flash-latest",
            "Gemini Pro latest (mais preciso)": "gemini-pro-latest",
            "Personalizado": "__custom__",
        },
        "env_key": "GOOGLE_API_KEY",
    },
}


def _image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def ask_anthropic_image(image: Image.Image, model: str) -> str:
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
                {"type": "text", "text": PROMPT_IMAGE},
            ],
        }],
    )
    return message.content[0].text


def ask_anthropic_text(text: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": PROMPT_TEXT.format(text=text),
        }],
    )
    return message.content[0].text


def ask_openai_image(image: Image.Image, model: str) -> str:
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
                    "image_url": {"url": f"data:image/png;base64,{_image_to_base64(image)}"},
                },
                {"type": "text", "text": PROMPT_IMAGE},
            ],
        }],
    )
    return response.choices[0].message.content


def ask_openai_text(text: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": PROMPT_TEXT.format(text=text),
        }],
    )
    return response.choices[0].message.content


def ask_google_image(image: Image.Image, model: str) -> str:
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
            PROMPT_IMAGE,
        ],
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        ),
    )
    print(f"[DEBUG] Gemini finish_reason: {response.candidates[0].finish_reason if response.candidates else 'sem candidatos'}")
    text = response.text
    if not text:
        return "Gemini não retornou resposta. Possível bloqueio por filtro de segurança."
    return text


def ask_google_text(text: str, model: str) -> str:
    import os
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    response = client.models.generate_content(
        model=model,
        contents=PROMPT_TEXT.format(text=text),
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        ),
    )
    print(f"[DEBUG] Gemini finish_reason: {response.candidates[0].finish_reason if response.candidates else 'sem candidatos'}")
    result = response.text
    if not result:
        return "Gemini não retornou resposta. Possível bloqueio por filtro de segurança."
    return result


_IMAGE_HANDLERS = {
    "Anthropic": ask_anthropic_image,
    "OpenAI": ask_openai_image,
    "Google": ask_google_image,
}

_TEXT_HANDLERS = {
    "Anthropic": ask_anthropic_text,
    "OpenAI": ask_openai_text,
    "Google": ask_google_text,
}


def ask_from_image(image: Image.Image, provider: str, model: str) -> str:
    return _IMAGE_HANDLERS[provider](image, model)


def ask_from_text(text: str, provider: str, model: str) -> str:
    return _TEXT_HANDLERS[provider](text, model)
