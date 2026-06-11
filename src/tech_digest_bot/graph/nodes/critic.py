"""Critic node - evaluates answer quality and triggers autonomous retries."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..schemas import CriticEvaluation
from ..state import GraphState

logger = logging.getLogger(__name__)


def format_sources_summary(search_results: list[dict]) -> str:
    """Create concise summary of sources for critic evaluation."""
    if not search_results:
        return "No sources available."

    summary = []
    for i, result in enumerate(search_results[:10], 1):  # Top 10 sources
        summary.append(f"[{i}] {result['title']} ({result['url'][:50]}...)")

    return "\n".join(summary)


async def critic_evaluation(state: GraphState, config: dict) -> GraphState:
    """
    Evaluate answer quality using objective source corroboration signals.

    THIS IS THE KEY AUTONOMOUS FEATURE - decides whether to retry without
    user intervention.

    Uses:
    - Source corroboration count (how many independent sources agree)
    - Inter-source agreement (do sources contradict each other)

    Deliberately avoids self-reported LLM confidence scores (miscalibrated).

    Args:
        state: Current graph state with answer and search_results
        config: Runtime configuration (includes max_retries)

    Returns:
        Updated state with confidence score and optional gap queries
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    max_retries = config.get("max_retries", 2)

    logger.info(
        f"Critic evaluating answer (retry {state['retry_count']}/{max_retries})..."
    )

    # Use Llama 3.3 70B for quality evaluation
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.2,  # Low temperature for objective evaluation
    )

    structured_llm = llm.with_structured_output(CriticEvaluation)

    # Prepare sources summary
    sources_summary = format_sources_summary(state["search_results"])

    prompt = f"""Evaluate this answer objectively using source corroboration:

Question: {state['question']}

Answer:
{state['answer']}

Available sources ({len(state['search_results'])} total):
{sources_summary}

Your task:
1. Assess source corroboration:
   - How many INDEPENDENT sources corroborate key claims?
   - Independent = different websites, not just repeating same info
   - Count: 0-1 sources = very low, 2 sources = low, 3+ sources = adequate

2. Check inter-source agreement:
   - Do sources contradict each other on key points?
   - Are there conflicting claims that aren't addressed?

3. Identify gaps:
   - Are there claims in the answer that lack source support?
   - Are there obvious aspects of the question not covered?

Confidence threshold:
- High (≥0.8): 3+ corroborating sources AND no contradictions
- Medium (0.5-0.8): 2 sources OR minor gaps
- Low (<0.5): 1 source OR contradictions OR major gaps

Should retry if:
- Confidence < 0.6 AND retry_count < {max_retries}
- If retrying, provide 1-3 specific gap-filling queries

Provide your evaluation:"""

    try:
        evaluation = await structured_llm.ainvoke(prompt)

        # Decision: retry if confidence is low AND under retry limit
        should_retry = (
            evaluation.should_retry
            and state["retry_count"] < max_retries
            and evaluation.confidence_score < 0.6
        )

        if should_retry:
            logger.warning(
                f"🔄 Critic triggering retry {state['retry_count'] + 1}/{max_retries} "
                f"(confidence: {evaluation.confidence_score:.2f})"
            )
            logger.info(
                f"Gap queries: {evaluation.gap_specific_queries}"
            )
        else:
            logger.info(
                f"✓ Critic passed (confidence: {evaluation.confidence_score:.2f})"
            )

        return {
            **state,
            "confidence_score": evaluation.confidence_score,
            "critic_feedback": (
                f"Corroboration: {evaluation.source_corroboration_count} sources, "
                f"Agreement: {'Yes' if evaluation.inter_source_agreement else 'No'}"
            ),
            "_gap_queries": (
                evaluation.gap_specific_queries if should_retry else []
            ),
            # Increment retry_count if we're triggering a retry
            "retry_count": state["retry_count"] + (1 if should_retry else 0),
        }

    except Exception as e:
        logger.error(f"Critic evaluation failed: {e}")
        # On error, pass with low confidence (no retry to avoid loops)
        return {
            **state,
            "confidence_score": 0.5,
            "critic_feedback": f"Evaluation error: {str(e)}",
            "_gap_queries": [],
        }
