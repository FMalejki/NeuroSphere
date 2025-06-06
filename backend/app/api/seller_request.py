"""
Endpoint for sellers 
"""
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.seller_model import Seller, SellerCreate
from app.db.get_seller_info import (
    create_seller_in_db,
    list_sellers_from_db,
    get_seller_from_db,
)

router = APIRouter()

@router.post("/sellers/", response_model=Seller)
async def create_seller(seller_data: SellerCreate):
    """
    Endpoint for creating seller account 
    """
    seller_dict = {
        "name": seller_data.name,
        "description": seller_data.description,
        "products": seller_data.products,
        "opinions": seller_data.opinions,
        "public_key": seller_data.public_key,
    }
    seller = await create_seller_in_db(seller_dict)
    return seller

@router.get("/sellers/", response_model=List[Seller])
async def list_sellers():
    """
    Endpoint for returning list of all the sellers
    """
    sellers = await list_sellers_from_db()
    return sellers

@router.get("/biudsbfuyibds/{seller_id}", response_model=Seller)
async def get_seller(seller_id: str):
    """
    Endpoint for getting a seller by his id 
    """
    seller = await get_seller_from_db(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller

#TODO: o co chodzi z tą funkcją xd 
# @router.get("/sellers/{seller_id}", response_model=str)
# async def get_seller_public_key(seller_id: str):
#     public_key = "8BMFvnHjGFwQwGzFLaPbZavWo6RTVe2BF24HnEiBhbwn" #await get_seller_public_key_db(seller_id)
#     #if not public_key:
#     #    raise HTTPException(status_code=404, detail="Seller not found")
#     return public_key
