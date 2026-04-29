#!/usr/bin/env python3
"""Quick test script to verify Groq integration with the bot."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tech_digest_bot.ai.llm import LLMClient
from tech_digest_bot.config import get_settings


async def test_groq_llm():
    """Test Groq LLM client."""
    print("=" * 80)
    print("Testing Groq Integration with Tech Digest Bot")
    print("=" * 80)

    # Load settings
    settings = get_settings()

    print(f"\n✓ Model: {settings.groq_model}")
    print(f"✓ API Key: {settings.groq_api_key[:20]}...")

    # Create LLM client
    llm = LLMClient(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
    )

    print("\n✓ LLM Client created with Groq")

    # Test generation
    print("\n" + "=" * 80)
    print("Test 1: Simple Generation")
    print("=" * 80)

    prompt = "What is Python in one sentence?"
    print(f"\nPrompt: {prompt}")
    print("\nResponse: ", end="", flush=True)

    response = await llm.generate(prompt, max_tokens=100)
    print(response)

    # Test digest generation
    print("\n" + "=" * 80)
    print("Test 2: Digest Generation")
    print("=" * 80)

    topic = "WebAssembly"
    context = """WebAssembly (Wasm) is a binary instruction format designed as a portable compilation target for programming languages.
    It enables high-performance applications on web browsers and can run alongside JavaScript.
    Major browsers support WebAssembly, and it's being adopted for serverless computing and edge computing."""

    print(f"\nTopic: {topic}")
    print("\nGenerating digest...")

    digest = await llm.generate_digest(
        topic=topic,
        context=context,
        max_tokens=500
    )

    print(f"\n{digest}")

    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_groq_llm())
