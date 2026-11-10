"""
LLM service — thin wrapper so the rest of the app doesn't care which
provider (Ollama, OpenAI, or Gemini) is actually generating text.

Defaults to Ollama: a fully local model server, so this works with zero
API keys and zero cost. Install it from https://ollama.com, then:
    ollama pull llama3.2
    ollama serve   (usually starts automatically)
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


def generate(prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
    """
    Generate a completion from the configured LLM provider.

    Kept deliberately simple (single-turn, prompt-in/text-out) since all
    conversational state and grounding is handled explicitly in the prompt
    templates before it ever reaches this function.
    """
    if settings.LLM_PROVIDER == "gemini":
        return _generate_gemini(prompt, system, temperature)
    if settings.LLM_PROVIDER == "openai":
        return _generate_openai(prompt, system, temperature)
    return _generate_ollama(prompt, system, temperature)


def _generate_ollama(prompt: str, system: str | None, temperature: float) -> str:
    """
    Call a locally running Ollama server. No API key needed — this is the
    free/offline path. Raises a clear, actionable error if Ollama isn't
    running or the model hasn't been pulled yet.
    """
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
            "Couldn't reach Ollama at "
            f"{settings.OLLAMA_BASE_URL}. Is it running? Start it with `ollama serve`, "
            f"and make sure you've pulled the model: `ollama pull {settings.OLLAMA_CHAT_MODEL}`."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        logger.exception("Ollama generation failed")
        raise RuntimeError(
            f"Ollama returned an error. Make sure the model is pulled: "
            f"`ollama pull {settings.OLLAMA_CHAT_MODEL}`."
        ) from exc


def _generate_openai(prompt: str, system: str | None, temperature: float) -> str:
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


def _generate_gemini(prompt: str, system: str | None, temperature: float) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        settings.GEMINI_CHAT_MODEL, system_instruction=system
    )
    try:
        response = model.generate_content(
            prompt, generation_config={"temperature": temperature}
        )
        return response.text or ""
    except Exception:
        logger.exception("Gemini generation failed")
        raise
