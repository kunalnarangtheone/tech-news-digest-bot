"""Entry point for running the API as a module: python -m tech_digest_bot"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "tech_digest_bot.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
