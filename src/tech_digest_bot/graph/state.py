"""LangGraph state definition for multi-agent Q&A workflow."""

import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict


class GraphState(TypedDict):
    """LangGraph state for multi-agent Q&A workflow."""

    # Input
    question: str
    conversation_history: list[dict[str, str]]

    # Classification
    question_type: Literal["simple", "complex", "contested"] | None

    # Planning
    sub_questions: list[str]
    contested: bool  # Flag for adversarial routing

    # Search results (accumulated from parallel agents)
    search_results: Annotated[list[dict], operator.add]  # Append-only

    # Synthesis
    answer: str | None
    citations: list[str]

    # Critic evaluation
    confidence_score: float  # 0-1
    retry_count: int
    critic_feedback: str | None

    # Adversarial layer (contested only)
    advocate_a_position: str | None
    advocate_b_position: str | None
    judge_synthesis: str | None

    # Output metadata
    debate_flag: bool
    followup_questions: list[dict[str, str]]  # [{question, brief_answer}]

    # Internal (retry handling)
    _gap_queries: list[str]  # Gap-specific queries for critic retries
