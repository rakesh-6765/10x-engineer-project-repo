"""FastAPI routes for PromptLab."""

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import __version__
from app.models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    PromptPartialUpdate,
    Collection,
    CollectionCreate,
    PromptList,
    CollectionList,
    HealthResponse,
    get_current_time,
    PromptVersion,
    PromptVersionCreate,
    PromptVersionList,
    RollbackRequest,
)
from app.storage import storage
from app.utils import filter_prompts_by_collection, search_prompts, sort_prompts_by_date


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Normalize validation errors to HTTP 400 for API clients."""

    return JSONResponse(status_code=400, content={"detail": exc.errors()})


def _validate_collection(collection_id: Optional[str]):
    if collection_id:
        collection = storage.get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")


def _snapshot_prompt(prompt: Prompt, change_note: Optional[str] = None, source_version_id: Optional[str] = None):
    version = PromptVersion(
        prompt_id=prompt.id,
        title=prompt.title,
        content=prompt.content,
        description=prompt.description,
        collection_id=prompt.collection_id,
        change_note=change_note,
        author="system",
        source_version_id=source_version_id,
    )
    return storage.create_version(version)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return API health and version information.

    Returns:
        HealthResponse: Health status and API version number.
    """

    return HealthResponse(status="healthy", version=__version__)


@app.get("/prompts", response_model=PromptList)
def list_prompts(collection_id: Optional[str] = None, search: Optional[str] = None):
    """List prompts with optional collection and search filters.

    Args:
        collection_id: When provided, only include prompts from this collection.
        search: Optional case-insensitive term to match title or description.

    Returns:
        PromptList: Prompts sorted by newest first with total count.
    """

    prompts = storage.get_all_prompts()

    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)

    if search:
        prompts = search_prompts(prompts, search)

    prompts = sort_prompts_by_date(prompts, descending=True)
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a single prompt by id.

    Args:
        prompt_id: Identifier of the prompt to retrieve.

    Returns:
        Prompt: The requested prompt.

    Raises:
        HTTPException: When the prompt cannot be found.
    """

    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt.

    Args:
        prompt_data: Payload containing prompt fields.

    Returns:
        Prompt: Newly created prompt persisted in storage.

    Raises:
        HTTPException: If the referenced collection does not exist.
    """

    _validate_collection(prompt_data.collection_id)

    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Replace an existing prompt with new data.

    Args:
        prompt_id: Identifier of the prompt to update.
        prompt_data: Replacement prompt fields.

    Returns:
        Prompt: Updated prompt after persistence.

    Raises:
        HTTPException: If the prompt or referenced collection does not exist.
    """

    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    _validate_collection(prompt_data.collection_id)

    _snapshot_prompt(existing)

    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time(),
    )

    return storage.update_prompt(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPartialUpdate):
    """Partially update an existing prompt.

    Args:
        prompt_id: Identifier of the prompt to patch.
        prompt_data: Partial prompt fields to merge.

    Returns:
        Prompt: Updated prompt with merged fields.

    Raises:
        HTTPException: If the prompt or referenced collection does not exist.
    """

    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_fields = prompt_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "collection_id" in update_fields and update_fields["collection_id"]:
        _validate_collection(update_fields["collection_id"])

    _snapshot_prompt(existing)

    updated_data = existing.model_dump()
    updated_data.update(update_fields)

    updated_data["id"] = existing.id
    updated_data["created_at"] = existing.created_at
    updated_data["updated_at"] = get_current_time()

    updated_prompt = Prompt(**updated_data)
    return storage.update_prompt(prompt_id, updated_prompt)


@app.get("/prompts/{prompt_id}/versions", response_model=PromptVersionList)
def list_prompt_versions(
    prompt_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List versions for a prompt sorted newest first."""

    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    versions = storage.get_versions_for_prompt(prompt_id)
    versions = sorted(versions, key=lambda v: v.created_at, reverse=True)
    paginated = versions[offset : offset + limit]
    return PromptVersionList(versions=paginated, total=len(versions))


@app.get("/prompts/{prompt_id}/versions/{version_id}", response_model=PromptVersion)
def get_prompt_version(prompt_id: str, version_id: str):
    """Fetch a specific version for a prompt."""

    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    version = storage.get_version(version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")

    return version


@app.post("/prompts/{prompt_id}/versions", response_model=PromptVersion, status_code=201)
def create_prompt_version(prompt_id: str, version_data: PromptVersionCreate):
    """Manually create a new version and update the prompt to match it."""

    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    _validate_collection(version_data.collection_id)

    version = PromptVersion(
        prompt_id=prompt_id,
        title=version_data.title,
        content=version_data.content,
        description=version_data.description,
        collection_id=version_data.collection_id,
        change_note=version_data.change_note,
        author=version_data.author or "system",
    )
    stored_version = storage.create_version(version)

    updated_prompt = Prompt(
        id=prompt.id,
        title=version_data.title,
        content=version_data.content,
        description=version_data.description,
        collection_id=version_data.collection_id,
        created_at=prompt.created_at,
        updated_at=get_current_time(),
    )
    storage.update_prompt(prompt_id, updated_prompt)

    return stored_version


@app.post(
    "/prompts/{prompt_id}/versions/{version_id}/rollback",
    response_model=PromptVersion,
    status_code=201,
)
def rollback_prompt_version(prompt_id: str, version_id: str, payload: RollbackRequest):
    """Create a rollback version and update the prompt to the target state."""

    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    target_version = storage.get_version(version_id)
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")

    if target_version.prompt_id != prompt_id:
        raise HTTPException(status_code=400, detail="Version does not belong to this prompt")

    _validate_collection(target_version.collection_id)

    rollback_version = PromptVersion(
        prompt_id=prompt_id,
        title=target_version.title,
        content=target_version.content,
        description=target_version.description,
        collection_id=target_version.collection_id,
        change_note=payload.change_note,
        author=payload.author or "system",
        source_version_id=version_id,
    )
    stored_version = storage.create_version(rollback_version)

    updated_prompt = Prompt(
        id=prompt.id,
        title=target_version.title,
        content=target_version.content,
        description=target_version.description,
        collection_id=target_version.collection_id,
        created_at=prompt.created_at,
        updated_at=get_current_time(),
    )
    storage.update_prompt(prompt_id, updated_prompt)

    return stored_version


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Delete a prompt.

    Args:
        prompt_id: Identifier of the prompt to delete.

    Returns:
        None: Empty response body on success.

    Raises:
        HTTPException: If the prompt does not exist.
    """

    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


@app.get("/collections", response_model=CollectionList)
def list_collections():
    """List all prompt collections.

    Returns:
        CollectionList: Collections with total count.
    """

    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a collection by id.

    Args:
        collection_id: Identifier of the collection to fetch.

    Returns:
        Collection: The requested collection.

    Raises:
        HTTPException: When the collection is not found.
    """

    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new collection.

    Args:
        collection_data: Payload describing the collection.

    Returns:
        Collection: Newly created collection.
    """

    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection and detach associated prompts.

    Args:
        collection_id: Identifier of the collection to delete.

    Returns:
        None: Empty response body on success.

    Raises:
        HTTPException: If the collection does not exist.
    """

    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    prompts = storage.get_all_prompts()
    for prompt in prompts:
        if prompt.collection_id == collection_id:
            updated_data = prompt.model_dump()
            updated_data["collection_id"] = None
            updated_data["updated_at"] = get_current_time()
            updated_prompt = Prompt(**updated_data)
            storage.update_prompt(prompt.id, updated_prompt)

    storage.delete_collection(collection_id)
    return None