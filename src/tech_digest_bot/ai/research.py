"""Research service combining multiple search providers."""

import logging
from typing import TYPE_CHECKING

from ..config.settings import Settings
from ..search import DuckDuckGoSearch
from .llm import LLMClient

if TYPE_CHECKING:
    from .agent import TechIntelligenceAgent

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for answering tech questions using multiple sources."""

    def __init__(
        self,
        llm_client: LLMClient,
        use_agent: bool = True,
        settings: Settings | None = None,
    ) -> None:
        """
        Initialize research service.

        Args:
            llm_client: LLM client for generating answers
            use_agent: Whether to use LangChain agent (default: True)
            settings: Settings object for agent initialization
        """
        self.llm = llm_client
        self.ddg = DuckDuckGoSearch()

        # LangChain agent integration
        self.use_agent = use_agent
        self.settings = settings
        self.agent: TechIntelligenceAgent | None = None

        # LangGraph multi-agent Q&A system
        self.use_graph = settings.use_langgraph if settings else False
        self.qa_graph = None  # Lazy-init in initialize()

    async def initialize(self) -> None:
        """Initialize LangChain agent and LangGraph."""
        # Initialize LangChain agent
        if self.use_agent and self.settings:
            try:
                from .agent import TechIntelligenceAgent

                # Initialize LangChain agent
                logger.info("Initializing LangChain agent...")
                self.agent = TechIntelligenceAgent(
                    self.settings, self.llm
                )

                logger.info(
                    "✓ LangChain agent initialized successfully"
                )
            except Exception as e:
                logger.exception(
                    f"Failed to initialize LangChain agent: {e}"
                )
                self.use_agent = False
                self.agent = None

        # Initialize LangGraph multi-agent system
        if self.use_graph and self.settings:
            try:
                from ..graph import create_qa_graph

                logger.info("Initializing LangGraph Q&A system...")
                self.qa_graph = create_qa_graph()

                logger.info(
                    "✓ LangGraph Q&A system initialized successfully"
                )
            except Exception as e:
                logger.exception(
                    f"Failed to initialize LangGraph: {e}"
                )
                self.use_graph = False
                self.qa_graph = None

    async def research_topic(self, topic: str) -> str:
        """
        Research a tech topic and generate a comprehensive answer.

        Priority:
        1. LangGraph multi-agent system (if enabled) - autonomous quality control
        2. LangChain agent (if enabled) - intelligent tool selection
        3. Basic DuckDuckGo - fallback

        Args:
            topic: Topic or question to research

        Returns:
            Generated answer as markdown text
        """
        logger.info("Researching topic: %s", topic)

        # Try LangGraph multi-agent system first
        if self.use_graph and self.qa_graph:
            try:
                logger.info("Using LangGraph multi-agent Q&A system")
                result = await self.research_topic_with_graph(topic)
                return result["answer"]
            except Exception as e:
                logger.exception(
                    f"LangGraph system failed: {e}"
                )
                # Fall through to agent

        # Try LangChain agent second
        if self.use_agent and self.agent:
            try:
                logger.info("Using LangChain agent for research")
                result = await self.agent.research(topic)
                return result["output"]
            except Exception as e:
                logger.exception(
                    f"LangChain agent failed: {e}"
                )
                # Fall through to basic search

        # Fallback to basic DuckDuckGo
        return await self._research_basic(topic)

    async def _research_basic(self, topic: str) -> str:
        """
        Research using only DuckDuckGo web search.

        Args:
            topic: Topic or question to research

        Returns:
            Generated answer
        """
        # Search the web
        search_results = await self.ddg.search(topic, max_results=5)

        if not search_results:
            return (
                f"❌ Could not find information about '{topic}'. "
                "Please try a different topic or be more specific."
            )

        # Prepare context from search results
        context = "\n\n".join(
            [
                f"Source: {r['title']}\nURL: {r['url']}\n{r['content']}"
                for r in search_results
            ]
        )

        # Generate answer
        answer = await self.llm.generate_answer(topic, context)
        return answer

    async def answer_followup(
        self, question: str, conversation_history: list[dict[str, str]]
    ) -> str:
        """
        Answer a follow-up question.

        Priority:
        1. LangChain agent (if enabled) - context-aware
        2. Basic LLM - fallback

        Args:
            question: User's question
            conversation_history: Previous conversation messages

        Returns:
            Answer text
        """
        # Try LangChain agent first
        if self.use_agent and self.agent:
            try:
                logger.info("Using LangChain agent for follow-up")
                result = await self.agent.answer_followup(
                    question, conversation_history
                )
                return result["output"]
            except Exception as e:
                logger.exception(f"Agent follow-up failed: {e}")
                # Fall through to basic LLM

        # Fallback to basic LLM
        return await self.llm.answer_question(
            question, conversation_history
        )

    async def is_topic_change(
        self, new_message: str, recent_user_messages: list[str]
    ) -> bool:
        """
        Detect if the new message represents a topic change.

        Uses LLM to intelligently determine if the user is asking about
        a different topic or continuing the same conversation.

        Args:
            new_message: The new user message
            recent_user_messages: Recent user messages from history

        Returns:
            True if this is a new topic, False if it's a follow-up
        """
        if not recent_user_messages:
            return True

        # Create context of previous topics
        previous_context = "\n".join(
            [f"- {msg}" for msg in recent_user_messages]
        )

        # Use LLM to detect topic change
        prompt = f"""Analyze if the new question is about the same topic or a different topic.

