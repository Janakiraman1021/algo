"""AI Text Summarization Engine for AgentPay SummaryAgent.

Supports multi-provider LLMs (Gemini, Groq, OpenAI) with deterministic fallback.
"""

import os
import re
import logging
import httpx
from typing import Optional
from app.config import settings

logger = logging.getLogger("agentpay.ai")

class AISummarizer:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.groq_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    async def summarize(self, text: str) -> str:
        """Generate a concise 2-4 sentence summary of the input text."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return "No input text was provided to summarize."

        # If text is already very short, summarize concisely
        if len(cleaned_text.split()) <= 15:
            return f"Summary: {cleaned_text}"

        # 1. Try Gemini if configured
        if self.provider == "gemini" and self.gemini_key:
            try:
                summary = await self._summarize_with_gemini(cleaned_text)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"Gemini summarization failed: {e}. Falling back to secondary engine.")

        # 2. Try Groq if configured
        if (self.provider == "groq" or not self.gemini_key) and self.groq_key:
            try:
                summary = await self._summarize_with_groq(cleaned_text)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"Groq summarization failed: {e}. Falling back to secondary engine.")

        # 3. Try OpenAI if configured
        if (self.provider == "openai" or (not self.gemini_key and not self.groq_key)) and self.openai_key:
            try:
                summary = await self._summarize_with_openai(cleaned_text)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"OpenAI summarization failed: {e}. Falling back to local engine.")

        # 4. Deterministic Local Summarizer Fallback (Zero external API dependencies needed)
        return self._summarize_locally(cleaned_text)

    async def _summarize_with_gemini(self, text: str) -> Optional[str]:
        """Summarize using Google Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = (
            "You are an expert AI summarization agent in an Agent-to-Agent micropayment marketplace. "
            "Provide a concise, highly readable, 2 to 4 sentence summary of the following text:\n\n"
            f"{text}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            else:
                logger.warning(f"Gemini API returned status {res.status_code}: {res.text}")
        return None

    async def _summarize_with_groq(self, text: str) -> Optional[str]:
        """Summarize using Groq API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional AI summarizer. Provide a concise 2-4 sentence summary."
                },
                {"role": "user", "content": f"Summarize this text:\n\n{text}"}
            ],
            "max_tokens": 200,
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        return None

    async def _summarize_with_openai(self, text: str) -> Optional[str]:
        """Summarize using OpenAI REST API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional AI summarizer. Provide a concise 2-4 sentence summary."
                },
                {"role": "user", "content": f"Summarize this text:\n\n{text}"}
            ],
            "max_tokens": 200,
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        return None

    def _summarize_locally(self, text: str) -> str:
        """Deterministic extractive summarizer for offline and reliable MVP operations."""
        # Split text into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if len(sentences) <= 3:
            return " ".join(sentences)

        # Score sentences by word importance / position
        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "it", "this", "that"}
        for w in words:
            if w not in stop_words and len(w) > 2:
                word_freq[w] = word_freq.get(w, 0) + 1

        scored = []
        for i, sent in enumerate(sentences):
            sent_words = re.findall(r'\w+', sent.lower())
            score = sum(word_freq.get(w, 0) for w in sent_words)
            # Boost first and last sentences
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.2
            scored.append((score, i, sent))

        # Pick top 3 sentences preserving original order
        scored.sort(key=lambda x: x[0], reverse=True)
        top_sentences = sorted(scored[:3], key=lambda x: x[1])
        summary = " ".join(s[2] for s in top_sentences)
        return summary

# Global instance
ai_summarizer = AISummarizer()
