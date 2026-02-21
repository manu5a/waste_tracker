from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from . import models, schemas


def list_items(db: Session, include_inactive: bool = True) -> list[models.Item]:
    stmt = select(models.Item).order_by(models.Item.name.asc())
    if not include_inactive:
        stmt = stmt.where(models.Item.is_active.is_(True))
    return list(db.execute(stmt).scalars().all())


def create_item(db: Session, data: schemas.ItemCreate) -> models.Item:
    item = models.Item(name=data.name.strip(), unit=data.unit, is_active=data.is_active)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, data: schemas.ItemUpdate) -> models.Item:
    item = db.get(models.Item, data.id)
    if not item:
        raise ValueError("Item not found")
    item.name = data.name.strip()
    item.unit = data.unit
    item.is_active = data.is_active
    db.commit()
    db.refresh(item)
    return item


def create_waste(db: Session, data: schemas.WasteCreate) -> models.WasteEntry:
    item = db.get(models.Item, data.item_id)
    if not item:
        raise ValueError("Item not found")
    entry = models.WasteEntry(
        entry_date=data.entry_date,
        item_id=data.item_id,
        quantity=float(data.quantity),
        note=data.note.strip() if data.note else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_waste(
    db: Session,
    start_date: str | None,
    end_date: str | None,
    item_id: int | None,
    limit: int,
    offset: int,
) -> tuple[list[models.WasteEntry], int]:
    stmt = select(models.WasteEntry).order_by(models.WasteEntry.entry_date.desc(), models.WasteEntry.id.desc())
    count_stmt = select(func.count()).select_from(models.WasteEntry)

    if start_date:
        stmt = stmt.where(models.WasteEntry.entry_date >= start_date)
        count_stmt = count_stmt.where(models.WasteEntry.entry_date >= start_date)
    if end_date:
        stmt = stmt.where(models.WasteEntry.entry_date <= end_date)
        count_stmt = count_stmt.where(models.WasteEntry.entry_date <= end_date)
    if item_id:
        stmt = stmt.where(models.WasteEntry.item_id == item_id)
        count_stmt = count_stmt.where(models.WasteEntry.item_id == item_id)

    total = int(db.execute(count_stmt).scalar_one())
    rows = list(db.execute(stmt.limit(limit).offset(offset)).scalars().all())
    return rows, total
