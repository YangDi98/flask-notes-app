from marshmallow import Schema, fields, validate, pre_load, ValidationError
from flask_babel import gettext

from src.schemas.auth import get_field_names


class UpdateUserSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    preferred_language = fields.Str(
        validate=validate.OneOf(["en_CA", "zh_CN"])
    )

    @pre_load
    def process_input(self, data, **kwargs):
        fields = ["first_name", "last_name"]
        for field in fields:
            if field in data:
                data[field] = data.get(field, "").strip()
                if not data[field]:
                    field_names = get_field_names()
                    raise ValidationError(
                        gettext(
                            "%(field)s %(field_name)s "
                            "cannot be empty or just spaces",
                            field=field_names.get(field, field),
                            field_name=field,
                        )
                    )
        return data


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    active = fields.Bool(dump_only=True)
    email = fields.Email(dump_only=True)
    preferred_language = fields.Str()
    active = fields.Bool(dump_only=True)
