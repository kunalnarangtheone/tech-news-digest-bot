"""Pydantic schemas for structured LLM outputs in graph nodes."""

from typing import Literal

from pydantic import BaseModel, Field


class Classification(BaseModel):
    """Question classification output."""

    question_type: Literal["simple", "complex", "contested"]
    reasoning: str = Field(description="Brief explanation of classification")


class SubQuestions(BaseModel):
    """Planner output with sub-questions."""

    sub_questions: list[str] = Field(
        min_length=2, max_length=5, description="3-5 focused sub-questions"
    )
    contested: bool = Field(
        description="Whether question involves trade-offs or opinions"
    )
    reasoning: str = Field(description="Why these sub-questions were chosen")


class SourceChunk(BaseModel):
    """Search result with metadata."""

    url: str
    title: str
    content: str
    relevance_score: float = Field(
        ge=0.0, le=1.0, default=0.5, description="Relevance to query"
    )
    sub_question: str | None = Field(
        default=None, description="Which sub-question this answers"
    )


class CriticEvaluation(BaseModel):
    """Critic quality assessment."""

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Objective confidence based on source corroboration",
    )
    source_corroboration_count: int = Field(
        ge=0, description="Number of independent sources agreeing"
    )
    inter_source_agreement: bool = Field(
        description="Whether sources agree (no contradictions)"
    )
    should_retry: bool = Field(description="Whether to trigger re-search")
    gap_specific_queries: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Specific queries to fill gaps (if retry needed)",
    )
    reasoning: str = Field(description="Explanation of evaluation")


class FollowupQuestion(BaseModel):
    """A single follow-up question with brief answer."""

    question: str = Field(description="Natural follow-up question")
    brief_answer: str = Field(
        max_length=200, description="1-2 sentence preview answer"
    )
