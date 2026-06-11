"""Followup agent - generates related questions with brief answers."""

import logging
import re

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..state import GraphState

logger = logging.getLogger(__name__)


def parse_followup_format(text: str) -> list[dict[str, str]]:
    """
    Parse LLM output into structured followup questions.

    Expected format:
    Q: [question]
    A: [brief answer]

    Returns:
        List of {question, brief_answer} dicts
    """
    followups = []

    # Split by Q: markers
    questions = re.split(r"\nQ:", text)

    for q_block in questions[1:]:  # Skip first (before first Q:)
        # Split into question and answer
        parts = re.split(r"\nA:", q_block, maxsplit=1)

        if len(parts) == 2:
            question = parts[0].strip()
            answer = parts[1].strip()

            # Clean up
            question = question.strip('"').strip("'").strip()
            answer = answer.strip('"').strip("'").strip()

            # Remove leading numbers like "1. " or "1) "
            question = re.sub(r"^\d+[\.)]\s*", "", question)

            followups.append({"question": question, "brief_answer": answer})

    return followups[:3]  # Max 3 followups


async def generate_followups(state: GraphState, config: dict) -> GraphState:
    """
    Generate 2-3 related follow-up questions with brief preview answers.

    Runs AFTER main answer is delivered (non-blocking in graph).

    Args:
        state: Current graph state with answer
        config: Runtime configuration

    Returns:
        Updated state with followup_questions
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info("Generating follow-up questions...")

    # Use Llama 3.1 8B for efficiency
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.4,
    )

    # Truncate answer for context
    answer_preview = (
        state["answer"][:800] + "..."
        if len(state["answer"]) > 800
        else state["answer"]
    )

    prompt = f"""Based on this Q&A, suggest 2-3 natural follow-up questions:

Original question: {state['question']}
Answer summary: {answer_preview}

For each follow-up:
1. Make it specific and actionable
2. Something a curious user might naturally ask next
3. Provide a 1-2 sentence preview answer (brief!)

Format exactly like this:
Q: [Follow-up question 1]
A: [Brief 1-2 sentence answer]

Q: [Follow-up question 2]
A: [Brief 1-2 sentence answer]

Generate 2-3 follow-ups:"""

    try:
        response = await llm.ainvoke(prompt)

        # Parse the response
        followups = parse_followup_format(response.content)

        logger.info(f"Generated {len(followups)} follow-up questions")

        return {
            **state,
            "followup_questions": followups,
        }

    except Exception as e:
        logger.error(f"Follow-up generation failed: {e}")
        return {
            **state,
            "followup_questions": [],
        }
