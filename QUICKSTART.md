# Quick Start Guide - Autonomous Multi-Agent Q&A System

## Prerequisites

- Python 3.14+
- Node.js 20+ (for frontend)
- Groq API key (free at https://console.groq.com/)

## 5-Minute Setup

### 1. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
# Required:
GROQ_API_KEY=your_actual_key_here

# Optional (for observability):
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

### 2. Install Python Dependencies

```bash
# Using uv (recommended - faster)
uv pip install -e .

# OR using pip
pip install -e .
```

### 3. Test the System

```bash
# Run the test script
python test_graph.py
```

You should see three tests run:
1. ✅ Simple question (fast path, ~2-4s)
2. ✅ Complex question (parallel search, ~8-12s)
3. ✅ Contested question (adversarial debate, ~15-20s)

### 4. Start the Backend API

```bash
uvicorn src.tech_digest_bot.api.main:app --reload
```

API will be available at http://localhost:8000

### 5. Start the Frontend (Optional)

```bash
cd frontend
npm install  # First time only
npm run dev
```

Frontend will be available at http://localhost:3000

## Quick Test from Command Line

```python
import asyncio
from src.tech_digest_bot.config.settings import get_settings
from src.tech_digest_bot.ai.llm import LLMClient
from src.tech_digest_bot.ai.research import ResearchService

async def ask(question):
    settings = get_settings()
    llm = LLMClient(settings)
    research = ResearchService(llm, use_agent=True, settings=settings)
    await research.initialize()
    
    result = await research.research_topic_with_graph(question)
    
    print(f"\n{'='*80}")
    print(f"Q: {question}")
    print(f"{'='*80}\n")
    print(result['answer'])
    print(f"\n📊 Confidence: {result['confidence']:.0%}")
    print(f"⚖️  Debate: {result['debate_flag']}")
    print(f"📚 Sources: {len(result['citations'])}")
    
    if result['followups']:
        print(f"\n💡 Follow-up questions:")
        for fq in result['followups']:
            print(f"   • {fq['question']}")

# Test it
asyncio.run(ask("What is React?"))
```

## What to Expect

### Simple Question Example

**Input:** "What is React?"

**Behavior:**
- Classifier → "simple" (Llama 3.1 8B, ~500ms)
- Fast Path → 1 search + synthesis (Llama 3.3 70B, ~2s)
- Critic → evaluates sources, passes (confidence ~0.85)
- Follow-up → suggests 2-3 related questions

**Total time:** ~3-4 seconds

### Complex Question Example

**Input:** "Compare React, Vue, and Angular"

**Behavior:**
- Classifier → "complex" (8B, ~500ms)
- Planner → decomposes into 4 sub-questions (8B, ~1s)
- Search Agents → 4 agents run in PARALLEL (8B × 4, ~6s)
  - Agent 1: "React features"
  - Agent 2: "Vue strengths"  
  - Agent 3: "Angular advantages"
  - Agent 4: "Performance comparison"
- Synthesizer → combines ~12 sources (70B, ~3s)
- Critic → validates (confidence ~0.75), passes
- Follow-up → suggests questions

**Total time:** ~12-15 seconds

### Contested Question Example

**Input:** "Should I use microservices or monolithic architecture?"

**Behavior:**
- Classifier → "contested" (8B, ~500ms)
- Planner → decomposes + sets `contested: true` (8B, ~1s)
- Search Agents → 3-4 agents in parallel (~6s)
- **Adversarial Layer:**
  - Advocate PRO (microservices) - 70B, ~4s
  - Advocate CON (monolith) - 70B, ~4s (parallel!)
  - Judge synthesizes balanced view - 70B, ~3s
- Critic → checks, might trigger RETRY if gaps found
  - If retry: +6-10s for gap-specific re-search
- Follow-up → suggests questions

**Total time:** ~18-25 seconds (with potential retry)

**Output includes:** ⚖️ "Multiple perspectives analyzed" badge

## Observing the Autonomous Retry

To see the critic's autonomous retry in action, ask a question with limited web sources:

```python
asyncio.run(ask("Explain Turbopack's incremental engine architecture"))
```

**What happens:**
1. Initial search finds ~2-3 sources
2. Synthesizer creates answer
3. **Critic evaluates:** "Only 2 sources, confidence = 0.52"
4. **Critic decides:** "Below threshold (0.6) → RETRY"
5. **Autonomous retry** (no user prompt!)
   - Generates gap-specific queries
   - Re-dispatches search agents
   - Finds +4-5 more sources
6. **Critic re-evaluates:** "7 sources, confidence = 0.78 → PASS"

**No user intervention required!**

## Configuration Options

Edit `.env` to tune behavior:

```bash
# Enable/disable the multi-agent system
USE_LANGGRAPH=true

# Maximum autonomous retries (0-5)
GRAPH_MAX_RETRIES=2

# Confidence threshold to trigger retry (0.0-1.0)
# Lower = more retries, higher quality
# Higher = fewer retries, faster responses
GRAPH_CONFIDENCE_THRESHOLD=0.6
```

**Tuning guide:**
- **Conservative (high quality):** `GRAPH_CONFIDENCE_THRESHOLD=0.7`, `GRAPH_MAX_RETRIES=3`
- **Balanced (default):** `GRAPH_CONFIDENCE_THRESHOLD=0.6`, `GRAPH_MAX_RETRIES=2`
- **Fast (fewer retries):** `GRAPH_CONFIDENCE_THRESHOLD=0.5`, `GRAPH_MAX_RETRIES=1`

## Observability with Langfuse

1. Sign up at https://langfuse.com (free tier available)
2. Get your public/secret keys
3. Add to `.env`:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk_xxx
   LANGFUSE_SECRET_KEY=sk_xxx
   ```
4. Run any question
5. View trace at https://cloud.langfuse.com

**You'll see:**
- Full graph execution DAG
- Every node with timing
- LLM calls with token counts
- Cost breakdown (8B vs 70B usage)
- **Retry loops highlighted in red**

## Troubleshooting

### "Groq API key is required"
→ Make sure `.env` exists and has `GROQ_API_KEY=...`

### "Rate limit exceeded"
→ Groq free tier has limits. Wait 60s or upgrade to paid tier.

### Search agents returning no results
→ DuckDuckGo might be rate-limiting. Wait a moment and retry.

### Web scraping fails (403 errors)
→ Normal! System falls back to DuckDuckGo snippets automatically.

### Answer confidence always low
→ Lower threshold in `.env`: `GRAPH_CONFIDENCE_THRESHOLD=0.5`

## Next Steps

1. **Try different question types** to see routing behavior
2. **Watch the retry loop** with obscure technical questions
3. **Check Langfuse** to visualize the graph execution
4. **Update frontend** to display confidence/debate/follow-ups
5. **Tune thresholds** to optimize speed vs. quality

## API Endpoints

Once the backend is running:

- **POST /api/chat/stream** - Stream responses with SSE
  ```bash
  curl -X POST http://localhost:8000/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"message": "What is React?"}'
  ```

- **POST /api/chat** - Non-streaming response
- **GET /api/health** - Health check

## Example Questions to Try

**Simple (Fast Path):**
- "What is Python?"
- "Who created Linux?"
- "When was Rust released?"

**Complex (Parallel Search):**
- "Compare Python, Go, and Rust for backend development"
- "Explain the JAMstack architecture"
- "What are the differences between SQL and NoSQL databases?"

**Contested (Adversarial Debate):**
- "Should I use TypeScript or JavaScript?"
- "Is serverless architecture worth it?"
- "Microservices vs monolith: which is better?"
- "Should startups use Kubernetes?"

**Retry-Triggering (Low Sources):**
- "Explain Turbopack's incremental compilation"
- "How does Bun's transpiler work internally?"
- "What is the Zig build system architecture?"

## Success Indicators

You know it's working when you see:

✅ **Fast path:** Simple questions answered in <5s  
✅ **Parallel search:** Complex questions show "Researching 4 aspects"  
✅ **Adversarial debate:** Contested questions show ⚖️ badge  
✅ **Autonomous retry:** Log shows "🔄 Critic retry 1/2" for low-confidence answers  
✅ **High confidence:** Final answers have 0.7+ confidence score  
✅ **Follow-ups:** 2-3 suggested questions appear after answer  

Enjoy your autonomous multi-agent Q&A system! 🚀
