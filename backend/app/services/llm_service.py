"""
LLM service supporting Ollama, OpenAI, and Gemini.
"""
from __future__ import annotations

import requests

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

_client = None


def _get_openai_client():
    from openai import OpenAI
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _get_gemini_client():
    from google import genai

    global _client

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing.")

    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)

    return _client


def generate(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.2
) -> str:

    if settings.LLM_PROVIDER == "gemini":
        return _generate_gemini(prompt, system, temperature)

    if settings.LLM_PROVIDER == "openai":
        return _generate_openai(prompt, system, temperature)

    return _generate_ollama(prompt, system, temperature)


def _generate_ollama(
    prompt: str,
    system: str | None,
    temperature: float
) -> str:

    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        response = requests.post(
            url,
            json={
                "model": settings.OLLAMA_CHAT_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=180,
        )

        response.raise_for_status()
        return response.json().get("response", "")

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Couldn't reach Ollama at {settings.OLLAMA_BASE_URL}."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        logger.exception("Ollama generation failed")
        raise RuntimeError("Ollama returned an error.") from exc


def _generate_openai(
    prompt: str,
    system: str | None,
    temperature: float
) -> str:

    client = _get_openai_client()

    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    except Exception:
        logger.exception("OpenAI generation failed")
        raise


def _generate_gemini(
    prompt: str,
    system: str | None,
    temperature: float
) -> str:

    from google.genai import types

    client = _get_gemini_client()

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=temperature,
            ),
        )

        return response.text or ""

    except Exception:
        logger.exception("Gemini generation failed")
        raise