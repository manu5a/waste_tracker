from __future__ import annotations

from datetime import date, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import Base, engine, get_db
from . import models, schemas, crud
from .services.dashboard import build_dashboard
from .services.tomorrow_plan import build_tomorrow_plan


def create_app() -> FastAPI:
    app = FastAPI(title="Circle M Deli Waste MVP", version="1.3.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health():
        return {"ok": True}

    # ---- Items ----
    @app.get("/items", response_model=list[schemas.ItemOut])
    def get_items(
        include_inactive: bool = Query(True),
        db: Session = Depends(get_db),
    ):
        return crud.list_items(db, include_inactive=include_inactive)

    @app.post("/items", response_model=schemas.ItemOut)
    def post_item(data: schemas.ItemCreate, db: Session = Depends(get_db)):
        existing = db.execute(select(models.Item).where(models.Item.name == data.name.strip())).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Item name already exists")
        return crud.create_item(db, data)

    @app.put("/items", response_model=schemas.ItemOut)
    def put_item(data: schemas.ItemUpdate, db: Session = Depends(get_db)):
        existing = db.execute(select(models.Item).where(models.Item.name == data.name.strip())).scalar_one_or_none()
        if existing and existing.id != data.id:
            raise HTTPException(status_code=400, detail="Item name already exists")
        try:
            return crud.update_item(db, data)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ---- Waste ----
    @app.post("/waste")
    def post_waste(data: schemas.WasteCreate, db: Session = Depends(get_db)):
        try:
            entry = crud.create_waste(db, data)
            return {"id": entry.id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/waste", response_model=schemas.WasteListOut)
    def get_waste(
        start_date: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
        end_date: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
        item_id: int | None = Query(None),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
    ):
        rows, total = crud.list_waste(db, start_date, end_date, item_id, limit, offset)
        items = {i.id: i for i in db.execute(select(models.Item)).scalars().all()}

        out_rows = []
        for r in rows:
            it = items.get(r.item_id)
            out_rows.append(
                {
                    "id": r.id,
                    "entry_date": r.entry_date,
                    "item_id": r.item_id,
                    "quantity": float(r.quantity),
                    "note": r.note,
                    "item_name": it.name if it else "Unknown",
                    "unit": it.unit if it else "pieces",
                }
            )

        return {"rows": out_rows, "total": total}

    # ---- Dashboard ----
    @app.get("/dashboard", response_model=schemas.DashboardOut)
    def dashboard(
        view: schemas.DashboardView = Query("week"),
        anchor_date: str = Query(date.today().isoformat(), pattern=r"^\d{4}-\d{2}-\d{2}$"),
        db: Session = Depends(get_db),
    ):
        return build_dashboard(db, view=view, anchor_date_str=anchor_date)

    # ---- Tomorrow plan (tomorrow only) ----
    @app.get("/tomorrow-plan", response_model=schemas.TomorrowPlanOut)
    def tomorrow_plan(
        target_date: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
        db: Session = Depends(get_db),
    ):
        t = date.fromisoformat(target_date) if target_date else (date.today() + timedelta(days=1))
        return build_tomorrow_plan(db, target_date=t)

    return app


app = create_app()
