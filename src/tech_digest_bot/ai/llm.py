"""LLM client for generating digests."""

import logging
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client using Ollama for local inference."""

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        base_url: str = "http://localhost:11434/v1",
    ) -> None:
        """
        Initialize LLM client with Ollama.

        Args:
            model: Ollama model identifier (default: qwen2.5:7b)
            base_url: Ollama API base URL
        """
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # Ollama doesn't require a real API key
        )

    async def generate_digest(
        self,
        topic: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 800,
    ) -> str:
        """
        Generate a tech digest using the LLM.

        Args:
            topic: Topic to research
            context: Research context from search results
            system_prompt: Optional custom system prompt
            max_tokens: Maximum tokens in response

        Returns:
            Generated digest text
        """
        default_system_prompt = """You are a tech digest assistant.
Your job is to create concise, informative 2-minute digests.

Guidelines:
- Start with a brief overview (1-2 sentences)
- Cover the most important points in bullet format
- Include recent developments or trends if relevant
- Use clear, accessible language
- Aim for ~200-300 words (2-minute read)
- Format in markdown with emojis for visual appeal
- Add 2-3 source URLs at the end

Keep it engaging but accurate."""

        user_prompt = f"""Create a 2-minute digest about: {topic}

Based on these search results:

{context}

Generate a comprehensive yet concise digest."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt or default_system_prompt,
                    },
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )

            digest = response.choices[0].message.content
            if digest:
                return digest.strip()
            return ""

        except Exception as e:
            logger.error("Error generating digest: %s", e)
            raise

    async def answer_question(
        self,
        question: str,
        conversation_history: list[dict[str, str]],
        max_tokens: int = 500,
    ) -> str:
        """
        Answer a follow-up question based on conversation history.

        Args:
            question: User's question
            conversation_history: Previous messages
            max_tokens: Maximum tokens in response

        Returns:
            Answer text
        """
        system_prompt = """You are a helpful tech assistant.
Answer follow-up questions based on the previous digest.

Guidelines:
- Be concise but informative
- Reference the previous digest when relevant
- If you need more information, suggest what to search for
- Use markdown formatting with emojis
- Keep answers under 150 words unless more detail is needed"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": question})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content
            if answer:
                return answer.strip()
            return ""

        except Exception as e:
            logger.error("Error answering question: %s", e)
            raise
