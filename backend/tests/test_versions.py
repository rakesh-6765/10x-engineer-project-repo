"""Tests for prompt versioning endpoints and behaviors."""

from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient


def _create_prompt(client: TestClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = client.post("/prompts", json=payload)
    assert response.status_code == 201
    return response.json()


def _get_versions(client: TestClient, prompt_id: str):
    response = client.get(f"/prompts/{prompt_id}/versions")
    return response


class TestVersionListing:
    def test_versions_require_prompt(self, client: TestClient):
        response = client.get("/prompts/missing/versions")
        assert response.status_code == 404

    def test_versions_empty_when_none(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)
        response = _get_versions(client, prompt["id"])
        assert response.status_code == 200
        data = response.json()
        assert data["versions"] == []
        assert data["total"] == 0


class TestAutomaticVersioning:
    def test_put_creates_snapshot(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)

        updated_payload = {
            "title": "Updated Title",
            "content": "Updated prompt content that is long enough",
            "description": "Updated description",
        }

        put_response = client.put(f"/prompts/{prompt['id']}", json=updated_payload)
        assert put_response.status_code == 200

        versions_response = _get_versions(client, prompt["id"])
        assert versions_response.status_code == 200
        versions = versions_response.json()["versions"]
        assert len(versions) == 1
        version = versions[0]
        assert version["prompt_id"] == prompt["id"]
        assert version["title"] == sample_prompt_data["title"]
        assert version["content"] == sample_prompt_data["content"]
        assert version["description"] == sample_prompt_data["description"]
        assert version["author"] == "system"
        assert version["source_version_id"] is None

        current_prompt = client.get(f"/prompts/{prompt['id']}").json()
        assert current_prompt["title"] == updated_payload["title"]
        assert current_prompt["content"] == updated_payload["content"]

    def test_patch_creates_snapshot(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)

        patch_payload = {"description": "Patched description"}
        patch_response = client.patch(f"/prompts/{prompt['id']}", json=patch_payload)
        assert patch_response.status_code == 200

        versions = _get_versions(client, prompt["id"]).json()["versions"]
        assert len(versions) == 1
        assert versions[0]["description"] == sample_prompt_data["description"]
        assert versions[0]["title"] == sample_prompt_data["title"]
        assert versions[0]["content"] == sample_prompt_data["content"]


class TestManualVersioning:
    def test_create_version_updates_prompt(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)

        new_version_payload = {
            "title": "Versioned Title",
            "content": "Versioned prompt content",
            "description": "Manual version description",
            "change_note": "Expanded details",
            "author": "tester",
        }

        response = client.post(f"/prompts/{prompt['id']}/versions", json=new_version_payload)
        assert response.status_code == 201
        version = response.json()
        assert version["author"] == "tester"
        assert version["change_note"] == "Expanded details"

        current_prompt = client.get(f"/prompts/{prompt['id']}").json()
        assert current_prompt["title"] == new_version_payload["title"]
        assert current_prompt["content"] == new_version_payload["content"]
        assert current_prompt["description"] == new_version_payload["description"]

    def test_change_note_validation(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)
        too_long = "x" * 281
        payload = {
            "title": "New Title",
            "content": "New content for validation",
            "description": "desc",
            "change_note": too_long,
        }

        response = client.post(f"/prompts/{prompt['id']}/versions", json=payload)
        assert response.status_code == 400


class TestRollback:
    def test_rollback_updates_prompt_and_creates_version(self, client: TestClient, sample_prompt_data):
        prompt = _create_prompt(client, sample_prompt_data)

        update_payload = {
            "title": "Current title",
            "content": "Current prompt content that is longer",
            "description": "Current description",
        }
        client.put(f"/prompts/{prompt['id']}", json=update_payload)

        versions = _get_versions(client, prompt["id"]).json()["versions"]
        assert len(versions) == 1
        original_version_id = versions[0]["id"]

        rollback_response = client.post(
            f"/prompts/{prompt['id']}/versions/{original_version_id}/rollback",
            json={"change_note": "Rollback to original"},
        )
        assert rollback_response.status_code == 201
        rollback_version = rollback_response.json()
        assert rollback_version["source_version_id"] == original_version_id

        current_prompt = client.get(f"/prompts/{prompt['id']}").json()
        assert current_prompt["title"] == sample_prompt_data["title"]
        assert current_prompt["content"] == sample_prompt_data["content"]

        all_versions = _get_versions(client, prompt["id"]).json()["versions"]
        assert len(all_versions) == 2

    def test_rollback_rejects_foreign_version(self, client: TestClient, sample_prompt_data):
        prompt_a = _create_prompt(client, sample_prompt_data)
        prompt_b = _create_prompt(
            client,
            {
                "title": "Another",
                "content": "Another prompt content",
                "description": "Another prompt desc",
            },
        )

        client.patch(f"/prompts/{prompt_a['id']}", json={"description": "change"})
        version_id = _get_versions(client, prompt_a["id"]).json()["versions"][0]["id"]

        response = client.post(
            f"/prompts/{prompt_b['id']}/versions/{version_id}/rollback",
            json={},
        )
        assert response.status_code == 400
