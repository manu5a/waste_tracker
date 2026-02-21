# Circle M Deli Waste Tracker + Tomorrow Planner (MVP v1.3 - waste-only, no extra inputs)

This version matches your instruction exactly:
- You only **enter waste**.
- Dashboard shows waste KPIs + charts.
- Tomorrow Plan outputs **only**: "Cook this many pieces/kg for each item" based on waste history.

## IMPORTANT (honest)
With only waste data, there is no perfect way to infer how many were cooked/sold.
So this MVP uses a simple, robust proxy:

1) Predict tomorrow waste for each item:
   - Same weekday average (last 4 occurrences) OR fallback last 14-day average.
2) Convert predicted waste to a cook recommendation using a fixed waste-rate assumption:
   - Assume waste is ~15% of cooked quantity (configurable constant).
   - Recommended cook = predicted_waste / 0.15
   - Guardrails:
     - If predicted_waste is 0 -> recommend 0
     - Minimums: pieces min 1, kg min 0.1
     - Round: pieces to whole numbers, kg to 2 decimals

This gives a **rough count** without asking staff to enter anything except waste.

---

## Prerequisites (Windows)

Install:
- Python 3.11+
- Node.js LTS
- VS Code

Verify:
```powershell
python --version
node --version
npm --version
```

---

## Run backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Seed demo data:
```powershell
python -m app.seed
```

API docs:
- http://127.0.0.1:8000/docs

---

## Run frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend:
- http://127.0.0.1:5173
