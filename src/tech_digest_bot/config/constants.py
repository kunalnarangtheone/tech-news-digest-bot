"""Application-wide constants and default values."""

# Groq LLM Configuration
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_GROQ_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_TEMPERATURE = 0.7

# Search Configuration
MAX_SEARCH_RESULTS = 5

# LLM Token Limits
MAX_DIGEST_TOKENS = 800
MAX_ANSWER_TOKENS = 500
MAX_GENERATION_TOKENS = 200

# Content Limits

# Conversation Management
MAX_CONVERSATION_HISTORY = 10
MAX_FOLLOWUP_CONTEXT_MESSAGES = 6

# Agent Configuration
AGENT_NUM_CTX = 8192
AGENT_TEMPERATURE = 0.7
AGENT_ANSWER_MIN_WORDS = 200
AGENT_ANSWER_MAX_WORDS = 300

# Digest Generation
DIGEST_MIN_WORDS = 200
DIGEST_MAX_WORDS = 300

# Query Limits
DEFAULT_QUERY_LIMIT = 10
RELATED_TOPICS_LIMIT = 10
RECENT_ARTICLES_LIMIT = 10

# Data Retention
CONVERSATION_RETENTION_DAYS = 30

# Stop Words for Query Processing
STOP_WORDS = {
    'what', 'is', 'are', 'the', 'a', 'an', 'how',
    'does', 'do', 'can', 'tell', 'me', 'about'
}
