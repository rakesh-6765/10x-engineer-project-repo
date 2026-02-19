"""FastAPI routes for PromptLab."""

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    Collection,
    CollectionCreate,
    PromptList,
    CollectionList,
    HealthResponse,
    get_current_time,
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

    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

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

    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

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
def patch_prompt(prompt_id: str, prompt_data: PromptUpdate):
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

    if "collection_id" in update_fields and update_fields["collection_id"]:
        collection = storage.get_collection(update_fields["collection_id"])
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    updated_data = existing.model_dump()
    updated_data.update(update_fields)

    updated_data["id"] = existing.id
    updated_data["created_at"] = existing.created_at
    updated_data["updated_at"] = get_current_time()

    updated_prompt = Prompt(**updated_data)
    return storage.update_prompt(prompt_id, updated_prompt)


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