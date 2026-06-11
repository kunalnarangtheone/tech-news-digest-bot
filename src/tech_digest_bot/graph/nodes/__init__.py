"""Graph node implementations."""

from .advocate import advocate_con, advocate_pro
from .classifier import classify_question, fast_path_simple
from .critic import critic_evaluation
from .followup import generate_followups
from .judge import judge_synthesis
from .planner import plan_research
from .search_agent import search_agent
from .synthesizer import synthesize_answer

__all__ = [
    "classify_question",
    "fast_path_simple",
    "plan_research",
    "search_agent",
    "synthesize_answer",
    "advocate_pro",
    "advocate_con",
    "judge_synthesis",
    "critic_evaluation",
    "generate_followups",
]
