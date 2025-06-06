"""Product data models for the NeuroSphere application."""
from typing import Optional
from pydantic import BaseModel


class Opinion(BaseModel):
    """Data model representing user opinions/reviews for products."""
    id: int
    rating: int
    content: Optional[str] = None


class Product(BaseModel):
    """Data model representing product information."""
    id: int
    title: str
    price: float
    description: Optional[str] = None
    opinion: Optional[Opinion] = None


class ProductBase(BaseModel):
    """Base product model with minimal required fields."""
    name: str
    description: Optional[str] = None
