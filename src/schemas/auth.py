from marshmallow import Schema, fields, validate, pre_load, ValidationError

import re


def validate_password(password: str):
    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%])[A-Za-z\d@$#%]{9,}$"
    pat = re.compile(reg)

    mat = re.search(pat, password)

    # Have at least one number
    # Have at least one uppercase letter
    # Have at least one lowercase letter
    # Have at least one special character

    if not mat:
        raise ValidationError("Invalid Password")


class RegisterSchema(Schema):
    first_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    last_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, validate=validate.Length(min=9, max=128)
    )

    @pre_load
    def process_input(self, data, **kwargs):
        fields = ["email", "first_name", "last_name"]
        for field in fields:
            data[field] = data.get(field, "").strip()
            if not data[field]:
                raise ValidationError(
                    f"{field.replace('_', ' ').title()} "
                    f"cannot be empty or just spaces"
                )
        data["email"] = data["email"].lower()
        reg_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        pat_email = re.compile(reg_email)
        mat_email = re.search(pat_email, data["email"])
        if not mat_email:
            raise ValidationError("Invalid Email Address")
        validate_password(data["password"])
        return data


class UpdatePasswordSchema(Schema):
    password = fields.Str(
        required=True, validate=validate.Length(min=9, max=128)
    )
    new_password = fields.Str(
        required=True, validate=validate.Length(min=9, max=128)
    )

    @pre_load
    def process_input(self, data, **kwargs):
        validate_password(data["new_password"])
        return data


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    active = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
