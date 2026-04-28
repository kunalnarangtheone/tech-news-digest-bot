"""LangChain agent for intelligent tech research."""

import logging
from typing import TYPE_CHECKING

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from ..config.constants import (
    AGENT_NUM_CTX,
    AGENT_TEMPERATURE,
    AGENT_ANSWER_MIN_WORDS,
    AGENT_ANSWER_MAX_WORDS,
)

if TYPE_CHECKING:
    from ..graph.neo4j_store import TechDigestNeo4jStore
    from ..config.settings import Settings

logger = logging.getLogger(__name__)


class TechIntelligenceAgent:
    """
    LangChain agent for intelligent tech research.

    Uses tool-calling with intelligent routing to decide which tools to use:
    - search_knowledge_graph: For previously indexed content
    - search_web_and_ingest: For breaking news and new topics
    - explore_graph_relationships: For topic discovery
    """

    def __init__(
        self,
        neo4j_store: "TechDigestNeo4jStore",
        settings: "Settings",
        llm_client,
    ):
        """
        Initialize the Tech Intelligence Agent.

        Args:
            neo4j_store: Neo4j store instance with BM25 search
            settings: Settings object for configuration
            llm_client: LLM client for topic extraction
        """
        self.neo4j_store = neo4j_store
        self.settings = settings
        self.llm_client = llm_client

        # Initialize Ollama LLM for agent reasoning
        logger.info(
            f"Initializing LangChain agent with model: "
            f"{settings.ollama_model}"
        )

        self.llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url.replace("/v1", ""),
            temperature=AGENT_TEMPERATURE,
            num_ctx=AGENT_NUM_CTX,
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
        from .tools import (
            GraphSearchTool,
            WebSearchTool,
            GraphExploreTool,
        )
        from ..graph.neo4j_store import TechDigestNeo4jStore
        from ..config.settings import Settings

        # Rebuild models to resolve forward references
        GraphSearchTool.model_rebuild()
        WebSearchTool.model_rebuild(_types_namespace={
            'TechDigestNeo4jStore': TechDigestNeo4jStore,
            'Settings': Settings,
        })
        GraphExploreTool.model_rebuild()

        tools = [
            GraphSearchTool(neo4j_store=self.neo4j_store),
            WebSearchTool(
                neo4j_store=self.neo4j_store,
                settings=self.settings,
                llm_client=self.llm_client,
            ),
            GraphExploreTool(neo4j_store=self.neo4j_store),
        ]

        logger.info("Created tools:")
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description[:60]}...")

        return tools

    def _create_system_prompt(self) -> str:
        """Create system prompt for agent."""
        return """You are a tech research assistant with access to a \
knowledge graph and web search.

**Available Tools:**
1. search_knowledge_graph - Search previously indexed articles
2. search_web_and_ingest - Search web and add to knowledge graph
3. explore_graph_relationships - Explore topic connections

**Tool Selection Strategy:**
- Start with search_knowledge_graph (fast)
- If no results, use search_web_and_ingest
- Use explore_graph_relationships for "what's related" questions

**Response Format:**
- Synthesize information from tool results
- Include URLs as references
- Keep answers concise ({AGENT_ANSWER_MIN_WORDS}-{AGENT_ANSWER_MAX_WORDS} words)
- Use markdown formatting
- Always cite sources"""

    async def research(self, query: str) -> dict:
        """
        Research a topic using intelligent tool routing.

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

            # Strategy: Try graph search first, then web if needed
            intermediate_steps = []

            # Step 1: Try knowledge graph search
            logger.info("Step 1: Searching knowledge graph...")
            graph_search = self.tools[0]  # search_knowledge_graph
            graph_result = await graph_search.ainvoke({"query": query})
            intermediate_steps.append(
                (
                    type(
                        "Action",
                        (),
                        {
                            "tool": "search_knowledge_graph",
                            "tool_input": query,
                        },
                    ),
                    graph_result,
                )
            )

            # Check if graph search found results
            if "No relevant articles found" in graph_result:
                # Step 2: Search web and ingest
                logger.info(
                    "Step 2: No graph results, searching web..."
                )
                web_search = self.tools[1]  # search_web_and_ingest
                web_result = await web_search.ainvoke({"query": query})
                intermediate_steps.append(
                    (
                        type(
                            "Action",
                            (),
                            {
                                "tool": "search_web_and_ingest",
                                "tool_input": query,
                            },
                        ),
                        web_result,
                    )
                )

                # Use web result for synthesis
                context = web_result
            else:
                # Use graph result for synthesis
                context = graph_result

            # Step 3: Synthesize answer using LLM
            logger.info("Step 3: Synthesizing answer...")
            synthesis_prompt = f"""Based on the following research results, \
provide a comprehensive answer to the question: "{query}"

Research Results:
{context}

Provide a well-structured answer ({AGENT_ANSWER_MIN_WORDS}-{AGENT_ANSWER_MAX_WORDS} words) with:
- Brief overview (1-2 sentences)
- Key points in bullet format
- Relevant URLs as references
- Use markdown formatting"""

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
                neo4j_store=self.neo4j_store,
                settings=self.settings,
                llm_client=self.llm_client,
            )
            fallback_result = await web_search.ainvoke({"query": query})

            return {
                "output": fallback_result,
                "intermediate_steps": [],
            }

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
        # Build context from history
        history_context = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-6:]
            ]
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
