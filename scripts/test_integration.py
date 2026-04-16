#!/usr/bin/env python3
"""Test OpenClaw integration."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tech_digest_bot.search import OpenClawClient


async def test_openclaw() -> bool:
    """Test OpenClaw integration."""
    print("🧪 Testing OpenClaw Integration\n")
    print("=" * 60)

    client = OpenClawClient()

    # Test 1: Gateway availability
    print("\n📡 Test 1: OpenClaw Gateway Connection")
    print("-" * 60)
    available = await client.check_availability()

    if not available:
        print("❌ OpenClaw Gateway is NOT running!")
        print("\nPlease start OpenClaw:")
        print("  1. Install: npm install -g openclaw")
        print("  2. Start:   openclaw start")
        print("  3. Verify:  curl http://localhost:3000/health")
        return False

    print("✅ Gateway is running\n")

    # Test 2: HackerNews skill
    print("\n📰 Test 2: HackerNews Skill")
    print("-" * 60)
    stories = await client.get_hackernews_top(limit=3)
    if stories:
        print(f"✅ Got {len(stories)} stories:\n")
        for story in stories[:3]:
            print(f"  {story.get('rank')}. {story.get('title', '')[:65]}")
            print(f"     {story.get('score')} points\n")
    else:
        print("⚠️  No stories - install skills:")
        print("   cp openclaw/skills/*.js ~/.openclaw/skills/")

    # Test 3: GitHub skill
    print("\n⭐ Test 3: GitHub Trending Skill")
    print("-" * 60)
    repos = await client.get_github_trending(timeframe="daily", limit=3)
    if repos:
        print(f"✅ Got {len(repos)} repos:\n")
        for repo in repos[:3]:
            print(f"  {repo.get('rank')}. {repo.get('name', '')}")
            print(f"     {repo.get('stars', '')}\n")
    else:
        print("⚠️  No repos returned")

    # Test 4: Aggregation
    print("\n🔄 Test 4: Multi-Source Aggregation")
    print("-" * 60)
    news = await client.aggregate_tech_news()
    total = sum(len(items) for items in news.values())
    print(f"✅ Aggregated {total} items:")
    print(f"   • HackerNews: {len(news['hackernews'])} stories")
    print(f"   • GitHub:     {len(news['github'])} repos")
    print(f"   • Dev.to:     {len(news['devto'])} articles")

    print("\n" + "=" * 60)
    print("✅ Tests completed!\n")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_openclaw())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)
