"""LLM client for generating digests using Groq."""

import logging

from openai import OpenAI

from ..config.constants import (
    DEFAULT_GROQ_MODEL,
    DEFAULT_GROQ_TEMPERATURE,
    DEFAULT_GROQ_URL,
    DIGEST_MAX_WORDS,
    DIGEST_MIN_WORDS,
)
from ..prompts import get_prompt

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client using Groq for fast cloud inference and comprehensive answers."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize LLM client with Groq.

        Args:
            model: Groq model identifier (defaults to llama-3.3-70b-versatile)
            api_key: Groq API key (required)
        """
        if not api_key:
            raise ValueError("Groq API key is required")

        self.model = model or DEFAULT_GROQ_MODEL
        self.base_url = DEFAULT_GROQ_URL
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
        )
        logger.info(f"LLM client initialized with Groq model: {self.model}")

    async def generate_answer(
        self,
        topic: str,
        context: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a comprehensive answer using the LLM.

        Args:
            topic: Topic or question to answer
            context: Research context from search results
            system_prompt: Optional custom system prompt
            max_tokens: Maximum tokens in response (None = no limit)

        Returns:
            Generated answer text
        """
        default_system_prompt = get_prompt("system_answer")

        user_prompt = f"""Answer this question comprehensively: {topic}

Based on these search results:

{context}

Provide a thorough, well-structured answer that covers all the important information."""

        try:
            # Build request params
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt or default_system_prompt,
                    },
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
            }

            # Only add max_tokens if specified
            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)

            answer = response.choices[0].message.content
            if answer:
                return answer.strip()
            return ""

        except Exception as e:
            logger.error("Error generating answer: %s", e)
            raise

    async def answer_question(
        self,
        question: str,
        conversation_history: list[dict[str, str]],
        max_tokens: int | None = None,
    ) -> str:
        """
        Answer a follow-up question based on conversation history.

        Args:
            question: User's question
            conversation_history: Previous messages
            max_tokens: Maximum tokens in response (None = no limit)

        Returns:
            Answer text
        """
        system_prompt = get_prompt("system_followup")

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": question})

        try:
            # Build request params
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": DEFAULT_GROQ_TEMPERATURE,
            }

            # Only add max_tokens if specified
            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)

            answer = response.choices[0].message.content
            if answer:
                return answer.strip()
            return ""

        except Exception as e:
            logger.error("Error answering question: %s", e)
            raise

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = DEFAULT_GROQ_TEMPERATURE,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a response using the LLM.

        Generic generation method for simple prompts (e.g., topic extraction).

        Args:
            prompt: User prompt text
            system_prompt: Optional system prompt (default: basic assistant)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (None = no limit)

        Returns:
            Generated text
        """
        default_system_prompt = (
            "You are a helpful assistant. Follow instructions precisely."
        )

        try:
            # Build request params
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt or default_system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
            }

            # Only add max_tokens if specified
            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)

            result = response.choices[0].message.content
            if result:
                return result.strip()
            return ""

        except Exception as e:
            logger.error("Error generating response: %s", e)
            raise
