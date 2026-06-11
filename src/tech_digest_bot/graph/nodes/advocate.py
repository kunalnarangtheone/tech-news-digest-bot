"""Advocate nodes - argue pro/con positions for contested questions."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..state import GraphState
from .synthesizer import format_search_context

logger = logging.getLogger(__name__)


async def advocate_pro(state: GraphState, config: dict) -> GraphState:
    """
    Argue PRO position for contested question.

    Uses Llama 3.3 70B to build strongest case from available sources.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        Updated state with advocate_a_position
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Advocate PRO building case for: {state['question'][:100]}...")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.5,  # Slightly higher for persuasive writing
    )

    context = format_search_context(state["search_results"])

    prompt = f"""You are advocating FOR this position: {state['question']}

Available evidence:
{context}

FORMATTING REQUIREMENTS:
1. Use ### for section headers (e.g., "### Key Arguments For")
2. Use bullet points (-) to list arguments and evidence
3. Use **bold** for key terms and important points
4. Cite sources using [1], [2] notation inline
5. Keep structure clear and scannable

YOUR ADVOCACY TASK:
1. Build the STRONGEST case you can for the PRO position
2. Use specific evidence from the sources
3. Acknowledge the strongest pro arguments
4. Be persuasive but honest - don't invent claims

Present your advocacy:"""

    try:
        response = await llm.ainvoke(prompt)

        logger.info("PRO advocacy position generated")

        return {
            **state,
            "advocate_a_position": response.content,
        }

    except Exception as e:
        logger.error(f"PRO advocate failed: {e}")
        return {
            **state,
            "advocate_a_position": f"Error generating PRO position: {str(e)}",
        }


async def advocate_con(state: GraphState, config: dict) -> GraphState:
    """
    Argue CON position for contested question.

    Uses Llama 3.3 70B to build strongest opposing case.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        Updated state with advocate_b_position
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Advocate CON building case for: {state['question'][:100]}...")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.5,
    )

    context = format_search_context(state["search_results"])

    prompt = f"""You are advocating AGAINST this position: {state['question']}

Available evidence:
{context}

FORMATTING REQUIREMENTS:
1. Use ### for section headers (e.g., "### Key Concerns Against")
2. Use bullet points (-) to list counter-arguments and risks
3. Use **bold** for key terms and important warnings
4. Cite sources using [1], [2] notation inline
5. Keep structure clear and scannable

YOUR ADVOCACY TASK:
1. Build the STRONGEST case you can for the CON/opposing position
2. Use specific evidence from the sources
3. Acknowledge the strongest con arguments and drawbacks
4. Be persuasive but honest - don't invent claims

Present your advocacy:"""

    try:
        response = await llm.ainvoke(prompt)

        logger.info("CON advocacy position generated")

        return {
            **state,
            "advocate_b_position": response.content,
        }

    except Exception as e:
        logger.error(f"CON advocate failed: {e}")
        return {
            **state,
            "advocate_b_position": f"Error generating CON position: {str(e)}",
        }
