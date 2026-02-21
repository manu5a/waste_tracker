from __future__ import annotations

from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # "pieces" or "kg"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    waste_entries: Mapped[list["WasteEntry"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )


class WasteEntry(Base):
    __tablename__ = "waste_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    item: Mapped[Item] = relationship(back_populates="waste_entries")


Index("ix_waste_date_item", WasteEntry.entry_date, WasteEntry.item_id)
