from marshmallow import Schema, fields

from src.schemas import PaginationRequestSchema, PaginationResponseSchema


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    user_id = fields.Int(dump_only=True)
    archived = fields.Int()
    content = fields.Str()
    category_id = fields.Int(allow_none=True)
    deleted_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UpdateNoteSchema(Schema):
    title = fields.Str()
    archived = fields.Int()
    content = fields.Str()
    category_id = fields.Int(allow_none=True)


class FetchNotesResponseSchema(PaginationResponseSchema):
    data = fields.Nested(NoteSchema, many=True)


class FetchNotesRequestSchema(PaginationRequestSchema):
    title = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
