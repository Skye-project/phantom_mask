from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, time, timedelta

from app import models, schemas
from app.database import get_db
from app.utils import WEEKDAYS

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Phantom Mask API is live"}


@app.get("/pharmacies/open", response_model=List[schemas.PharmacyOpenInfo])
def get_open_pharmacies(
    day: Optional[str] = Query(None, examples={"example": {"value": "Mon"}}),
    time: Optional[str] = Query(None, examples={"example": {"value": "10:00"}}),
    db: Session = Depends(get_db)
):
    # Monday" → "Mon" 
    if day:
        day = WEEKDAYS.get(day, day)

    # string to time conversion
    target_time = None
    if time:
        try:
            target_time = datetime.strptime(time, "%H:%M").time()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format")

    query = db.query(models.Pharmacy, models.OpeningHour).join(models.OpeningHour)

    # filter by day and time if provided
    if day:
        query = query.filter(models.OpeningHour.day_of_week == day)
    if target_time:
        query = query.filter(
            models.OpeningHour.open_time <= target_time,
            models.OpeningHour.close_time >= target_time
        )

    result = query.all()

    return [
        schemas.PharmacyOpenInfo(
            id=pharmacy.id,
            name=pharmacy.name,
            day_of_week=oh.day_of_week,
            open_time=oh.open_time,
            close_time=oh.close_time
        )
        for pharmacy, oh in result
    ]


@app.get("/pharmacies/{pharmacy_name}/masks", response_model=List[schemas.MaskSchema])
def list_masks_by_pharmacy_name(
    pharmacy_name: str,
    sort_by: Optional[str] = Query("name", enum=["name", "price"]),
    order: Optional[str] = Query("asc", enum=["asc", "desc"]),
    db: Session = Depends(get_db)
):
    pharmacy = db.query(models.Pharmacy).filter(models.Pharmacy.name == pharmacy_name).first()
    
    if not pharmacy:
        raise HTTPException(status_code=404, detail="Pharmacy not found")

    query = db.query(models.Mask).filter(models.Mask.pharmacy_id == pharmacy.id)
    
    # Apply sorting if specified (default is by name)
    sort_column = models.Mask.price if sort_by == "price" else models.Mask.name

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:  # Default to ascending order
        query = query.order_by(sort_column)

    return query.all()

@app.get("/pharmacies/mask_count", response_model=List[schemas.PharmacyMaskCountSchema])
def mask_count(
    min_price: float = Query(...),
    max_price: float = Query(...),
    count: int = Query(...),
    op: str = Query(..., pattern="^(gt|lt)$"),
    db: Session = Depends(get_db)
):
    op_map = {
        'gt': lambda a, b: a > b,
        'lt': lambda a, b: a < b
    }

    pharmacies = db.query(models.Pharmacy).all()
    result = []

    for pharmacy in pharmacies:
        # Filter masks by price range
        filtered_masks = [
            m for m in pharmacy.masks
            if min_price <= m.price <= max_price
        ]

        # Check if the count of filtered masks meets the condition
        if op_map[op](len(filtered_masks), count):
            result.append(schemas.PharmacyMaskCountSchema(
                id=pharmacy.id,
                name=pharmacy.name,
                mask_count=len(filtered_masks),
                masks=[
                    schemas.FilteredMask(name=m.name, price=m.price)
                    for m in filtered_masks
                ]
            ))

    return result

def validate_date_format(date_str: str) -> datetime:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD.")
    return date

@app.get("/users/top_users", response_model=List[schemas.UserWithTotalAmount])
def get_top_users(
    top: int = Query(5, ge=1), # Minimum limit of 1, default to 5
    start_date: Optional[str] = None, # YYYY-MM-DD format
    end_date: Optional[str] = None, # YYYY-MM-DD format
    db: Session = Depends(get_db)
):
    query = db.query(
        models.User,
        func.sum(models.PurchaseHistory.transaction_amount).label("total_amount")
    ).join(models.PurchaseHistory).group_by(models.User.id)

    if start_date:
        start = validate_date_format(start_date)
        query = query.filter(models.PurchaseHistory.transaction_date >= start)

    if end_date:
        end = validate_date_format(end_date) + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(models.PurchaseHistory.transaction_date <= end)
        
    query = query.order_by(func.sum(models.PurchaseHistory.transaction_amount).desc()).limit(top)

    result = query.all()

    return [
        schemas.UserWithTotalAmount(
            id=user.id,
            name=user.name,
            cash_balance=user.cash_balance,
            total_amount=round(total_amount, 2)
        )
        for user, total_amount in result
    ]


