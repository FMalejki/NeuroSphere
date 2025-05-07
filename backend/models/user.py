from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId  # Correct import from bson

# Helper class for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):  # Added `field` argument for Pydantic v2 compatibility
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

# Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    identifier: str  # Can be either email or username
    password: str

class UserOut(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr

    class Config:
        validate_by_name = True  # Updated for Pydantic v2
        json_encoders = {ObjectId: str}
