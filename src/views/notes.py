from flask_smorest import Blueprint
from flask import url_for, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required

from src.schemas.notes import (
    NoteSchema,
    FetchNotesResponseSchema,
    FetchNotesRequestSchema,
    UpdateNoteSchema,
)
from src.models.notes import Note
from src.models.categories import Category
from src.views.utils import user_access_required

note_blueprint = Blueprint(
    "note", __name__, url_prefix="/users/<int:user_id>/notes"
)


@note_blueprint.route("/", methods=["GET"])
@note_blueprint.arguments(FetchNotesRequestSchema, location="query")
@note_blueprint.response(200, FetchNotesResponseSchema)
@jwt_required()
@user_access_required
def get_notes(args, user_id):
    notes = Note.filter(user_id=user_id, **args)
    next_cursor = notes[-1].created_at if notes else None
    next_id = notes[-1].id if notes else None
    url = None
    if (next_cursor or next_id) and request.endpoint:
        url = url_for(
            request.endpoint,
            user_id=user_id,
            cursor_created_at=next_cursor,
            cursor_id=next_id,
            limit=args.get("limit", 100),
            _external=False,
        )
    return {"data": notes, "next": url}


@note_blueprint.route("/<int:note_id>", methods=["GET"])
@note_blueprint.response(200, NoteSchema)
@jwt_required()
@user_access_required
def get_note(user_id, note_id):
    return Note.find_note_by_user_and_id_or_404(user_id, note_id)


@note_blueprint.route("/", methods=["POST"])
@note_blueprint.arguments(NoteSchema, location="json")
@note_blueprint.response(201, NoteSchema)
@jwt_required()
@user_access_required
def create_note(json_data, user_id):
    if json_data.get("category_id"):
        Category.find_category_by_user_and_id_or_404(
            user_id, json_data["category_id"]
        )
    note = Note.create({**json_data, "user_id": user_id}, commit=True)
    return note


@note_blueprint.route("/<int:note_id>", methods=["PUT"])
@note_blueprint.arguments(UpdateNoteSchema, location="json")
@note_blueprint.response(200, NoteSchema)
@jwt_required()
@user_access_required
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
@jwt_required()
@user_access_required
def delete_note(user_id, note_id):
    note = Note.find_note_by_user_and_id_or_404(user_id, note_id)
    note.soft_delete(commit=True)
    return


@note_blueprint.route("/<int:note_id>/restore", methods=["POST"])
@note_blueprint.response(200, NoteSchema)
@jwt_required()
@user_access_required
def restore_note(user_id, note_id):
    note = Note.find_note_by_user_and_id_or_404(
        user_id, note_id, include_deleted=True
    )
    note.restore(commit=True)
    return note
