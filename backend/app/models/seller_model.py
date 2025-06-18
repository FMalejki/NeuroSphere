"""
Module containing Pydantic models for sellers in the NeuroSphere application.
These models define the structure for seller data validation and serialization.
"""
from typing import List, Optional
from pydantic import BaseModel
from app.models.product_model import Product


class OpinionS(BaseModel):
    """
    Model representing an opinion about a seller.
    Contains rating and optional content.
    """
    id: int
    rating: int
    content: Optional[str] = None


class SellerBase(BaseModel):
    """
    Base model with common seller attributes.
    Contains name and optional description.
    """
    name: str
    description: Optional[str] = None


class SellerCreate(SellerBase):
    """
    Model for creating a new seller.
    Extends SellerBase with products, opinions, and public key.
    """
    products: List[Product] = []
    opinions: List[OpinionS] = []
    public_key: str


class Seller(SellerBase):
    """
    Complete seller model including database ID.
    Used for responses and data retrieval.
    """
    id: int
    products: List[Product] = []
    opinions: List[OpinionS] = []
    public_key: str
