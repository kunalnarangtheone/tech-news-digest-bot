# Autonomous Multi-Agent Q&A System - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                      USER QUESTION                                      │
│                           ↓                                             │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    CLASSIFIER NODE                              │   │
│  │              (Llama 3.1 8B - Fast)                              │   │
│  │                                                                 │   │
│  │  Categorizes as:                                                │   │
│  │  • simple    - factual, one-answer questions                    │   │
│  │  • complex   - multi-faceted research                           │   │
│  │  • contested - trade-offs, opinions                             │   │
│  └────────────────────────────────────────────────────────────────┘   │
│           │                                │                            │
│    simple │                                │ complex/contested          │
│           ↓                                ↓                            │
│                                                                         │
│  ┌─────────────────────┐        ┌─────────────────────────────┐       │
│  │   FAST PATH         │        │     PLANNER NODE            │       │
│  │  (Llama 3.3 70B)    │        │   (Llama 3.1 8B)            │       │
│  │                     │        │                             │       │
│  │ • 1 search          │        │ • Decomposes into 3-5       │       │
│  │ • 1 LLM call        │        │   sub-questions             │       │
│  │ • < 2 seconds       │        │ • Sets contested flag       │       │
│  └─────────────────────┘        └─────────────────────────────┘       │
│           │                                │                            │
│           │                                ↓                            │
│           │                                                             │
│           │                  ┌─────────────────────────────────┐       │
│           │                  │   PARALLEL SEARCH AGENTS        │       │
│           │                  │      (via Send() fanout)        │       │
│           │                  │                                 │       │
│           │                  │  ┌─────┐  ┌─────┐  ┌─────┐    │       │
│           │                  │  │ S1  │  │ S2  │  │ S3  │    │       │
│           │                  │  │ 8B  │  │ 8B  │  │ 8B  │    │       │
│           │                  │  └─────┘  └─────┘  └─────┘    │       │
│           │                  │                                 │       │
│           │                  │ Each agent:                     │       │
│           │                  │ • 2-3 DuckDuckGo queries        │       │
│           │                  │ • Fetches full page content     │       │
│           │                  │ • Returns ~3 source chunks      │       │
│           │                  └─────────────────────────────────┘       │
│           │                                │                            │
│           │                                ↓                            │
│           │                                                             │
│           │                  ┌─────────────────────────────────┐       │
│           │                  │    CONTESTED ROUTER             │       │
│           │                  │  (reads contested flag)         │       │
│           │                  └─────────────────────────────────┘       │
│           │                     │                    │                  │
│           │              standard                    │ contested        │
│           │                     ↓                    ↓                  │
│           │                                                             │
│           │       ┌──────────────────┐    ┌──────────────────────┐    │
│           │       │  SYNTHESIZER     │    │  ADVERSARIAL LAYER   │    │
│           │       │ (Llama 3.3 70B)  │    │   (Llama 3.3 70B)    │    │
│           │       │                  │    │                      │    │
│           │       │ • Combines       │    │  ┌─────────────┐    │    │
│           │       │   sources        │    │  │ Advocate A  │    │    │
│           │       │ • Cites [1][2]   │    │  │ (PRO)       │    │    │
│           │       │ • Thorough       │    │  └─────────────┘    │    │
│           │       └──────────────────┘    │         ↓           │    │
│           │                │               │  ┌─────────────┐    │    │
│           │                │               │  │ Advocate B  │    │    │
│           │                │               │  │ (CON)       │    │    │
│           │                │               │  └─────────────┘    │    │
│           │                │               │         ↓           │    │
│           │                │               │  ┌─────────────┐    │    │
│           │                │               │  │   JUDGE     │    │    │
│           │                │               │  │ Synthesizer │    │    │
│           │                │               │  │             │    │    │
│           │                │               │  │ • Balanced  │    │    │
│           │                │               │  │ • Surfaces  │    │    │
│           │                │               │  │   disagree  │    │    │
│           │                │               │  └─────────────┘    │    │
│           │                │               └──────────────────────┘    │
│           │                │                         │                 │
│           └────────────────┴─────────────────────────┘                 │
│                              ↓                                          │
│                                                                         │
│          ┌───────────────────────────────────────────────────────┐    │
│          │              ⭐ CRITIC NODE ⭐                         │    │
│          │            (Llama 3.3 70B)                             │    │
│          │                                                        │    │
│          │  THE KEY AUTONOMOUS FEATURE:                           │    │
│          │                                                        │    │
│          │  Evaluates answer quality objectively:                 │    │
│          │  • Count independent sources corroborating claims      │    │
│          │  • Check for inter-source contradictions              │    │
│          │  • NOT self-reported LLM confidence (miscalibrated!)   │    │
│          │                                                        │    │
│          │  Decision thresholds:                                  │    │
│          │  • ≥3 sources + no contradictions = PASS              │    │
│          │  • <3 sources OR contradictions = RETRY               │    │
│          │                                                        │    │
│          │  If RETRY (max 2x):                                    │    │
│          │  • Identifies specific knowledge gaps                  │    │
│          │  • Generates 1-3 gap-filling queries                   │    │
│          │  • Loops back to Search Agents                         │    │
│          └───────────────────────────────────────────────────────┘    │
│                      │                          │                      │
│                 confidence                      │                      │
│                 < threshold                confidence                  │
│                      │                       ≥ threshold               │
│                      │                          │                      │
│                      │                          ↓                      │
│              ┌───────┴──────┐                                          │
│              │               │                                          │
│              ↓               │          ┌──────────────────────┐       │
│         RETRY LOOP           │          │   FOLLOWUP AGENT     │       │
│         (max 2x)             │          │  (Llama 3.1 8B)      │       │
│              │               │          │                      │       │
│              │               │          │ • 2-3 related Qs     │       │
│         Gap queries          │          │ • Brief preview      │       │
│              │               │          │   answers            │       │
│              ↓               │          │ • Non-blocking       │       │
│       Search Agents ─────────┘          └──────────────────────┘       │
│       (targeted                                    │                   │
│        re-search)                                  ↓                   │
│                                                                         │
│                                        FINAL ANSWER                     │
│                                             +                           │
│                                        Metadata:                        │
│                                        • Confidence score               │
│                                        • Citations                      │
│                                        • Debate flag                    │
│                                        • Follow-up questions            │
│                                        • Critic feedback                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Model Usage by Node

