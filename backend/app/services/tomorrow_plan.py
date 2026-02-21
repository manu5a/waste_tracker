from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .. import models

# Waste-only conversion assumption:
# We assume "waste is about 15% of cooked quantity".
# Then cooked ~= waste / 0.15.
ASSUMED_WASTE_RATE = 0.15  # 15%


@dataclass
class Stats:
    avg: float
    n: int


def _weekday_average_last_n(db: Session, item_id: int, target_weekday: int, n_occurrences: int = 4) -> Stats:
    today = date.today()
    start = today - timedelta(days=90)

    stmt = (
        select(models.WasteEntry.entry_date, func.sum(models.WasteEntry.quantity))
        .where(models.WasteEntry.item_id == item_id)
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= today.isoformat())
        .group_by(models.WasteEntry.entry_date)
        .order_by(models.WasteEntry.entry_date.desc())
    )
    rows = db.execute(stmt).all()

    vals: list[float] = []
    for d_str, total in rows:
        d = date.fromisoformat(d_str)
        if d.weekday() == target_weekday:
            vals.append(float(total))
            if len(vals) >= n_occurrences:
                break

    if not vals:
        return Stats(avg=0.0, n=0)
    return Stats(avg=sum(vals) / len(vals), n=len(vals))


def _average_last_days(db: Session, item_id: int, days: int = 14) -> Stats:
    end = date.today()
    start = end - timedelta(days=days - 1)

    stmt = (
        select(func.coalesce(func.sum(models.WasteEntry.quantity), 0.0))
        .where(models.WasteEntry.item_id == item_id)
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= end.isoformat())
    )
    total = float(db.execute(stmt).scalar_one())
    avg = total / float(days)

    n_stmt = (
        select(func.count(func.distinct(models.WasteEntry.entry_date)))
        .where(models.WasteEntry.item_id == item_id)
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= end.isoformat())
    )
    n = int(db.execute(n_stmt).scalar_one())
    return Stats(avg=avg, n=n)


def _confidence(used_points: int) -> str:
    if used_points >= 4:
        return "high"
    if used_points >= 2:
        return "medium"
    return "low"


def _round_qty(unit: str, qty: float) -> float:
    if qty <= 0:
        return 0.0
    if unit == "pieces":
        # whole numbers
        return float(int(round(qty)))
    # kg: keep 2 decimals
    return float(round(qty, 2))


def _apply_minimum(unit: str, qty: float) -> float:
    if qty <= 0:
        return 0.0
    if unit == "pieces":
        return float(max(1.0, qty))
    return float(max(0.1, qty))


def build_tomorrow_plan(db: Session, target_date: date):
    items = db.execute(
        select(models.Item).where(models.Item.is_active.is_(True)).order_by(models.Item.name.asc())
    ).scalars().all()

    out_items = []
    for item in items:
        wd = _weekday_average_last_n(db, item.id, target_date.weekday(), n_occurrences=4)
        if wd.n >= 2:
            pred_waste = wd.avg
            used = wd.n
        else:
            fb = _average_last_days(db, item.id, days=14)
            pred_waste = fb.avg
            used = fb.n

        # Convert predicted waste -> cook qty using assumed waste rate
        if pred_waste <= 0:
            cook = 0.0
        else:
            cook = pred_waste / ASSUMED_WASTE_RATE

        cook = _apply_minimum(item.unit, cook)
        cook = _round_qty(item.unit, cook)

        out_items.append(
            {
                "item_id": item.id,
                "item_name": item.name,
                "unit": item.unit,
                "target_date": target_date.isoformat(),
                "recommended_cook_qty": float(cook),
                "confidence": _confidence(int(used)),
                "history_points_used": int(used),
            }
        )

    return {"target_date": target_date.isoformat(), "items": out_items}
