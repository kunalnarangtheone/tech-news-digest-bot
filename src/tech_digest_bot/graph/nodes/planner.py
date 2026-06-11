"""Planner node - decomposes complex questions into sub-questions."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..schemas import SubQuestions
from ..state import GraphState

logger = logging.getLogger(__name__)


async def plan_research(state: GraphState, config: dict) -> GraphState:
    """
    Decompose complex/contested questions into 3-5 sub-questions.

    Also determines if the question is contested (involves trade-offs/opinions).

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        Updated state with sub_questions and contested flag
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Planning research for: {state['question'][:100]}...")

    # Use Llama 3.1 8B for planning
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.3,
    )

    structured_llm = llm.with_structured_output(SubQuestions)

    prompt = f"""Break down this question into 3-5 focused sub-questions for research:

Question: {state['question']}

Guidelines:
1. Each sub-question should be independently researchable
2. Together they should cover all aspects of the main question
3. Avoid overlapping sub-questions
4. Make them specific enough to search effectively

Also determine if this is a CONTESTED question:
- Contested = involves trade-offs, opinions, "best" practices, or context-dependent answers
- Examples: "Should I use X or Y?", "What's the best framework?", "Is X worth it?"
- Non-contested = factual comparisons, technical explanations
- Examples: "How does X work?", "What are the differences between X and Y?"

Return:
- sub_questions: List of 3-5 focused questions
- contested: Boolean flag
- reasoning: Brief explanation of your decomposition
"""

    try:
        result = await structured_llm.ainvoke(prompt)

        logger.info(
            f"Generated {len(result.sub_questions)} sub-questions. "
            f"Contested: {result.contested}"
        )
        logger.info(f"Reasoning: {result.reasoning}")

        return {
            **state,
            "sub_questions": result.sub_questions,
            "contested": result.contested,
        }

    except Exception as e:
        logger.error(f"Planning failed: {e}")
        # Fallback: use main question as single sub-question
        return {
            **state,
            "sub_questions": [state["question"]],
            "contested": False,
        }