Previous questions:
{previous_context}

New question:
{new_message}

Is this new question:
A) A follow-up/clarification about the same topic (e.g., "tell me more", "how does it compare", "what about X aspect")
B) A completely different topic

Respond with ONLY one word: "SAME" or "DIFFERENT"
"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.1,  # Low temperature for deterministic classification
                max_tokens=10,  # Only need one word
            )
            response = response.strip().upper()

            is_different = "DIFFERENT" in response
            logger.info(
                f"Topic change detection: {new_message[:50]}... -> "
                f"{'NEW TOPIC' if is_different else 'FOLLOW-UP'}"
            )
            return is_different

        except Exception as e:
            logger.exception(f"Topic detection failed: {e}")
            # On error, assume it's a new topic to be safe
            return True

    async def research_topic_with_graph(self, topic: str) -> dict:
        """
        Research using LangGraph autonomous multi-agent pipeline.

        Args:
            topic: Topic or question to research

        Returns:
            Dict with: answer, citations, confidence, debate_flag, followups
        """
        if not self.qa_graph or not self.settings:
            raise ValueError("LangGraph not initialized")

        logger.info(f"Starting LangGraph research: {topic[:100]}...")

        # Build initial state
        initial_state = {
            "question": topic,
            "conversation_history": [],
            "question_type": None,
            "sub_questions": [],
            "contested": False,
            "search_results": [],
            "answer": None,
            "citations": [],
            "confidence_score": 0.0,
            "retry_count": 0,
            "critic_feedback": None,
            "advocate_a_position": None,
            "advocate_b_position": None,
            "judge_synthesis": None,
            "debate_flag": False,
            "followup_questions": [],
            "_gap_queries": [],
        }

        # Execute graph with config
        config = {
            "max_retries": self.settings.graph_max_retries,
            "configurable": {
                "settings": self.settings,
                "thread_id": "default",
            },
        }

        # Add Langfuse tracing if configured
        if (
            self.settings.langfuse_public_key
            and self.settings.langfuse_secret_key
        ):
            try:
                from langfuse.callback import CallbackHandler

                langfuse_handler = CallbackHandler(
                    public_key=self.settings.langfuse_public_key,
                    secret_key=self.settings.langfuse_secret_key,
                )
                config["callbacks"] = [langfuse_handler]
                logger.info("Langfuse tracing enabled")
            except ImportError:
                logger.warning(
                    "Langfuse keys configured but langfuse not installed"
                )

        # Execute graph
        final_state = await self.qa_graph.ainvoke(initial_state, config)

        logger.info(
            f"LangGraph completed: confidence={final_state['confidence_score']:.2f}, "
            f"retries={final_state['retry_count']}, "
            f"debate={final_state['debate_flag']}"
        )

        return {
            "answer": final_state["answer"],
            "citations": final_state["citations"],
            "confidence": final_state["confidence_score"],
            "debate_flag": final_state["debate_flag"],
            "followups": final_state["followup_questions"],
            "critic_feedback": final_state.get("critic_feedback"),
        }

    async def research_topic_with_graph_stream(self, topic: str):
        """
        Research using LangGraph with streaming events.

        Args:
            topic: Topic or question to research

        Yields:
            Tuples of (event_type, data) where:
            - event_type: "node_start", "node_end", "complete"
            - data: Event-specific data (node name, state updates, final result)
        """
        if not self.qa_graph or not self.settings:
            raise ValueError("LangGraph not initialized")

        logger.info(f"Starting LangGraph streaming research: {topic[:100]}...")

        # Build initial state
        initial_state = {
            "question": topic,
            "conversation_history": [],
            "question_type": None,
            "sub_questions": [],
            "contested": False,
            "search_results": [],
            "answer": None,
            "citations": [],
            "confidence_score": 0.0,
            "retry_count": 0,
            "critic_feedback": None,
            "advocate_a_position": None,
            "advocate_b_position": None,
            "judge_synthesis": None,
            "debate_flag": False,
            "followup_questions": [],
            "_gap_queries": [],
        }

        # Execute graph with config
        config = {
            "max_retries": self.settings.graph_max_retries,
            "configurable": {
                "settings": self.settings,
                "thread_id": "default",
            },
        }

        # Add Langfuse tracing if configured
        if (
            self.settings.langfuse_public_key
            and self.settings.langfuse_secret_key
        ):
            try:
                from langfuse.callback import CallbackHandler

                langfuse_handler = CallbackHandler(
                    public_key=self.settings.langfuse_public_key,
                    secret_key=self.settings.langfuse_secret_key,
                )
                config["callbacks"] = [langfuse_handler]
                logger.info("Langfuse tracing enabled")
            except ImportError:
                logger.warning(
                    "Langfuse keys configured but langfuse not installed"
                )

        # Stream graph events
        final_state = None
        async for event in self.qa_graph.astream_events(initial_state, config, version="v2"):
            event_type = event.get("event")

            # Node start events
            if event_type == "on_chain_start":
                node_name = event.get("name", "")
                if node_name and node_name != "LangGraph":  # Skip root graph event
                    logger.debug(f"Node started: {node_name}")
                    yield ("node_start", {"node": node_name})

            # Node end events with state
            elif event_type == "on_chain_end":
                node_name = event.get("name", "")
                output = event.get("data", {}).get("output", {})

                if node_name and node_name != "LangGraph" and output:
                    logger.debug(f"Node completed: {node_name}")
                    yield ("node_end", {"node": node_name, "state": output})

                    # Track final state
                    if isinstance(output, dict):
                        final_state = output

        # Return final result
        if final_state:
            logger.info(
                f"LangGraph completed: confidence={final_state.get('confidence_score', 0):.2f}, "
                f"retries={final_state.get('retry_count', 0)}, "
                f"debate={final_state.get('debate_flag', False)}"
            )

            yield ("complete", {
                "answer": final_state.get("answer"),
                "citations": final_state.get("citations", []),
                "confidence": final_state.get("confidence_score", 0.0),
                "debate_flag": final_state.get("debate_flag", False),
                "followups": final_state.get("followup_questions", []),
                "critic_feedback": final_state.get("critic_feedback"),
            })

    async def cleanup(self):
        """Cleanup resources."""
        pass
