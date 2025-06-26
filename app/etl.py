import json
from datetime import datetime
from app.models import Pharmacy, Mask, OpeningHour, User, PurchaseHistory
from app.database import SessionLocal, init_db
from app.utils import parse_opening_hours

def load_pharmacies(json_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    db = SessionLocal()
    for p in data:
        pharmacy = Pharmacy(
            name=p["name"],
            cash_balance=p.get("cashBalance", 0.0)
        )
        db.add(pharmacy)
        db.flush()  # 確保 pharmacy.id 可用

        # Masks
        for m in p.get("masks", []):
            db.add(Mask(
                name=m["name"],
                price=m["price"],
                pharmacy_id=pharmacy.id
            ))

        # Opening Hours
        for oh in parse_opening_hours(p.get("openingHours", "")):
            db.add(OpeningHour(
                day_of_week=oh["day_of_week"],
                open_time=oh["open_time"],
                close_time=oh["close_time"],
                pharmacy_id=pharmacy.id
            ))

    db.commit()
    db.close()

def load_users(json_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    db = SessionLocal()
    pharmacy_lookup = {p.name: p.id for p in db.query(Pharmacy).all()}

    for u in data:
        user = User(
            name=u["name"],
            cash_balance=u.get("cashBalance", 0.0)
        )
        db.add(user)
        db.flush()  # 確保 user.id 可用

        for ph in u.get("purchaseHistories", []):
            pharmacy_id = pharmacy_lookup.get(ph["pharmacyName"])
            if pharmacy_id:
                db.add(PurchaseHistory(
                    user_id=user.id,
                    pharmacy_id=pharmacy_id,
                    mask_name=ph["maskName"],
                    transaction_amount=ph["transactionAmount"],
                    transaction_date=datetime.strptime(ph["transactionDate"], "%Y-%m-%d %H:%M:%S")
                ))

    db.commit()
    db.close()

def run_etl():
    init_db()
    load_pharmacies("data/pharmacies.json")
    load_users("data/users.json")

if __name__ == "__main__":
    run_etl()
