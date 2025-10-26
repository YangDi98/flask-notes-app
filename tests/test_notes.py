from http import HTTPStatus

from src.models.notes import Note
from src.models.users import User


class TestGetNotes:
    def test_get_notes_with_pagination(self, test_user, authenticated_client):
        decoy_user = User.create(
            {
                "first_name": "decoy",
                "last_name": "user",
                "email": "decoy@example.com",
            }
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
        assert response.json["next"] is None
