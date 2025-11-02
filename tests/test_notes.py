from http import HTTPStatus
from datetime import datetime, timedelta, timezone

from src.models.notes import Note
from src.models.users import User


class TestNotes:
    def test_get_notes_with_pagination(self, test_user, authenticated_client):
        decoy_user = User.create(
            {
                "first_name": "decoy",
                "last_name": "user",
                "email": "decoy@example.com",
            },
            commit=True,
        )
        Note.create(
            {
                "user_id": decoy_user.id,
                "title": "Decoy Note",
                "content": "This note should not "
                "appear in the test_user's notes.",
            }
        )
        for i in range(5):
            Note.create(
                {
                    "user_id": test_user.id,
                    "title": f"Note {i+1}",
                    "content": f"Content for note {i+1}",
                }
            )
        response = authenticated_client.get(f"/users/{test_user.id}/notes/")

        assert response.status_code == HTTPStatus.OK
        assert len(response.json["data"]) == 5
        assert response.json["data"][0]["title"] == "Note 5"
        assert response.json["data"][-1]["title"] == "Note 1"
        expected_datetime = response.json["data"][-1]["created_at"].replace(
            "T", "+"
        )
        assert (
            response.json["next"]
            == f"/users/{test_user.id}/notes/?cursor_created_at="
            f"{expected_datetime}&cursor_id="
            f'{response.json["data"][-1]["id"]}&limit=100'
        )
        response = authenticated_client.get(response.json["next"])
        assert response.status_code == HTTPStatus.OK
        assert len(response.json["data"]) == 0
        assert response.json["next"] is None

    def test_get_notes_with_pagination_limit(
        self, test_user, authenticated_client
    ):
        for i in range(3):
            Note.create(
                {
                    "user_id": test_user.id,
                    "title": f"Note {i+1}",
                    "content": f"Content for note {i+1}",
                }
            )
        first_response = authenticated_client.get(
            f"/users/{test_user.id}/notes/?limit=2"
        )
        assert first_response.status_code == HTTPStatus.OK
        assert len(first_response.json["data"]) == 2

        next_url = first_response.json["next"]
        second_response = authenticated_client.get(next_url)
        assert second_response.status_code == HTTPStatus.OK
        assert len(second_response.json["data"]) == 1

    def test_get_notes_filter_date_range(
        self, test_user, authenticated_client, db_session
    ):
        now = datetime.now(timezone.utc)
        dates = [
            now - timedelta(days=10),
            now - timedelta(days=5),
            now,
        ]
        for i, note_date in enumerate(dates):
            Note.create(
                {
                    "user_id": test_user.id,
                    "title": f"Note {i+1}",
                    "content": f"Content for note {i+1}",
                    "created_at": note_date,
                },
                commit=False,
            )
        db_session.session.commit()

        start_date = (now - timedelta(days=7)).isoformat() + "Z"
        end_date = now.isoformat() + "Z"
        response = authenticated_client.get(
            f"/users/{test_user.id}/notes/?start_date="
            f"{start_date}&end_date={end_date}"
        )

        assert response.status_code == HTTPStatus.OK
        assert len(response.json["data"]) == 2
        titles = [note["title"] for note in response.json["data"]]
        assert "Note 2" in titles
        assert "Note 3" in titles

    def test_get_notes_filter_title(self, test_user, authenticated_client):
        Note.create(
            {
                "user_id": test_user.id,
                "title": "Shopping List",
                "content": "Buy milk, eggs, and bread.",
            }
        )
        Note.create(
            {
                "user_id": test_user.id,
                "title": "Work Tasks",
                "content": "Finish the report and email it to the team.",
            }
        )

        response = authenticated_client.get(
            f"/users/{test_user.id}/notes/?title=shop"
        )

        assert response.status_code == HTTPStatus.OK
        assert len(response.json["data"]) == 1
        assert response.json["data"][0]["title"] == "Shopping List"

    def test_get_notes_unauthorized_access(
        self, test_user, authenticated_client
    ):
        other_user = User.create(
            {
                "first_name": "other",
                "last_name": "user",
                "email": "other@example.com",
            },
            commit=True,
        )
        response = authenticated_client.get(f"/users/{other_user.id}/notes/")
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert (
            response.json["message"]
            == "You do not have permission to access this resource."
        )

    def test_get_note(self, test_user, authenticated_client):
        note = Note.create(
            {
                "user_id": test_user.id,
                "title": "Sample Note",
                "content": "This is a sample note.",
            },
            commit=True,
        )
        response = authenticated_client.get(
            f"/users/{test_user.id}/notes/{note.id}"
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json["title"] == "Sample Note"
        assert response.json["content"] == "This is a sample note."

    def test_get_note_not_found(self, test_user, authenticated_client):
        response = authenticated_client.get(
            f"/users/{test_user.id}/notes/9999"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert (
            response.json["message"] == "The requested resource was not found."
        )

    def test_get_note_unauthorized_access(
        self, test_user, authenticated_client
    ):
        other_user = User.create(
            {
                "first_name": "other",
                "last_name": "user",
                "email": "other@example.com",
            },
            commit=True,
        )
        response = authenticated_client.get(f"/users/{other_user.id}/notes/")
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert (
            response.json["message"]
            == "You do not have permission to access this resource."
        )

    def test_create_note(self, test_user, authenticated_client):
        note_data = {
            "title": "New Note",
            "content": "Content of the new note.",
        }
        response = authenticated_client.post(
            f"/users/{test_user.id}/notes/", json=note_data
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.json["title"] == "New Note"
        assert response.json["content"] == "Content of the new note."

    def test_update_note(self, test_user, authenticated_client):
        note = Note.create(
            {
                "user_id": test_user.id,
                "title": "Old Title",
                "content": "Old content.",
            },
            commit=True,
        )
        update_data = {
            "title": "Updated Title",
            "content": "Updated content.",
        }
        response = authenticated_client.put(
            f"/users/{test_user.id}/notes/{note.id}", json=update_data
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json["title"] == "Updated Title"
        assert response.json["content"] == "Updated content."

    def test_delete_note(self, test_user, authenticated_client):
        note = Note.create(
            {
                "user_id": test_user.id,
                "title": "Note to be deleted",
                "content": "This note will be deleted.",
            },
            commit=True,
        )
        response = authenticated_client.delete(
            f"/users/{test_user.id}/notes/{note.id}"
        )
        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verify the note is deleted
        get_response = authenticated_client.get(
            f"/users/{test_user.id}/notes/{note.id}"
        )
        assert get_response.status_code == HTTPStatus.NOT_FOUND
