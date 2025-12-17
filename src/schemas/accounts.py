from pydantic import BaseModel, EmailStr


class BaseEmailPasswordSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "from_attributes": True
    }


class UserRegistrationRequestSchema(BaseEmailPasswordSchema):
    pass
