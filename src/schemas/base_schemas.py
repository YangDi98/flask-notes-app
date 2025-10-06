from marshmallow import Schema, fields, validate


class PaginationRequestSchema(Schema):
    limit = fields.Int(
        validate=validate.Range(min=1, max=500), load_default=100
    )
    cursor_created_at = fields.DateTime()
    cursor_id = fields.Int()


class PaginationResponseSchema(Schema):
    next = fields.Str()
