"""Application-wide constants and default values."""

# Groq LLM Configuration
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_GROQ_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_TEMPERATURE = 0.7

# Embedding Configuration (HuggingFace)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIMENSION = 384

# Neo4j Configuration
DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_DATABASE = "neo4j"

# Search Configuration
MAX_SEARCH_RESULTS = 5
MAX_BM25_RESULTS = 5
MIN_BM25_SCORE_THRESHOLD = 1.5

# Graph Configuration
RRF_K_CONSTANT = 60  # Reciprocal Rank Fusion constant
DEFAULT_VECTOR_WEIGHT = 0.5
DEFAULT_BM25_WEIGHT = 0.5
MAX_TOPIC_EXTRACTION = 10
MIN_TOPIC_LENGTH = 2

# LLM Token Limits
MAX_DIGEST_TOKENS = 800
MAX_ANSWER_TOKENS = 500
MAX_GENERATION_TOKENS = 200

# Content Limits
TOPIC_EXTRACTION_CONTENT_LIMIT = 1500
SNIPPET_LENGTH = 200

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
