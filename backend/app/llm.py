from __future__ import annotations

from typing import Any

from sarvamai import SarvamAI


class SarvamClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = SarvamAI(api_subscription_key=api_key) if api_key else None

    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self.client:
            return (
                "Sarvam API key is not configured. "
                "Set SARVAM_API_KEY in backend/.env to enable live generation."
            )

        response = self.client.chat.completions(
            messages=[
                {"role": "system", "content": "You are a helpful customer support assistant."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return self._extract_text(response)

    def _extract_text(self, response: Any) -> str:
        if isinstance(response, str):
            return response.strip()

        if isinstance(response, dict):
            if "output_text" in response and response["output_text"]:
                return str(response["output_text"]).strip()
            choices = response.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content")
                if content:
                    return str(content).strip()
            return str(response)

        for attr in ("output_text", "text", "content"):
            value = getattr(response, attr, None)
            if value:
                return str(value).strip()

        choices = getattr(response, "choices", None)
        if choices:
            first_choice = choices[0]
            message = getattr(first_choice, "message", None)
            if message:
                content = getattr(message, "content", None)
                if content:
                    return str(content).strip()

        return str(response)
