from marshmallow import Schema, fields

from src.schemas import PaginationRequestSchema, PaginationResponseSchema


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str()
    deleted_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class FetchNotesResponseSchema(PaginationResponseSchema):
    data = fields.Nested(NoteSchema, many=True)


class FetchNotesRequestSchema(PaginationRequestSchema):
    title = fields.Str()
