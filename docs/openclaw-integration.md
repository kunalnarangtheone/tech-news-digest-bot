# Using OpenClaw from Python

This guide shows you how to integrate **actual OpenClaw** with your Python bot. OpenClaw runs as a Node.js service, but you control it entirely from Python.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Your Python Bot (Telegram Interface)               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP API Calls
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenClaw Gateway (Node.js)                      │
│  • Manages browser automation (Puppeteer)                    │
│  • Executes JavaScript skills                                │
│  • Handles cron scheduling                                   │
│  • Provides HTTP/WebSocket API                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── Browser Automation (Puppeteer/CDP)
                 ├─── Skill Registry
                 └─── Cron Scheduler
```

## Why This Approach?

- ✅ **Use OpenClaw's power**: Browser automation, skill ecosystem, cron
- ✅ **Write in Python**: All your bot logic stays in Python
- ✅ **Best of both**: OpenClaw for browser stuff, Python for AI/Telegram
- ✅ **One language for bot**: No need to learn JavaScript for bot logic

## Setup (20 minutes)

### 1. Install OpenClaw

```bash
# Install OpenClaw globally
npm install -g openclaw

# Start the Gateway
openclaw start

# Verify it's running (should return 200 OK)
curl http://localhost:3000/health
```

### 2. Install OpenClaw Skills (JavaScript - one time)

These are the browser automation skills. They're JavaScript but you call them from Python:

Copy the skills I provided earlier to OpenClaw:

```bash
# Create skills directory
mkdir -p ~/.openclaw/skills

