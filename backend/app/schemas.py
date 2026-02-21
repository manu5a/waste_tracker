from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field

Unit = Literal["pieces", "kg"]
DashboardView = Literal["day", "week", "month"]


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    unit: Unit
    is_active: bool = True


class ItemUpdate(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=120)
    unit: Unit
    is_active: bool


class ItemOut(BaseModel):
    id: int
    name: str
    unit: Unit
    is_active: bool

    class Config:
        from_attributes = True


class WasteCreate(BaseModel):
    entry_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    item_id: int
    quantity: float = Field(gt=0)
    note: Optional[str] = None


class WasteOut(BaseModel):
    id: int
    entry_date: str
    item_id: int
    quantity: float
    note: Optional[str]
    item_name: str
    unit: Unit


class WasteListOut(BaseModel):
    rows: list[WasteOut]
    total: int


class ByItemPoint(BaseModel):
    item_id: int
    item_name: str
    unit: Unit
    total_waste: float


class TrendPoint(BaseModel):
    date: str
    total_waste: float


class Comparison(BaseModel):
    label: str
    current_total: float
    previous_total: float
    delta: float
    delta_pct: float | None


class DashboardOut(BaseModel):
    view: DashboardView
    anchor_date: str
    range_start: str
    range_end: str
    total_waste: float
    by_item: list[ByItemPoint]
    trend: list[TrendPoint]
    comparisons: list[Comparison]


class TomorrowPlanItem(BaseModel):
    item_id: int
    item_name: str
    unit: Unit
    target_date: str

    recommended_cook_qty: float
    confidence: Literal["low", "medium", "high"]
    history_points_used: int


class TomorrowPlanOut(BaseModel):
    target_date: str
    items: list[TomorrowPlanItem]