| Node           | Model           | Why                                    |
|----------------|-----------------|----------------------------------------|
| Classifier     | Llama 3.1 8B    | Fast, simple categorization            |
| Fast Path      | Llama 3.3 70B   | Quality matters for user-facing answer |
| Planner        | Llama 3.1 8B    | Fast decomposition, low cost           |
| Search Agents  | Llama 3.1 8B    | High volume, parallel execution        |
| Synthesizer    | Llama 3.3 70B   | Quality synthesis for final answer     |
| Advocate A/B   | Llama 3.3 70B   | Persuasive, nuanced argumentation      |
| Judge          | Llama 3.3 70B   | Balanced synthesis requires quality    |
| **Critic**     | **Llama 3.3 70B** | **Most important: quality evaluation** |
| Follow-up      | Llama 3.1 8B    | Suggestions, not critical path         |

## Request Lifecycle Examples

### Example 1: Simple Question ("What is React?")

```
User → "What is React?"
  ↓
Classifier (8B) → "simple"
  ↓
Fast Path (70B)
  ├─ 1 DuckDuckGo search (5 results)
  ├─ Synthesize answer
  └─ (~2s)
  ↓
Critic (70B)
  ├─ Checks: 5 sources, no contradictions
  ├─ Confidence: 0.85
  └─ PASS (no retry)
  ↓
Follow-up (8B)
  └─ "What are React hooks?", "Compare React and Vue"
  ↓
DONE (~3s total)
```

### Example 2: Complex Question ("Compare React, Vue, and Angular")

```
User → "Compare React, Vue, and Angular"
  ↓
Classifier (8B) → "complex"
  ↓
Planner (8B)
  ├─ Sub-Q1: "What are React's key features?"
  ├─ Sub-Q2: "What are Vue's strengths?"
  ├─ Sub-Q3: "What are Angular's advantages?"
  ├─ Sub-Q4: "Performance comparison"
  └─ contested: false
  ↓
3 Search Agents (8B) IN PARALLEL
  ├─ Agent 1 → searches Q1 → 3 sources
  ├─ Agent 2 → searches Q2 → 3 sources
  └─ Agent 3 → searches Q3, Q4 → 4 sources
  (~6s, parallel)
  ↓
Contested Router → "standard" (not contested)
  ↓
Synthesizer (70B)
  └─ Combines 10 sources → comprehensive answer
  ↓
Critic (70B)
  ├─ Checks: 10 sources, good agreement
  ├─ Confidence: 0.78
  └─ PASS
  ↓
Follow-up (8B)
  ↓
DONE (~12s total)
```

### Example 3: Contested Question with Retry ("Should I use microservices?")