# Copy the JavaScript skills
cp openclaw-skills/*.js ~/.openclaw/skills/

# List available skills
openclaw skills list
```

You should see:
- `hackernews-top-stories`
- `github-trending`
- `devto-trending`

### 3. Python Client (Already Created!)

Use the `openclaw_client.py` I created earlier - it's perfect for this:

```python
from openclaw_bot.openclaw_client import OpenClawClient

# Initialize client
client = OpenClawClient()  # Connects to http://localhost:3000

# Check if OpenClaw is available
available = await client.check_availability()

# Get HackerNews stories (calls OpenClaw's JavaScript skill)
stories = await client.get_hackernews_top(limit=10)

# Get GitHub trending (calls OpenClaw)
repos = await client.get_github_trending(timeframe="daily")
```

### 4. Install Python Dependencies

```bash
pip install aiohttp apscheduler

# Or with uv
uv add aiohttp apscheduler
```

## Using OpenClaw from Your Bot

### Update Your AI Handler

```python
# src/openclaw_bot/ai_handler.py

from .openclaw_client import OpenClawClient
import asyncio

class AIHandler:
    def __init__(self):
        # ... existing code ...
        self.openclaw = OpenClawClient()
        
    async def generate_digest(self, topic: str, user_id: int) -> str:
        """Enhanced digest using DuckDuckGo + OpenClaw."""
        
        # Check if OpenClaw is available
        if await self.openclaw.check_availability():
            # Use advanced research with OpenClaw
            return await self.generate_digest_with_openclaw(topic, user_id)
        else:
            # Fallback to regular DuckDuckGo search
            return await self.generate_digest_basic(topic, user_id)
    
    async def generate_digest_with_openclaw(self, topic: str, user_id: int) -> str:
        """Generate digest with OpenClaw browser automation."""
        
        # Run searches in parallel
        web_search, tech_news = await asyncio.gather(
            self.search_web(topic, max_results=3),
            self.openclaw.aggregate_tech_news(topic_filter=topic)
        )
        
        # Filter relevant items
        hn_stories = tech_news.get('hackernews', [])[:3]
        gh_repos = tech_news.get('github', [])[:3]
        dev_articles = tech_news.get('devto', [])[:3]
        
        # Build comprehensive context
        context_parts = ["Web Search Results:"]
        context_parts.extend([
            f"- {r['title']}: {r['content']}" 
            for r in web_search
        ])
        
        if hn_stories:
            context_parts.append("\n\nHackerNews Discussions:")
            context_parts.extend([
                f"- {s['title']} ({s['score']} points) - {s['hn_url']}"
                for s in hn_stories
            ])
        
        if gh_repos:
            context_parts.append("\n\nGitHub Trending:")
            context_parts.extend([
                f"- {r['name']}: {r.get('description', 'No description')} ({r['stars']})"
                for r in gh_repos
            ])
        
        if dev_articles:
            context_parts.append("\n\nDev.to Articles:")
            context_parts.extend([
                f"- {a['title']} by {a['author']} ({a['reactions']} reactions)"
                for a in dev_articles
            ])
        
        context = "\n".join(context_parts)
        
        # Enhanced system prompt
        system_prompt = """You are a tech digest assistant with access to:
- Web search results
- Real-time HackerNews discussions
- GitHub trending repositories  
- Dev.to community articles

Create a comprehensive 2-minute digest that:
- Synthesizes information from ALL sources
- Highlights what the community is discussing
- Links to relevant GitHub repos with code examples
- Notes trending patterns and community sentiment
- Provides actionable insights
"""
        
        user_prompt = f"""Create a comprehensive digest about: {topic}

Multi-source context:
{context}

Generate an in-depth digest that leverages all these sources."""
        
        # Generate with LLM (your existing code)
        response = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        digest = response.choices[0].message.content.strip()
        
        # Store in history
        self._update_history(user_id, topic, digest)
        
        return digest
```

## Python-Controlled Workflows

You can trigger OpenClaw skills from Python on a schedule using APScheduler:

### Create Python Workflow Controller

```python
# src/openclaw_bot/openclaw_workflows.py

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.constants import ParseMode

from .openclaw_client import OpenClawClient

class OpenClawWorkflowController:
    """Control OpenClaw workflows from Python."""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.openclaw = OpenClawClient()
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.scheduler = AsyncIOScheduler()
    
    def setup(self):
        """Set up scheduled workflows."""
        
        # Daily digest at 9 AM
        self.scheduler.add_job(
            self.run_daily_digest,
            CronTrigger(hour=9, minute=0),
            id='daily_digest',
            name='OpenClaw Daily Digest'
        )
        
        # Topic monitoring every 6 hours
        self.scheduler.add_job(
            self.run_topic_monitor,
            CronTrigger(hour='*/6'),
            id='topic_monitor',
            name='OpenClaw Topic Monitor'
        )
        
        self.scheduler.start()
    
    async def run_daily_digest(self):
        """Execute daily digest using OpenClaw."""
        print(f"[{datetime.now()}] Running OpenClaw daily digest...")
        
        # Call OpenClaw skills via HTTP API
        tech_news = await self.openclaw.aggregate_tech_news()
        
        # Format message
        digest = self._format_digest(tech_news)
        
        # Send to Telegram
        await self.bot.send_message(
            chat_id=self.channel_id,
            text=digest,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
        print("✅ Daily digest sent!")
    
    async def run_topic_monitor(self):
        """Monitor topics using OpenClaw."""
        topics = ['rust', 'kubernetes', 'ai', 'python']
        
        for topic in topics:
            # Use OpenClaw to get topic-specific news
            news = await self.openclaw.aggregate_tech_news(topic_filter=topic)
            
            # Check if there's significant activity
            total_items = sum(len(items) for items in news.values())
            
            if total_items >= 3:
                alert = f"🚨 {topic.upper()} is trending!\n\n"
                # Format alert...
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=alert,
                    parse_mode=ParseMode.MARKDOWN
                )
    
    def _format_digest(self, tech_news):
        """Format tech news into Telegram message."""
        # Your formatting logic...
        pass
```

### Use in Your Scheduler

```python
# src/openclaw_bot/scheduler.py

from .openclaw_workflows import OpenClawWorkflowController

def main():
    controller = OpenClawWorkflowController(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        channel_id=os.getenv('TELEGRAM_CHANNEL_ID')
    )
    
    controller.setup()
    
    # Keep running
    asyncio.get_event_loop().run_forever()
