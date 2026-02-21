from __future__ import annotations

import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal, Base, engine
from . import models


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        items = [
            ("Chicken Fillet Roll", "pieces"),
            ("Sausage Roll", "pieces"),
            ("Breakfast Roll", "pieces"),
            ("Hot Wedges (tray)", "pieces"),
            ("Chicken Curry", "kg"),
        ]

        existing = {i.name: i for i in db.execute(select(models.Item)).scalars().all()}
        for name, unit in items:
            if name not in existing:
                db.add(models.Item(name=name, unit=unit, is_active=True))
        db.commit()

        all_items = list(db.execute(select(models.Item)).scalars().all())

        today = date.today()
        for days_back in range(0, 30):
            d = today - timedelta(days=days_back)
            ds = d.isoformat()
            for item in all_items:
                if random.random() < 0.88:
                    base = 2.0 + (item.id % 3)
                    weekend_boost = 1.6 if d.weekday() >= 5 else 1.0
                    qty = max(0.0, random.gauss(base * weekend_boost, 1.2))
                    if item.unit == "kg":
                        qty = qty / 10.0
                    if qty > 0.05:
                        db.add(models.WasteEntry(entry_date=ds, item_id=item.id, quantity=round(qty, 2), note=None))
        db.commit()
        print("Seed complete: items + last 30 days waste entries")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
