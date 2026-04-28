"""Prompt template loader using Jinja2."""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Get templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Create Jinja2 environment
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_prompt(template_name: str, **context) -> str:
    """
    Render a prompt template with context.

    Args:
        template_name: Name of template file (e.g., "digest_generation.jinja2")
        **context: Template variables

    Returns:
        Rendered prompt string
    """
    template = _env.get_template(template_name)
    return template.render(**context)


def render_digest_prompt(topic: str, context: str) -> str:
    """Render digest generation prompt."""
    return render_prompt("digest_generation.jinja2", topic=topic, context=context)


def render_followup_prompt(question: str, history: list[dict]) -> str:
    """Render follow-up question prompt."""
    return render_prompt("followup_answer.jinja2", question=question, history=history)


def render_topic_extraction_prompt(title: str, content: str) -> str:
    """Render topic extraction prompt."""
    return render_prompt("topic_extraction.jinja2", title=title, content=content)


def render_agent_system_prompt() -> str:
    """Render agent system prompt."""
    return render_prompt("agent_system.jinja2")


def render_agent_synthesis_prompt(query: str, context: str) -> str:
    """Render agent synthesis prompt."""
    return render_prompt("agent_synthesis.jinja2", query=query, context=context)
