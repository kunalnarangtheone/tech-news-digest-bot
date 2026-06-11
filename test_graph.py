#!/usr/bin/env python3
"""Test script for LangGraph multi-agent Q&A system."""

import asyncio
import logging
from src.tech_digest_bot.config.settings import get_settings
from src.tech_digest_bot.ai.llm import LLMClient
from src.tech_digest_bot.ai.research import ResearchService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_simple_question():
    """Test simple question - should use fast path."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Simple Question (Fast Path)")
    logger.info("=" * 80)

    settings = get_settings()
    llm = LLMClient(settings)
    research = ResearchService(llm, use_agent=True, settings=settings)

    await research.initialize()

    question = "What is React?"
    logger.info(f"\nQuestion: {question}")

    result = await research.research_topic_with_graph(question)

    logger.info(f"\n✓ Answer:\n{result['answer'][:500]}...")
    logger.info(f"\n✓ Confidence: {result['confidence']:.2%}")
    logger.info(f"✓ Debate flag: {result['debate_flag']}")
    logger.info(f"✓ Citations: {len(result['citations'])} sources")
    logger.info(
        f"✓ Follow-ups: {len(result['followups'])} suggested questions"
    )

    return result


async def test_complex_question():
    """Test complex question - should trigger planner + parallel search."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Complex Question (Parallel Search Agents)")
    logger.info("=" * 80)

    settings = get_settings()
    llm = LLMClient(settings)
    research = ResearchService(llm, use_agent=True, settings=settings)

    await research.initialize()

    question = "Compare React, Vue, and Angular for building web applications"
    logger.info(f"\nQuestion: {question}")

    result = await research.research_topic_with_graph(question)

    logger.info(f"\n✓ Answer:\n{result['answer'][:500]}...")
    logger.info(f"\n✓ Confidence: {result['confidence']:.2%}")
    logger.info(f"✓ Debate flag: {result['debate_flag']}")
    logger.info(f"✓ Critic feedback: {result['critic_feedback']}")
    logger.info(f"✓ Citations: {len(result['citations'])} sources")

    return result


async def test_contested_question():
    """Test contested question - should trigger adversarial advocates."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Contested Question (Adversarial Debate)")
    logger.info("=" * 80)

    settings = get_settings()
    llm = LLMClient(settings)
    research = ResearchService(llm, use_agent=True, settings=settings)

    await research.initialize()

    question = "Should I use microservices or monolithic architecture?"
    logger.info(f"\nQuestion: {question}")

    result = await research.research_topic_with_graph(question)

    logger.info(f"\n✓ Answer:\n{result['answer'][:500]}...")
    logger.info(f"\n✓ Confidence: {result['confidence']:.2%}")
    logger.info(f"✓ Debate flag: {result['debate_flag']}")
    logger.info(f"✓ Critic feedback: {result['critic_feedback']}")
    logger.info(
        f"✓ Follow-ups: {len(result['followups'])} suggested questions"
    )

    if result["debate_flag"]:
        logger.info(
            "\n⚖️  ADVERSARIAL DEBATE was used - multiple perspectives synthesized!"
        )

    return result


async def main():
    """Run all tests."""
    try:
        # Test 1: Simple question (fast path)
        await test_simple_question()

        # Test 2: Complex question (parallel search)
        await test_complex_question()

        # Test 3: Contested question (adversarial debate)
        await test_contested_question()

        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
