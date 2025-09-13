from marshmallow import Schema, fields, validate
from src.notes.schemas import NoteSchema


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    color = fields.Str(allow_none=True)
    user_id = fields.Int(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    notes = fields.Nested(
        NoteSchema, only=["id", "title"], many=True, dump_only=True
    )