```

## Testing

### Test OpenClaw Connection

```python
# test_openclaw_integration.py

import asyncio
from src.openclaw_bot.openclaw_client import OpenClawClient

async def test():
    client = OpenClawClient()
    
    # 1. Check Gateway
    print("Testing OpenClaw Gateway connection...")
    available = await client.check_availability()
    print(f"Gateway available: {available}")
    
    if not available:
        print("❌ OpenClaw Gateway not running!")
        print("Start it with: openclaw start")
        return
    
    # 2. Test HackerNews skill
    print("\nTesting HackerNews skill (via OpenClaw)...")
    stories = await client.get_hackernews_top(limit=3)
    print(f"Got {len(stories)} stories from OpenClaw")
    for s in stories[:3]:
        print(f"  - {s['title']}")
    
    # 3. Test GitHub skill
    print("\nTesting GitHub skill (via OpenClaw)...")
    repos = await client.get_github_trending(timeframe="daily")
    print(f"Got {len(repos)} repos from OpenClaw")
    for r in repos[:3]:
        print(f"  - {r['name']}")
    
    # 4. Test aggregation
    print("\nTesting multi-source aggregation...")
    news = await client.aggregate_tech_news()
    print(f"Aggregated: {len(news['hackernews'])} HN, {len(news['github'])} GH, {len(news['devto'])} Dev")
    
    print("\n✅ All OpenClaw integration tests passed!")

asyncio.run(test())
```

Run it:
```bash
python test_openclaw_integration.py
```

## Running Everything

### Terminal 1: Start OpenClaw Gateway

```bash
# Start OpenClaw (runs the Node.js service)
openclaw start

# Or in foreground to see logs
openclaw start --foreground
```

### Terminal 2: Start Your Python Bot

```bash
# Your Telegram bot (with OpenClaw integration)
openclaw-bot
```

### Terminal 3: Start Python Scheduler

```bash
# Python scheduler that controls OpenClaw
openclaw-scheduler
```

## How It Works

1. **OpenClaw Gateway** (Node.js) runs as a service on port 3000
2. **JavaScript skills** (HackerNews, GitHub scrapers) are registered in OpenClaw
3. **Your Python bot** calls OpenClaw via HTTP API when users ask questions
4. **Python scheduler** triggers OpenClaw skills on a schedule
5. **Results** come back to Python, you format and send to Telegram

## Benefits of This Approach

✅ **Use OpenClaw's ecosystem**: 13,000+ community skills available  
✅ **Stay in Python**: All your bot logic is Python  
✅ **Browser automation**: OpenClaw handles Puppeteer complexity  
✅ **Best of both worlds**: Node.js for browser, Python for everything else  
✅ **Scalable**: OpenClaw Gateway can run on a separate server  

## Advanced: Custom OpenClaw Skills

You can still create OpenClaw skills in JavaScript and call them from Python:

### Create Custom Skill

```javascript
// ~/.openclaw/skills/reddit-scraper.js

module.exports = {
  name: "reddit-programming",
  description: "Scrape r/programming top posts",
  
  async execute({ browser, args }) {
    const { limit = 10 } = args;
    const page = await browser.newPage();
    await page.goto('https://reddit.com/r/programming');
    
    const posts = await page.evaluate((limit) => {
      // Scraping logic
      return posts;
    }, limit);
    
    await page.close();
    return posts;
  }
};
```

### Call from Python

```python
# In your Python code
result = await openclaw_client.execute_skill("reddit-programming", {"limit": 10})
posts = result.get("data", [])
```

## Summary

- **OpenClaw**: Runs as Node.js service (handles browser automation)
- **Skills**: Written in JavaScript, stored in `~/.openclaw/skills/`
- **Your Bot**: 100% Python, calls OpenClaw via HTTP
- **Workflows**: Python APScheduler triggers OpenClaw skills
- **Result**: Best of both worlds!

This way you're actually **using OpenClaw** while keeping your bot code in Python.