@app.get("/transactions/summary")
def get_transaction_summary(
    start_date: Optional[str] = None, # YYYY-MM-DD format
    end_date: Optional[str] = None, # YYYY-MM-DD format
    db: Session = Depends(get_db)
):
    query = db.query(models.PurchaseHistory)

    if start_date:
        start = validate_date_format(start_date)
        query = query.filter(models.PurchaseHistory.transaction_date >= start)

    if end_date:
        end = validate_date_format(end_date) + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(models.PurchaseHistory.transaction_date <= end)

    total_value = sum([p.transaction_amount for p in query.all()])
    total_count = query.count()

    return {
        "total_transactions": total_count,
        "total_amount": round(total_value, 2)
    }

@app.get("/search", response_model=List[schemas.SearchResult])
def search_items(
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    keyword_lower = keyword.lower()
    results = []

    # Search pharmacies
    pharmacies = db.query(models.Pharmacy).all()
    for p in pharmacies:
        if keyword_lower in p.name.lower():
            results.append({
                "type": "pharmacy",
                "name": p.name,
                "relevance": len(keyword) / len(p.name)
            })

    # Search masks
    masks = db.query(models.Mask).all()
    for m in masks:
        if keyword_lower in m.name.lower():
            results.append({
                "type": "mask",
                "name": m.name,
                "relevance": len(keyword) / len(m.name)
            })

    return sorted(results, key=lambda x: x["relevance"], reverse=True)

@app.post("/purchase", response_model=schemas.PurchaseResponse)
def purchase_masks(purchase: schemas.PurchaseRequest, db: Session = Depends(get_db)):
    # check if user exists
    user = db.query(models.User).filter(models.User.id == purchase.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_cost = 0

    # check if all masks exist and calculate total cost
    for item in purchase.purchases:

        mask = db.query(models.Mask).filter(
            models.Mask.id == item.mask_id,
            models.Mask.pharmacy_id == item.pharmacy_id
        ).first()

        if not mask:
            raise HTTPException(status_code=404, detail=f"Mask {item.mask_id} not found in pharmacy {item.pharmacy_id}")
        
        # if mask.price is None:
        #     raise HTTPException(status_code=500, detail=f"Mask {mask.id} has no price")

        total_cost += round(mask.price * item.quantity, 2)

    # check if user has enough balance
    if user.cash_balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    details = []
    now = datetime.now()

    # execute the purchase and update database
    for item in purchase.purchases:
        pharmacy = db.query(models.Pharmacy).filter(models.Pharmacy.id == item.pharmacy_id).first()
        if not pharmacy:
            raise HTTPException(status_code=404, detail=f"Pharmacy {item.pharmacy_id} not found")

        mask = db.query(models.Mask).filter(
            models.Mask.id == item.mask_id,
            models.Mask.pharmacy_id == item.pharmacy_id
        ).first()

        item_total = round(mask.price * item.quantity, 2)

        # update purchase history
        db.add(models.PurchaseHistory(
            user_id=user.id,
            pharmacy_id=pharmacy.id,
            mask_name=mask.name,
            transaction_amount=item_total,
            transaction_date=now
        ))

        # update pharmacy cash balance
        pharmacy.cash_balance += item_total

        # return purchase details
        details.append(schemas.PurchaseItemDetail(
            pharmacy_id=pharmacy.id,
            pharmacy_name=pharmacy.name,
            mask_id=mask.id,
            mask_name=mask.name,
            quantity=item.quantity,
            unit_price=mask.price,
            total_price=item_total
        ))

    # update user's cash balance
    user.cash_balance -= total_cost

    db.commit()

    return schemas.PurchaseResponse(
        message="Purchase successful",
        total_cost=round(total_cost, 2),
        remaining_balance=round(user.cash_balance, 2),
        details=details
    )
