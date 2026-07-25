"""
Groq API service wrapper with streaming support and mock fallback.
"""
import json
import os
from typing import AsyncIterator, Optional

from app.core.config import settings

# Try to import groq; fall back to mock if not installed or no key
try:
    from groq import AsyncGroq
    _groq_available = bool(settings.GROQ_API_KEY)
except ImportError:
    _groq_available = False


class GroqService:
    def __init__(self):
        if _groq_available:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        else:
            self.client = None
        self.model = settings.GROQ_MODEL

    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """Non-streaming completion. Returns full text."""
        if not self.client:
            return self._mock_response(messages[-1].get("content", ""))

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    async def stream_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Streaming completion. Yields text chunks."""
        if not self.client:
            mock = self._mock_response(messages[-1].get("content", ""))
            for word in mock.split(" "):
                yield word + " "
            return

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _mock_response(self, user_input: str) -> str:
        """Fallback response when no Groq key is set."""
        return (
            "🤖 **SkillBridge AI** (Demo Mode — add your GROQ_API_KEY to enable real AI)\n\n"
            f"You asked: *{user_input[:100]}*\n\n"
            "**What I'd tell you with a real API key:**\n"
            "- Analyze your skills and identify gaps\n"
            "- Generate a personalized learning roadmap\n"
            "- Recommend specific projects to build\n"
            "- Help you prepare for interviews\n\n"
            "Get your free Groq API key at [console.groq.com](https://console.groq.com) and add it to your `.env` file."
        )


groq_service = GroqService()
