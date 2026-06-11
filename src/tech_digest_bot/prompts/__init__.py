"""Prompt management utilities."""

from pathlib import Path
from typing import Any

import yaml


def load_prompt(prompt_name: str) -> tuple[str, dict[str, Any]]:
    """
    Load a prompt from a .prompt.md file.

    Args:
        prompt_name: Name of the prompt file (without .prompt.md extension)

    Returns:
        Tuple of (prompt_content, metadata_dict)
    """
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{prompt_name}.prompt.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    content = prompt_file.read_text()

    # Parse YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            prompt_content = parts[2].strip()
            return prompt_content, metadata

    # No frontmatter
    return content.strip(), {}


def get_prompt(prompt_name: str) -> str:
    """
    Get prompt content only (convenience method).

    Args:
        prompt_name: Name of the prompt file (without .prompt.md extension)

    Returns:
        Prompt content as string
    """
    content, _ = load_prompt(prompt_name)
    return content
