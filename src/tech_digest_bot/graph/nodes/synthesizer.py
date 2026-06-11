"""Synthesizer node - combines search results into coherent answer."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..state import GraphState

logger = logging.getLogger(__name__)


def format_search_context(search_results: list[dict]) -> str:
    """Format search results into context for synthesis."""
    if not search_results:
        return "No sources found."

    formatted = []
    for i, result in enumerate(search_results, 1):
        formatted.append(
            f"[{i}] {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Content: {result['content'][:1000]}..."  # Truncate long content
        )

    return "\n\n".join(formatted)


def extract_citations(search_results: list[dict]) -> list[str]:
    """Extract unique URLs as citations."""
    seen = set()
    citations = []

    for result in search_results:
        url = result["url"]
        if url not in seen:
            seen.add(url)
            citations.append(url)

    return citations


async def synthesize_answer(state: GraphState, config: dict) -> GraphState:
    """
    Synthesize comprehensive answer from search results (non-contested path).

    Uses Llama 3.3 70B for high-quality synthesis.

    Args:
        state: Current graph state with search_results populated
        config: Runtime configuration

    Returns:
        Updated state with answer and citations
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(
        f"Synthesizing answer from {len(state['search_results'])} sources..."
    )

    # Use Llama 3.3 70B for quality synthesis
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.3,
    )

    # Format context from search results
    context = format_search_context(state["search_results"])

    prompt = f"""Synthesize a comprehensive answer to this question using the provided sources:

Question: {state['question']}

Sources:
{context}

FORMATTING REQUIREMENTS - STRICTLY FOLLOW THIS STRUCTURE:
1. Start directly with a ## Header matching the question topic (e.g., "## What is AI?")
   - DO NOT use generic section names like "Introduction", "Overview", or "Summary"
   - Use the exact topic from the question
2. Lead with 2-4 bullet points summarizing key findings
3. Use ### for subsections to organize detailed information
4. Use bullet points (-) for lists, features, steps, or multiple items
5. Use **bold** for key terms, important concepts, and emphasis
6. Use *italics* for new concepts or terms being introduced
7. Cite sources using [1], [2] notation inline where you reference them
8. Include relevant emojis sparingly in subsection headers (e.g., 🚀 💡 ⚡)

EXAMPLE STRUCTURE:
## [Topic from Question]
- Key finding 1
- Key finding 2
- Key finding 3

### Recent Developments 🚀
- Development 1 with **important detail** [1]
- Development 2 [2]

### Why This Matters 💡
Brief explanation with **key terms** emphasized...

CONTENT REQUIREMENTS:
- Be accurate - only state what the sources support
- Cover all important aspects from the sources
- If sources are limited or contradict, acknowledge this
- Provide thorough, well-structured information

Answer:"""

    try:
        response = await llm.ainvoke(prompt)

        # Extract citations
        citations = extract_citations(state["search_results"])

        logger.info("Answer synthesized successfully")

        return {
            **state,
            "answer": response.content,
            "citations": citations,
        }

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return {
            **state,
            "answer": f"Error synthesizing answer: {str(e)}",
            "citations": [],
        }