```
User → "Should I use microservices or monolith?"
  ↓
Classifier (8B) → "contested"
  ↓
Planner (8B)
  ├─ Sub-Q1: "Microservices benefits"
  ├─ Sub-Q2: "Monolith benefits"
  ├─ Sub-Q3: "Trade-offs and when to use each"
  └─ contested: TRUE ⚖️
  ↓
3 Search Agents (8B) IN PARALLEL
  └─ 9 sources collected
  ↓
Contested Router → "adversarial"
  ↓
Advocate A (70B) ──┐
  (PRO microservices)
                     ├─ PARALLEL
Advocate B (70B) ──┘
  (PRO monolith)
  ↓
Judge (70B)
  └─ Balanced synthesis acknowledging trade-offs
  ↓
Critic (70B) - FIRST PASS
  ├─ Checks: 9 sources, but some gaps on "team size" context
  ├─ Confidence: 0.52 (< 0.6 threshold!)
  └─ RETRY (generates gap queries)
  ↓
🔄 AUTONOMOUS RETRY (retry 1/2)
  ↓
3 Search Agents (8B) with gap queries
  ├─ Gap Q1: "microservices team size requirements"
  ├─ Gap Q2: "monolith scalability limits"
  └─ Gap Q3: "when to split monolith"
  └─ +6 more sources
  ↓
Re-synthesize (reuse judge output + new sources)
  ↓
Critic (70B) - SECOND PASS
  ├─ Checks: 15 sources total, comprehensive coverage
  ├─ Confidence: 0.82
  └─ PASS ✓
  ↓
Follow-up (8B)
  ↓
DONE (~22s total, with 1 retry)
```

## Key Autonomous Behaviors

### 1. Question Classification (No User Input)
- Automatically detects if question is simple, complex, or contested
- Routes to appropriate pipeline
- User never asked "is this simple or complex?"

### 2. Parallel Search Dispatch (No User Input)
- Planner generates sub-questions
- All search agents fire simultaneously via `Send()`
- No sequential bottleneck

### 3. **Autonomous Retry (No User Input)** ⭐
- Critic evaluates quality objectively
- If confidence < threshold → automatically re-searches
- Generates specific gap-filling queries
- Loops up to 2 times without asking user
- **This is the killer feature**

### 4. Adversarial Debate (No User Input)
- Planner detects contested question
- Automatically triggers PRO + CON advocates
- Judge synthesizes balanced view
- User sees "⚖️ Multiple perspectives" badge

### 5. Follow-up Suggestions (No User Input)
- Generates related questions automatically
- Runs in background (non-blocking)
- Appears after main answer

## Confidence Scoring (Objective, Not Self-Reported)

```python
def calculate_confidence(search_results, answer):
    # Extract key claims from answer
    claims = extract_claims(answer)
    
    # Count independent sources supporting each claim
    corroboration = {}
    for claim in claims:
        corroboration[claim] = count_supporting_sources(claim, search_results)
    
    # Check for contradictions
    contradictions = find_contradictions(search_results)
    
    # Objective scoring
    min_corroboration = min(corroboration.values())
    has_contradictions = len(contradictions) > 0
    
    if min_corroboration >= 3 and not has_contradictions:
        return 0.85  # High confidence
    elif min_corroboration >= 2 and not has_contradictions:
        return 0.70  # Medium confidence
    elif min_corroboration >= 1 and not has_contradictions:
        return 0.55  # Low confidence
    else:
        return 0.30  # Very low (contradictions or no sources)
```

This is **objective** and **measurable**, unlike asking the LLM "how confident are you?" (which is miscalibrated).

## Why This Architecture Works

1. **Fast Path Optimization** - Simple questions skip expensive multi-agent pipeline
2. **Parallel Execution** - Search agents run simultaneously, not sequentially
3. **Model Tiering** - 8B for volume work, 70B for quality (cost optimization)
4. **Autonomous Quality Control** - Critic catches low-quality answers without user intervention
5. **Adversarial Robustness** - Contested questions get balanced treatment, not one-sided answers
6. **Graceful Degradation** - Each component has fallback behavior

## Comparison to Original System

| Feature | Before | After |
|---------|--------|-------|
| Answer Quality | Single LLM call | Multi-agent synthesis |
| Quality Control | None | Autonomous critic with retry |
| Contested Questions | One-sided | Adversarial debate |
| Search Strategy | Sequential | Parallel agents |
| Cost Optimization | Single model | Tiered (8B/70B) |
| Confidence Scoring | None | Objective source corroboration |
| Observability | Basic logging | Langfuse tracing |

**Result:** A simple chatbot → **Autonomous research assistant with quality control**
