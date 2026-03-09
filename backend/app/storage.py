"""In-memory storage for PromptLab.

This module provides simple in-memory storage for prompts and collections.
In production deployments, replace this with a persistent database-backed
implementation.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection, PromptVersion


class Storage:
    """Lightweight storage adapter that mimics persistence.

    Attributes:
        _prompts: Mapping of prompt ids to ``Prompt`` objects.
        _collections: Mapping of collection ids to ``Collection`` objects.
    """

    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
        self._versions: Dict[str, PromptVersion] = {}

    # ============== Prompt Operations ==============

    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Persist a new prompt instance.

        Args:
            prompt: Prompt to store.

        Returns:
            Prompt: The stored prompt.
        """
        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Fetch a prompt by identifier.

        Args:
            prompt_id: Unique prompt identifier.

        Returns:
            Optional[Prompt]: The prompt if found, otherwise ``None``.
        """
        return self._prompts.get(prompt_id)

    def get_all_prompts(self) -> List[Prompt]:
        """Return every prompt currently stored.

        Returns:
            List[Prompt]: Collection of all prompts.
        """
        return list(self._prompts.values())

    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Replace an existing prompt with new data.

        Args:
            prompt_id: Identifier of the prompt to update.
            prompt: New prompt payload.

        Returns:
            Optional[Prompt]: Updated prompt when it exists, otherwise ``None``.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        """Remove a prompt from storage.

        Args:
            prompt_id: Identifier of the prompt to delete.

        Returns:
            bool: True if the prompt was deleted, False when missing.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False

    # ============== Version Operations ==============

    def create_version(self, version: PromptVersion) -> PromptVersion:
        """Persist a new prompt version.

        Args:
            version: Version instance to store.

        Returns:
            PromptVersion: Stored version.
        """
        self._versions[version.id] = version
        return version

    def get_version(self, version_id: str) -> Optional[PromptVersion]:
        """Fetch a version by identifier."""

        return self._versions.get(version_id)

    def get_versions_for_prompt(self, prompt_id: str) -> List[PromptVersion]:
        """Return versions associated with a prompt."""

        return [version for version in self._versions.values() if version.prompt_id == prompt_id]

    # ============== Collection Operations ==============

    def create_collection(self, collection: Collection) -> Collection:
        """Persist a new collection.

        Args:
            collection: Collection to store.

        Returns:
            Collection: Stored collection instance.
        """
        self._collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Fetch a collection by identifier.

        Args:
            collection_id: Unique collection identifier.

        Returns:
            Optional[Collection]: The collection if found, otherwise ``None``.
        """
        return self._collections.get(collection_id)

    def get_all_collections(self) -> List[Collection]:
        """Return all stored collections.

        Returns:
            List[Collection]: Every collection in storage.
        """
        return list(self._collections.values())

    def update_collection(self, collection_id: str, collection: Collection) -> Optional[Collection]:
        """Replace an existing collection with new data.

        Args:
            collection_id: Identifier of the collection to update.
            collection: New collection payload.

        Returns:
            Optional[Collection]: Updated collection when found, otherwise ``None``.
        """
        if collection_id not in self._collections:
            return None
        self._collections[collection_id] = collection
        return collection

    def delete_collection(self, collection_id: str) -> bool:
        """Remove a collection from storage.

        Args:
            collection_id: Identifier of the collection to delete.

        Returns:
            bool: True if deletion occurred, False when missing.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False

    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Return prompts assigned to a collection.

        Args:
            collection_id: Target collection identifier.

        Returns:
            List[Prompt]: Prompts whose ``collection_id`` matches the input.
        """
        return [prompt for prompt in self._prompts.values() if prompt.collection_id == collection_id]

    # ============== Utility ==============

    def clear(self):
        """Reset storage by clearing prompts and collections."""
        self._prompts.clear()
        self._collections.clear()
        self._versions.clear()


# Global storage instance
storage = Storage()
