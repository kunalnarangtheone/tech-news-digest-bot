"""OpenClaw integration using CLI commands."""

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class OpenClawCLIClient:
    """Client for OpenClaw using CLI commands."""

    def __init__(self) -> None:
        """Initialize OpenClaw CLI client."""
        self.enabled = False

    async def check_availability(self) -> bool:
        """
        Check if OpenClaw CLI is available.

        Returns:
            True if OpenClaw is installed and running
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "openclaw",
                "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                output = stdout.decode()
                # Check if gateway is actually running
                if "running" in output.lower():
                    self.enabled = True
                    logger.info("OpenClaw Gateway is running")
                    return True
                else:
                    logger.warning(
                        "OpenClaw installed but gateway not running"
                    )
                    self.enabled = False
                    return False
            else:
                logger.warning("OpenClaw not available: %s", stderr.decode())
                self.enabled = False
                return False

        except FileNotFoundError:
            logger.warning("OpenClaw CLI not found")
            self.enabled = False
            return False
        except Exception as e:
            logger.error("Error checking OpenClaw: %s", e)
            self.enabled = False
            return False

    async def ask_agent(
        self,
        message: str,
        timeout: int = 60,
        session_id: str = "tech-digest-bot",
    ) -> dict[str, Any]:
        """
        Ask OpenClaw agent a question using local embedded mode.

        Args:
            message: Message to send to the agent
            timeout: Command timeout in seconds
            session_id: Session ID for conversation continuity

        Returns:
            Dict with 'success', 'response', and optional 'error'
        """
        try:
            # Use local embedded mode for faster responses
            proc = await asyncio.create_subprocess_exec(
                "openclaw",
                "agent",
                "--local",
                "--message",
                message,
                "--session-id",
                session_id,
                "--timeout",
                str(timeout),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout + 5
                )
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning("OpenClaw agent timeout")
                return {"success": False, "error": "Request timeout"}

            if proc.returncode == 0:
                output = stdout.decode().strip()
                try:
                    # Parse JSON response
                    result = json.loads(output)
                    response_text = result.get("response", "")

                    logger.info(
                        "OpenClaw response received (%d chars)",
                        len(response_text),
                    )
                    return {
                        "success": True,
                        "response": response_text,
                        "data": result,
                    }
                except json.JSONDecodeError:
                    # Fallback to plain text if not JSON
                    logger.warning(
                        "OpenClaw response not valid JSON, "
                        "using as plain text"
                    )
                    return {"success": True, "response": output}
            else:
                error_msg = stderr.decode().strip()
                logger.error("OpenClaw agent error: %s", error_msg)
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error("Error calling OpenClaw agent: %s", e)
            return {"success": False, "error": str(e)}

    async def get_tech_news_context(self, topic: str) -> str:
        """
        Get tech news context from OpenClaw agent.

        Args:
            topic: Topic to research

        Returns:
            Context string with tech news information
        """
        query = f"""Search for current information about {topic} including:
- Recent HackerNews discussions
- Trending GitHub repositories
- Dev.to articles
- Latest developments and news

Provide factual, up-to-date information with sources."""

        result = await self.ask_agent(query, timeout=60)

        if result.get("success"):
            return result.get("response", "")
        else:
            logger.warning(
                "OpenClaw agent failed: %s",
                result.get("error", "Unknown error"),
            )
            return ""
