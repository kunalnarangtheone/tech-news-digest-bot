"""Judge node - synthesizes nuanced answer from adversarial positions."""

import logging

from langchain_openai import ChatOpenAI

from ...config.constants import DEFAULT_GROQ_URL
from ..state import GraphState
from .synthesizer import extract_citations

logger = logging.getLogger(__name__)


async def judge_synthesis(state: GraphState, config: dict) -> GraphState:
    """
    Synthesize balanced answer from PRO and CON advocacy positions.

    The judge explicitly surfaces genuine disagreement rather than
    producing false consensus.

    Args:
        state: Current graph state with both advocate positions
        config: Runtime configuration

    Returns:
        Updated state with answer and debate_flag set to True
    """
    settings = config.get("configurable", {}).get("settings")
    if not settings:
        raise ValueError("Settings not found in config")

    logger.info(f"Judge synthesizing from debate: {state['question'][:100]}...")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        base_url=DEFAULT_GROQ_URL,
        api_key=settings.groq_api_key,
        temperature=0.4,
    )

    prompt = f"""Two advocates debated this question: {state['question']}

PRO Position:
{state['advocate_a_position']}

CON Position:
{state['advocate_b_position']}

FORMATTING REQUIREMENTS - STRICTLY FOLLOW THIS STRUCTURE:
1. Start directly with a ## Header matching the question topic (e.g., "## Should You Use React or Vue?")
   - DO NOT use generic section names like "Introduction", "Overview", "Synthesis"
   - Use the exact topic from the question
2. Lead with 2-4 bullet points summarizing key perspectives from the debate
3. Use ### for subsections to organize different viewpoints
4. Use bullet points (-) for listing arguments, trade-offs, or context-dependent factors
5. Use **bold** for key terms, important concepts, and emphasis
6. Use *italics* for caveats or nuanced distinctions
7. Maintain all source citations using [1], [2] notation
8. Include relevant emojis sparingly in subsection headers (e.g., ⚖️ 💡 🎯)

EXAMPLE STRUCTURE:
## [Topic from Question]
- Key perspective 1 from debate
- Key perspective 2 from debate
- Key contextual factor

### PRO Perspective ⚖️
- Argument 1 with **key benefit** [1]
- Argument 2

### CON Perspective ⚖️
- Counter-argument 1 with **key concern** [2]
- Counter-argument 2

### When Each Makes Sense 🎯
- Use approach A when **context X**
- Use approach B when **context Y**

CONTENT REQUIREMENTS:
1. Synthesize a BALANCED answer that acknowledges genuine disagreement
2. Present both perspectives fairly
3. Identify when trade-offs are context-dependent
4. DO NOT force false consensus - if experts genuinely disagree, say so
5. Help the reader understand WHEN each position makes sense

Provide a nuanced synthesis:"""

    try:
        response = await llm.ainvoke(prompt)

        # Extract citations from search results
        citations = extract_citations(state["search_results"])

        logger.info("Judge synthesis completed - debate acknowledged")

        return {
            **state,
            "answer": response.content,
            "citations": citations,
            "debate_flag": True,  # Mark that adversarial synthesis was used
        }

    except Exception as e:
        logger.error(f"Judge synthesis failed: {e}")
        return {
            **state,
            "answer": f"Error synthesizing from debate: {str(e)}",
            "citations": [],
            "debate_flag": True,
        }
