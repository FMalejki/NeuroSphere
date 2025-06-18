"""
User models module for the NeuroSphere application.
This module defines Pydantic models for user-related operations including creation,
authentication, and data representation.
"""
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom type for handling MongoDB ObjectId fields in Pydantic models.
    Provides validation and serialization methods for ObjectId fields.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):  # Added `field` argument for Pydantic v2 compatibility
        """
        Validate that the input value is a valid ObjectId.
        
        Args:
            v: The value to validate
            field: Field information (required for Pydantic v2 compatibility)
            
        Returns:
            ObjectId: The validated ObjectId
            
        Raises:
            ValueError: If the provided value is not a valid ObjectId
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema


class UserCreate(BaseModel):
    """
    Model for user creation/registration with required fields.
    Used to validate user input during registration.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """
    Model for user login authentication with flexible identifier.
    Allows login with either username or email.
    """
    identifier: str  # Can be either email or username
    password: str


class UserOut(BaseModel):
    """
    Model for user data representation in API responses.
    Excludes sensitive information like passwords.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr

    class Config:
        """
        Configuration class for the UserOut model.
        Defines serialization behavior for MongoDB ObjectId.
        """
        validate_by_name = True  # Updated for Pydantic v2
        json_encoders = {ObjectId: str}
