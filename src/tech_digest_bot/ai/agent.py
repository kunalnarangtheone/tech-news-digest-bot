"""LangChain agent for intelligent tech research."""

import logging
from typing import TYPE_CHECKING

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config.constants import (
    AGENT_TEMPERATURE,
    DEFAULT_GROQ_URL,
)

if TYPE_CHECKING:
    from ..config.settings import Settings

logger = logging.getLogger(__name__)


class TechIntelligenceAgent:
    """
    LangChain agent for intelligent tech research.

    Uses web search tool for finding current information.
    """

    def __init__(
        self,
        settings: Settings,
        llm_client,
    ):
        """
        Initialize the Tech Intelligence Agent.

        Args:
            settings: Settings object for configuration
            llm_client: LLM client
        """
        self.settings = settings
        self.llm_client = llm_client

        # Initialize Groq LLM for agent reasoning
        logger.info(
            f"Initializing LangChain agent with Groq model: {settings.groq_model}"
        )

        self.llm = ChatOpenAI(
            model=settings.groq_model,
            base_url=DEFAULT_GROQ_URL,
            api_key=settings.groq_api_key,
            temperature=AGENT_TEMPERATURE,
        )

        # Create tools
        self.tools = self._create_tools()

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        logger.info(
            f"✓ Tech Intelligence Agent initialized with "
            f"{len(self.tools)} tools"
        )

    def _create_tools(self):
        """Create LangChain tools for the agent."""
        from ..config.settings import Settings
        from .tools import WebSearchTool

        # Rebuild models to resolve forward references
        WebSearchTool.model_rebuild(_types_namespace={
            'Settings': Settings,
        })

        tools = [
            WebSearchTool(
                settings=self.settings,
                llm_client=self.llm_client,
            ),
        ]

        logger.info("Created tools:")
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description[:60]}...")

        return tools

    def _create_system_prompt(self) -> str:
        """Create system prompt for agent."""
        return """You are a tech research assistant with web search capabilities.

**Available Tools:**
1. search_web - Search the web for current information

**CRITICAL FORMATTING REQUIREMENTS - STRICTLY FOLLOW:**
1. Start directly with a ## Header matching the question topic (e.g., "## Latest AI Developments in 2026")
   - DO NOT use generic section names like "Introduction", "Overview", or "Summary"
   - Use the exact topic from the question
2. Lead with 2-4 bullet points summarizing key findings immediately after the header
3. Use ### for subsections to organize information by theme/category
4. Use bullet points (-) for lists, features, developments, or multiple items
5. Use **bold** for key terms, important names, and emphasis
6. Use *italics* for new concepts being introduced
7. Include relevant emojis sparingly in subsection headers (e.g., 🚀 💡 ⚡)
8. Always cite sources using [source name](URL) inline

**EXAMPLE STRUCTURE:**
## Latest AI Developments in 2026
- Key development 1
- Key development 2
- Key development 3

### Recent Breakthroughs 🚀
- Development 1 with **key detail** from [Source](url)
- Development 2

### Industry Impact 💡
Brief explanation with **key terms** emphasized...

**CONTENT REQUIREMENTS:**
- Synthesize information from search results comprehensively
- Be thorough and cover all important aspects
- Always cite sources with clickable links
- Provide detailed, complete answers that fully address the query"""

    async def research(self, query: str) -> dict:
        """
        Research a topic using web search.

        Args:
            query: User's question or topic to research

        Returns:
            Dict with 'output' (final answer) and 'intermediate_steps'
        """
        try:
            logger.info(f"Agent researching: {query}")

            # Create prompt
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self._create_system_prompt()),
                    ("human", "{input}"),
                ]
            )

            intermediate_steps = []

            # Search web
            logger.info("Searching web...")
            web_search = self.tools[0]  # search_web
            web_result = await web_search.ainvoke({"query": query})
            intermediate_steps.append(
                (
                    type(
                        "Action",
                        (),
                        {
                            "tool": "search_web",
                            "tool_input": query,
                        },
                    ),
                    web_result,
                )
            )

            # Synthesize answer using LLM
            logger.info("Synthesizing answer...")
            synthesis_prompt = f"""Based on the following search results, \
provide a comprehensive answer to the question: "{query}"

Search Results:
{web_result}

Provide a thorough, well-structured answer with:
- Clear overview
- Detailed coverage of all key points
- Relevant context and background
- Specific examples or details where available
- Relevant URLs as references

Be comprehensive - cover all important aspects fully."""

            chain = prompt | self.llm
            result = await chain.ainvoke({"input": synthesis_prompt})

            final_answer = result.content

            logger.info("Agent research completed successfully")
            return {
                "output": final_answer,
                "intermediate_steps": intermediate_steps,
            }

        except Exception as e:
            logger.exception(f"Agent research failed: {e}")

            # Fallback: try direct web search
            logger.warning("Falling back to direct web search")
            from .tools import WebSearchTool

            web_search = WebSearchTool(
                settings=self.settings,
                llm_client=self.llm_client,
            )
            fallback_result = await web_search.ainvoke({"query": query})

            return {
                "output": fallback_result,
                "intermediate_steps": [],
            }

    def _is_raw_search_results(self, content: str) -> bool:
        """
        Detect if content is raw search results vs synthesized answer.

        Raw results have patterns like:
        - "Found X articles and added to knowledge graph"
        - "**1. Title**\nURL: https://..."
        - Multiple "URL:" and "Content:" entries

        Args:
            content: Response content to check

        Returns:
            True if raw search results, False if synthesized answer
        """
        # Check for raw search result patterns
        raw_indicators = [
            "Found" in content and "articles and added to knowledge graph" in content,
            content.count("URL:") >= 3,  # Multiple article URLs
            content.count("**") >= 4,  # Multiple markdown headers for articles
            "Content:" in content and content.count("Content:") >= 2,
        ]

        return any(raw_indicators)

    def _extract_context_from_history(
        self, conversation_history: list[dict[str, str]]
    ) -> str:
        """
        Extract relevant context from conversation history.

        Intelligently handles:
        - Raw search results: Extract only summary
        - Synthesized answers: Keep in full (up to reasonable limit)
        - User messages: Keep in full

        Args:
            conversation_history: Previous conversation messages

        Returns:
            Formatted context string
        """
        history_items = []

        for msg in conversation_history[-4:]:
            content = msg['content']

            if msg['role'] == 'assistant':
                # Detect if this is raw search results
                if self._is_raw_search_results(content):
                    # Extract just the summary line
                    first_line = content.split('\n')[0]
                    history_items.append(
                        f"assistant: {first_line}\n"
                        "[Detailed search results omitted for brevity]"
                    )
                else:
                    # It's a synthesized answer - keep it but with reasonable limit
                    if len(content) > 1000:
                        # Very long synthesized answer - keep first part
                        content = content[:1000] + "\n[Answer truncated for context]"
                    history_items.append(f"assistant: {content}")
            else:
                # User message - always keep in full
                history_items.append(f"user: {content}")

        return "\n\n".join(history_items)

    async def answer_followup(
        self, question: str, conversation_history: list[dict[str, str]]
    ) -> dict:
        """
        Answer a follow-up question with conversation context.

        Args:
            question: Follow-up question
            conversation_history: Previous messages

        Returns:
            Dict with 'output' (answer) and 'intermediate_steps'
        """
        # Extract intelligent context from history
        history_context = self._extract_context_from_history(
            conversation_history
        )

        full_query = f"""Based on this conversation:

{history_context}

Follow-up question: {question}"""

        return await self.research(full_query)

    def get_tool_names(self) -> list[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]

    def get_tool_descriptions(self) -> dict[str, str]:
        """Get tool names and descriptions."""
        return {tool.name: tool.description for tool in self.tools}
