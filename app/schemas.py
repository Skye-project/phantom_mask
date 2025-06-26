from typing import List
from pydantic import BaseModel
from datetime import time


# /pharmacies/open
class PharmacyOpenInfo(BaseModel):
    id: int
    name: str
    day_of_week: str
    open_time: time
    close_time: time

# /pharmacies/{pharmacy_name}/masks
class MaskSchema(BaseModel):
    name: str
    price: float

    class Config:
        from_attributes = True


# /pharmacies/mask_count
class FilteredMask(BaseModel):
    name: str
    price: float

    class Config:
        from_attributes = True

class PharmacyMaskCountSchema(BaseModel):
    id: int
    name: str
    mask_count: int
    masks: List[FilteredMask]

    class Config:
        from_attributes = True

# /users/top_users
class UserWithTotalAmount(BaseModel):
    id: int
    name: str
    cash_balance: float
    total_amount: float

    class Config:
        from_attributes = True

# /search
class SearchResult(BaseModel):
    type: str  # pharmacy or mask
    name: str
    relevance: float

# /purchase
class PurchaseItem(BaseModel):
    pharmacy_id: int
    mask_id: int
    quantity: int

class PurchaseRequest(BaseModel):
    user_id: int
    purchases: List[PurchaseItem]

class PurchaseItemDetail(BaseModel):
    pharmacy_id: int
    pharmacy_name: str
    mask_id: int
    mask_name: str
    quantity: int
    unit_price: float
    total_price: float

class PurchaseResponse(BaseModel):
    message: str
    total_cost: float
    remaining_balance: float
    details: List[PurchaseItemDetail]

