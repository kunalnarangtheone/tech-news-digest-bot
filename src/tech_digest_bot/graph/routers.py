"""Router functions for conditional edges in the graph."""

import logging

from langgraph.graph import Send

from .state import GraphState

logger = logging.getLogger(__name__)


def route_by_question_type(state: GraphState) -> str:
    """
    Route based on classifier output.

    Args:
        state: Current graph state with question_type set

    Returns:
        "fast_path" for simple questions, "planner" for complex/contested
    """
    if state["question_type"] == "simple":
        logger.info("→ Routing to fast_path (simple question)")
        return "fast_path"
    else:
        logger.info(
            f"→ Routing to planner ({state['question_type']} question)"
        )
        return "planner"


def dispatch_search_agents(state: GraphState) -> list[Send]:
    """
    Fan out to parallel search agents using Send().

    Each Send() invokes 'search_agents' node with a subset of state
    containing just the sub-question.

    On RETRY: Uses gap-specific queries instead of original sub-questions.

    Args:
        state: Current graph state with sub_questions or _gap_queries

    Returns:
        List of Send() commands for parallel execution
    """
    # Check if this is a retry (gap queries present)
    if "_gap_queries" in state and state["_gap_queries"]:
        queries = state["_gap_queries"]
        logger.info(
            f"→ Dispatching {len(queries)} gap-specific search agents (RETRY)"
        )
    else:
        queries = state["sub_questions"]
        logger.info(
            f"→ Dispatching {len(queries)} search agents for sub-questions"
        )

    # Fan out: one Send() per query
    return [Send("search_agents", {"sub_question": q}) for q in queries]


def route_contested(state: GraphState) -> str | list[Send]:
    """
    Route to adversarial layer if contested flag is set.

    For contested questions, uses Send() to trigger BOTH advocates in parallel.

    Args:
        state: Current graph state with contested flag

    Returns:
        List of Send() for parallel advocates if contested, "standard" otherwise
    """
    if state.get("contested", False):
        logger.info("→ Routing to adversarial advocates (contested question)")
        # Send both advocates in parallel - they'll both feed into judge
        return [
            Send("advocate_a", state),
            Send("advocate_b", state),
        ]
    else:
        logger.info("→ Routing to standard synthesizer")
        return "standard"


def decide_retry(state: GraphState, config: dict) -> str:
    """
    Autonomous retry decision based on critic evaluation.

    THIS IS THE KEY AUTONOMOUS FEATURE - the critic's decision to retry
    happens without user intervention.

    Args:
        state: Current graph state with _gap_queries from critic
        config: Runtime configuration (includes max_retries)

    Returns:
        "retry" to re-dispatch search agents, "done" to proceed to followup
    """
    max_retries = config.get("max_retries", 2)

    # Check if critic flagged for retry AND under retry limit
    has_gap_queries = bool(state.get("_gap_queries"))
    under_retry_limit = state["retry_count"] < max_retries

    if has_gap_queries and under_retry_limit:
        logger.warning(
            f"🔄 Critic RETRY triggered: {state['retry_count'] + 1}/{max_retries} "
            f"(confidence: {state['confidence_score']:.2f})"
        )
        return "retry"
    else:
        if not has_gap_queries:
            logger.info(
                f"✓ Critic PASSED (confidence: {state['confidence_score']:.2f})"
            )
        else:
            logger.warning(
                f"⚠ Max retries reached ({max_retries}) - proceeding with "
                f"confidence: {state['confidence_score']:.2f}"
            )
        return "done"
