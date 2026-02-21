# Waste Tracker
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


