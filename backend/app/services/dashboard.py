from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .. import models


@dataclass
class Range:
    start: date
    end: date  # inclusive


def _parse(d: str) -> date:
    return date.fromisoformat(d)


def _day_range(anchor: date) -> Range:
    return Range(start=anchor, end=anchor)


def _week_range(anchor: date) -> Range:
    start = anchor - timedelta(days=anchor.weekday())  # Monday
    end = start + timedelta(days=6)
    return Range(start=start, end=end)


def _month_range(anchor: date) -> Range:
    start = anchor.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1, day=1)
    else:
        next_month = start.replace(month=start.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return Range(start=start, end=end)


def _get_range(view: str, anchor: date) -> Range:
    if view == "day":
        return _day_range(anchor)
    if view == "week":
        return _week_range(anchor)
    if view == "month":
        return _month_range(anchor)
    raise ValueError("Invalid view (use day/week/month)")


def _sum_waste(db: Session, start: date, end: date) -> float:
    stmt = (
        select(func.coalesce(func.sum(models.WasteEntry.quantity), 0.0))
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= end.isoformat())
    )
    return float(db.execute(stmt).scalar_one())


def _sum_waste_by_item(db: Session, start: date, end: date):
    stmt = (
        select(
            models.Item.id,
            models.Item.name,
            models.Item.unit,
            func.coalesce(func.sum(models.WasteEntry.quantity), 0.0).label("total_waste"),
        )
        .join(models.WasteEntry, models.WasteEntry.item_id == models.Item.id)
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= end.isoformat())
        .group_by(models.Item.id, models.Item.name, models.Item.unit)
        .order_by(func.sum(models.WasteEntry.quantity).desc())
    )
    return db.execute(stmt).all()


def _daily_trend(db: Session, start: date, end: date):
    days = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += timedelta(days=1)

    stmt = (
        select(
            models.WasteEntry.entry_date,
            func.coalesce(func.sum(models.WasteEntry.quantity), 0.0).label("total_waste"),
        )
        .where(models.WasteEntry.entry_date >= start.isoformat())
        .where(models.WasteEntry.entry_date <= end.isoformat())
        .group_by(models.WasteEntry.entry_date)
        .order_by(models.WasteEntry.entry_date.asc())
    )
    rows = {r[0]: float(r[1]) for r in db.execute(stmt).all()}

    out = []
    for d in days:
        ds = d.isoformat()
        out.append({"date": ds, "total_waste": float(rows.get(ds, 0.0))})
    return out


def _comparison(label: str, current: float, previous: float):
    delta = current - previous
    delta_pct = None
    if previous and abs(previous) > 1e-9:
        delta_pct = (delta / previous) * 100.0
    return {
        "label": label,
        "current_total": float(current),
        "previous_total": float(previous),
        "delta": float(delta),
        "delta_pct": None if delta_pct is None else float(delta_pct),
    }


def build_dashboard(db: Session, view: str, anchor_date_str: str):
    anchor = _parse(anchor_date_str)
    r = _get_range(view, anchor)

    total = _sum_waste(db, r.start, r.end)
    by_item_rows = _sum_waste_by_item(db, r.start, r.end)
    by_item = [
        {"item_id": int(i), "item_name": n, "unit": u, "total_waste": float(t)}
        for (i, n, u, t) in by_item_rows
    ]
    trend = _daily_trend(db, r.start, r.end)

    comps = []
    yesterday = anchor - timedelta(days=1)
    comps.append(_comparison("Today vs Yesterday", _sum_waste(db, anchor, anchor), _sum_waste(db, yesterday, yesterday)))

    this_w = _week_range(anchor)
    last_w = Range(start=this_w.start - timedelta(days=7), end=this_w.end - timedelta(days=7))
    comps.append(_comparison("This Week vs Last Week", _sum_waste(db, this_w.start, this_w.end), _sum_waste(db, last_w.start, last_w.end)))

    this_m = _month_range(anchor)
    last_month_anchor = this_m.start - timedelta(days=1)
    last_m = _month_range(last_month_anchor)
    comps.append(_comparison("This Month vs Last Month", _sum_waste(db, this_m.start, this_m.end), _sum_waste(db, last_m.start, last_m.end)))

    return {
        "view": view,
        "anchor_date": anchor.isoformat(),
        "range_start": r.start.isoformat(),
        "range_end": r.end.isoformat(),
        "total_waste": float(total),
        "by_item": by_item,
        "trend": trend,
        "comparisons": comps,
    }
