"""Main StateGraph construction for multi-agent Q&A system."""

import logging

from langgraph.graph import END, StateGraph

from .nodes import (
    advocate_con,
    advocate_pro,
    classify_question,
    critic_evaluation,
    fast_path_simple,
    generate_followups,
    judge_synthesis,
    plan_research,
    search_agent,
    synthesize_answer,
)
from .routers import (
    decide_retry,
    dispatch_search_agents,
    route_by_question_type,
    route_contested,
)
from .state import GraphState

logger = logging.getLogger(__name__)


def create_qa_graph():
    """
    Build the complete Q&A StateGraph with all nodes and edges.

    Graph topology:
    1. Entry → classifier
    2. Classifier → fast_path (simple) OR planner (complex/contested)
    3. Fast_path → critic
    4. Planner → parallel search_agents (via Send())
    5. Search_agents → contested router
    6. Contested router → synthesizer (standard) OR advocates (contested)
    7. Synthesizer → critic
    8. Advocates → judge → critic
    9. Critic → retry loop (back to search_agents) OR done → followup
    10. Followup → END

    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building Q&A StateGraph...")

    # Initialize graph
    graph = StateGraph(GraphState)

    # Add all nodes
    graph.add_node("classifier", classify_question)
    graph.add_node("fast_path", fast_path_simple)
    graph.add_node("planner", plan_research)
    graph.add_node("search_agents", search_agent)  # Parallelizable via Send()
    graph.add_node("synthesizer", synthesize_answer)
    graph.add_node("advocate_a", advocate_pro)
    graph.add_node("advocate_b", advocate_con)
    graph.add_node("judge", judge_synthesis)
    graph.add_node("critic", critic_evaluation)
    graph.add_node("followup", generate_followups)

    # Entry point
    graph.set_entry_point("classifier")

    # Classifier routing: simple → fast_path, complex/contested → planner
    graph.add_conditional_edges(
        "classifier",
        route_by_question_type,
        {
            "fast_path": "fast_path",
            "planner": "planner",
        },
    )

    # Fast path goes directly to critic
    graph.add_edge("fast_path", "critic")

    # Planner → parallel search agents (via Send())
    # This is a conditional edge that returns Send() commands
    graph.add_conditional_edges(
        "planner",
        dispatch_search_agents,
        # No path map needed - Send() handles routing to 'search_agents' node
    )

    # After all search agents complete → contested router
    # Router returns Send() list for contested (parallel advocates) or string for standard
    graph.add_conditional_edges(
        "search_agents",
        route_contested,
        {
            "standard": "synthesizer",
            # No explicit edge needed for advocates - Send() handles routing
        },
    )

    # Standard path: synthesizer → critic
    graph.add_edge("synthesizer", "critic")

    # Adversarial path: both advocates (triggered via Send() in router) → judge
    # The graph waits for BOTH advocates to complete before running judge
    graph.add_edge("advocate_a", "judge")
    graph.add_edge("advocate_b", "judge")
    graph.add_edge("judge", "critic")

    # THE KEY FEATURE: Critic retry loop
    # Critic evaluates answer and autonomously decides to retry or proceed
    # retry_count is incremented in the critic node when retry is triggered
    graph.add_conditional_edges(
        "critic",
        decide_retry,
        {
            "retry": "search_agents",  # Loop back to re-search with gap queries
            "done": "followup",  # Proceed to followup generation
        },
    )

    # Followup → END
    graph.add_edge("followup", END)

    logger.info("Q&A StateGraph built successfully")

    return graph.compile()
