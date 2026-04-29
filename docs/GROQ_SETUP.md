# Groq Setup Guide

The tech news digest bot uses **Groq** for ultra-fast LLM inference.

## Why Groq?

- ⚡ **Ultra-fast inference** - Groq's LPU architecture provides extremely low latency
- 🆓 **Free tier** - Generous rate limits on the free tier
- ☁️ **Cloud-based** - No need to run local models
- 🚀 **High quality** - Access to powerful models like llama-3.3-70b-versatile

## Setup Steps

### 1. Get Your Groq API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (starts with `gsk_...`)

### 2. Configure the Bot

Add your API key to `.env`:

```bash
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Test the Integration

```bash
python scripts/test_bot_groq.py
```

You should see:
- ✓ Model configuration
- ✓ Simple generation test
- ✓ Digest generation test

## Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `llama-3.3-70b-versatile` | Most capable, balanced | General use (default) |
| `llama-3.1-8b-instant` | Fastest responses | Quick queries |

Check [Groq Models](https://console.groq.com/docs/models) for the latest available models.

## Performance

With Groq, your bot will have:
- **3-8 second** response times for full research
- **< 1 second** for knowledge graph queries
- **No local GPU** requirements
- **No model downloads** needed

## Rate Limits

The free tier includes:
- Generous daily request limits
- High tokens per minute
- Multiple concurrent requests

If you hit rate limits:
1. Wait for the limit to reset (usually quick)
2. Monitor usage in the Groq dashboard
3. Consider upgrading if needed

## Troubleshooting

### "API key is required"

Make sure your `.env` file has:
```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

### Connection errors

1. Check your internet connection
2. Verify the API key is correct
3. Check [Groq status page](https://status.groq.com/)

### Model errors

If a model is decommissioned, update to the latest:
```bash
GROQ_MODEL=llama-3.3-70b-versatile
```

## Next Steps

1. **Run the bot**: `tech-digest-bot`
2. **Monitor usage**: Check your [Groq dashboard](https://console.groq.com/)
3. **Optimize**: Experiment with different models for your use case

## Resources

- [Groq Console](https://console.groq.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [Groq Models](https://console.groq.com/docs/models)
- [Rate Limits](https://console.groq.com/docs/rate-limits)
