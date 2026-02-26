"""Pydantic models for PromptLab."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique identifier for persisted objects.

    Returns:
        str: UUID4 as a string.
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Return the current UTC timestamp.

    Returns:
        datetime: Current UTC time.
    """
    return datetime.utcnow()


# ============== Prompt Models ==============


class PromptBase(BaseModel):
    """Shared fields for prompt creation and updates.

    Attributes:
        title: Human readable title for the prompt.
        content: Prompt text that may include template variables.
        description: Optional summary of the prompt's purpose.
        collection_id: Optional identifier for the parent collection.
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class PromptCreate(PromptBase):
    """Payload model for creating prompts."""


class PromptUpdate(PromptBase):
    """Payload model for updating prompts."""


class PromptPartialUpdate(BaseModel):
    """Payload model for partially updating prompts."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class Prompt(PromptBase):
    """Full prompt model used in storage and responses.

    Attributes:
        id: Unique prompt identifier.
        created_at: Timestamp when the prompt was created.
        updated_at: Timestamp when the prompt was last modified.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    model_config = ConfigDict(from_attributes=True)


# ============== Collection Models ==============


class CollectionBase(BaseModel):
    """Shared fields for collection creation and updates.

    Attributes:
        name: Collection display name.
        description: Optional description of the collection purpose.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Payload model for creating collections."""


class Collection(CollectionBase):
    """Full collection model used in storage and responses.

    Attributes:
        id: Unique collection identifier.
        created_at: Timestamp when the collection was created.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    model_config = ConfigDict(from_attributes=True)


# ============== Response Models ==============


class PromptList(BaseModel):
    """Response wrapper for prompt collections.

    Attributes:
        prompts: List of prompts returned from an API request.
        total: Count of prompts in the response.
    """

    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Response wrapper for collection collections.

    Attributes:
        collections: List of collections returned from an API request.
        total: Count of collections in the response.
    """

    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Response model for health checks.

    Attributes:
        status: Indicates service health.
        version: Current API version string.
    """

    status: str
    version: str


# ============== Version Models ==============


class PromptVersionBase(BaseModel):
    """Shared fields for prompt version payloads."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    change_note: Optional[str] = Field(None, max_length=280)
    author: Optional[str] = Field(default="system", min_length=1, max_length=100)


class PromptVersionCreate(PromptVersionBase):
    """Payload model for manually creating prompt versions."""


class PromptVersion(PromptVersionBase):
    """Stored representation of a prompt version."""

    id: str = Field(default_factory=generate_id)
    prompt_id: str
    created_at: datetime = Field(default_factory=get_current_time)
    source_version_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PromptVersionList(BaseModel):
    """Response wrapper for collections of prompt versions."""

    versions: List[PromptVersion]
    total: int


class RollbackRequest(BaseModel):
    """Payload for rollback operations."""

    change_note: Optional[str] = Field(None, max_length=280)
    author: Optional[str] = Field(default="system", min_length=1, max_length=100)
