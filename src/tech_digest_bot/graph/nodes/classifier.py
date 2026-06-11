"""Question classifier node - categorizes questions as simple/complex/contested."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..schemas import Classification
from ..state import GraphState

logger = logging.getLogger(__name__)


async def classify_question(state: GraphState, config: dict) -> GraphState:
    """
    Classify question as simple/complex/contested using Llama 3.1 8B.

    Args:
        state: Current graph state
        config: Runtime configuration (includes settings)

    Returns:
        Updated state with question_type set
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Classifying question: {state['question'][:100]}...")

    # Initialize Llama 3.1 8B for fast classification
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.1,  # Low temperature for deterministic classification
    )

    # Use structured output
    structured_llm = llm.with_structured_output(Classification)

    prompt = f"""Classify this question into one of three categories:

Question: {state['question']}

Categories:
- simple: Factual, straightforward questions with clear answers
  Examples: "What is React?", "Who created Python?", "When was Rust released?"

- complex: Multi-faceted questions requiring research across multiple aspects
  Examples: "Compare React, Vue, and Angular", "Explain microservices architecture"

- contested: Questions involving trade-offs, opinions, or context-dependent answers
  Examples: "Should I use microservices?", "Is TypeScript better than JavaScript?"
  "Which framework is best for my project?"

Classify the question and explain your reasoning briefly.
"""

    try:
        result = await structured_llm.ainvoke(prompt)

        logger.info(
            f"Classified as: {result.question_type} - {result.reasoning}"
        )

        return {
            **state,
            "question_type": result.question_type,
        }

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        # Default to complex on error
        return {
            **state,
            "question_type": "complex",
        }


async def fast_path_simple(state: GraphState, config: dict) -> GraphState:
    """
    Fast path for simple questions - single search + single LLM call.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        Updated state with answer and search results
    """
    from ...config.settings import Settings
    from ...search import DuckDuckGoSearch

    settings: Settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Fast path for simple question: {state['question'][:100]}...")

    try:
        # Single DuckDuckGo search
        ddg = DuckDuckGoSearch()
        results = await ddg.search(state["question"], max_results=5)

        if not results:
            logger.warning("No search results found")
            return {
                **state,
                "search_results": [],
                "answer": "I couldn't find information about this topic.",
                "citations": [],
            }

        # Format context
        context = "\n\n".join(
            [
                f"[{i+1}] {r['title']}\nURL: {r['url']}\n{r['content']}"
                for i, r in enumerate(results)
            ]
        )

        # Generate answer with Llama 3.3 70B
        llm = ChatOpenAI(
            model="llama-3.3-70b-versatile",
            base_url=DEFAULT_GROQ_URL,
            api_key=settings.groq_api_key,
            temperature=0.3,
        )

        prompt = f"""Answer this question using the provided sources:

Question: {state['question']}

Sources:
{context}

FORMATTING REQUIREMENTS:
1. Start with a ## Header matching the question topic (e.g., "## What is Python?")
   - DO NOT use "Introduction" or generic headers
2. Lead with 2-3 bullet points summarizing key points
3. Use ### for any subsections if needed
4. Use bullet points (-) for lists or multiple items
5. Use **bold** for key terms
6. Cite sources using [1], [2] notation inline

Provide a clear, well-formatted answer:
"""

        response = await llm.ainvoke(prompt)

        # Extract citations
        citations = [r["url"] for r in results]

        logger.info("Fast path answer generated")

        return {
            **state,
            "search_results": [
                {
                    "url": r["url"],
                    "title": r["title"],
                    "content": r["content"],
                    "sub_question": None,
                }
                for r in results
            ],
            "answer": response.content,
            "citations": citations,
        }

    except Exception as e:
        logger.error(f"Fast path failed: {e}")
        return {
            **state,
            "search_results": [],
            "answer": f"Error processing question: {str(e)}",
            "citations": [],
        }
