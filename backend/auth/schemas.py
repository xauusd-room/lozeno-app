from pydantic import BaseModel, Field, validator

class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @validator("email")
    def normalize_email(cls, value):
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@") or any(c.isspace() for c in value):
            raise ValueError("请输入有效的邮箱地址")
        return value

class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @validator("email")
    def normalize_email(cls, value):
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@") or any(c.isspace() for c in value):
            raise ValueError("请输入有效的邮箱地址")
        return value
