from flask_smorest import Blueprint
from flask import url_for
from http import HTTPStatus

from src.notes.schemas import (
    NoteSchema,
    FetchNotesResponseSchema,
    FetchNotesRequestSchema,
)
from src.notes.models import Note
from src.users.models import User
from src.extensions import db

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
    User.get_or_404(user_id)
    return Note.get_or_404(note_id)


@note_blueprint.route("/", methods=["POST"])
@note_blueprint.arguments(NoteSchema, location="json")
@note_blueprint.response(201, NoteSchema)
def create_note(json_data, user_id):
    User.get_or_404(user_id)
    note = Note(**json_data)
    db.session.add(note)
    db.session.commit()
    return note


@note_blueprint.route("/<int:note_id>", methods=["PUT"])
@note_blueprint.arguments(NoteSchema, location="json")
@note_blueprint.response(200, NoteSchema)
def update_note(json_data, user_id, note_id):
    User.get_or_404(user_id)
    note = Note.get_or_404(note_id)
    if "title" in json_data:
        note.title = json_data["title"]
    if "content" in json_data:
        note.content = json_data["content"]
    db.session.commit()
    return note


@note_blueprint.route("/<int:note_id>", methods=["DELETE"])
@note_blueprint.response(HTTPStatus.NO_CONTENT)
def delete_note(user_id, note_id):
    User.get_or_404(user_id)
    note = Note.get_or_404(note_id)
    note.soft_delete(commit=True)
    return
