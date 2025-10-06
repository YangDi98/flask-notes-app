from flask_smorest import Blueprint
from flask import url_for
from http import HTTPStatus

from src.schemas.notes import (
    NoteSchema,
    FetchNotesResponseSchema,
    FetchNotesRequestSchema,
    UpdateNoteSchema,
)
from src.models.notes import Note
from src.models.users import User
from src.models.categories import Category

note_blueprint = Blueprint(
    "note", __name__, url_prefix="/users/<int:user_id>/notes"
)


@note_blueprint.route("/", methods=["GET"])
@note_blueprint.arguments(FetchNotesRequestSchema, location="query")
@note_blueprint.response(200, FetchNotesResponseSchema)
def get_notes(args, user_id):
    User.get_or_404(user_id)
    notes = Note.filter(user_id=user_id, **args)
    next_cursor = notes[-1].created_at if notes else None
    next_id = notes[-1].id if notes else None
    url = (
        url_for(
            "note.get_notes",
            user_id=user_id,
            cursor_created_at=next_cursor,
            cursor_id=next_id,
            limit=args.get("limit", 100),
            _external=False,
        )
        if next_cursor or next_id
        else None
    )
    return {"data": notes, "next": url}


@note_blueprint.route("/<int:note_id>", methods=["GET"])
@note_blueprint.response(200, NoteSchema)
def get_note(user_id, note_id):
    return Note.find_note_by_user_and_id_or_404(user_id, note_id)


@note_blueprint.route("/", methods=["POST"])
@note_blueprint.arguments(NoteSchema, location="json")
@note_blueprint.response(201, NoteSchema)
def create_note(json_data, user_id):
    # All need to validate identity of user
    User.get_or_404(user_id)
    if json_data.get("category_id"):
        Category.find_category_by_user_and_id_or_404(
            user_id, json_data["category_id"]
        )
    note = Note.create({**json_data, "user_id": user_id}, commit=True)
    return note


@note_blueprint.route("/<int:note_id>", methods=["PUT"])
@note_blueprint.arguments(UpdateNoteSchema, location="json")
@note_blueprint.response(200, NoteSchema)
def update_note(json_data, user_id, note_id):
    if json_data.get("category_id"):
        Category.find_category_by_user_and_id_or_404(
            user_id, json_data["category_id"]
        )
    note = Note.find_note_by_user_and_id_or_404(user_id, note_id)
    note.update(json_data, commit=True)
    return note


@note_blueprint.route("/<int:note_id>", methods=["DELETE"])
@note_blueprint.response(HTTPStatus.NO_CONTENT)
def delete_note(user_id, note_id):
    note = Note.find_note_by_user_and_id_or_404(user_id, note_id)
    note.soft_delete(commit=True)
    return


@note_blueprint.route("/<int:note_id>/restore", methods=["POST"])
@note_blueprint.response(200, NoteSchema)
def restore_note(user_id, note_id):
    note = Note.find_note_by_user_and_id_or_404(
        user_id, note_id, include_deleted=True
    )
    note.restore(commit=True)
    return note
