"""Utility functions for PromptLab."""

from typing import List
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date.

    Args:
        prompts: Prompts to sort.
        descending: Whether to return newest prompts first.

    Returns:
        List[Prompt]: Prompts ordered by ``created_at``.
    """
    return sorted(prompts, key=lambda prompt: prompt.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Return prompts that belong to a specific collection.

    Args:
        prompts: Prompts to filter.
        collection_id: Identifier of the target collection.

    Returns:
        List[Prompt]: Prompts linked to the given collection.
    """
    return [prompt for prompt in prompts if prompt.collection_id == collection_id]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """Search prompts by title or description.

    Args:
        prompts: Prompts to search within.
        query: Case-insensitive term to match.

    Returns:
        List[Prompt]: Prompts whose title or description contains the query.
    """
    query_lower = query.lower()
    return [
        prompt
        for prompt in prompts
        if query_lower in prompt.title.lower()
        or (prompt.description and query_lower in prompt.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Check whether prompt text meets basic quality rules.

    Args:
        content: Prompt text to validate.

    Returns:
        bool: True when content is non-empty and at least 10 characters.
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """Extract template variables in ``{{variable}}`` format.

    Args:
        content: Prompt body that may contain template variables.

    Returns:
        List[str]: Variable names discovered in the content.
    """
    import re

    pattern = r"\{\{(\w+)\}\}"
    return re.findall(pattern, content)
