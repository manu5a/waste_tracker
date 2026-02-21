import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function TomorrowPlan() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    const d = await api.getTomorrowPlan();
    setData(d);
  }

  useEffect(() => {
    load().catch((e) => setErr(e.message));
  }, []);

  return (
    <div className="container">
      <h2>Tomorrow Plan</h2>

      <div className="card">
        <div className="small">
          This is a **rough cook count** calculated from waste history only.
          (Internally it assumes waste is ~15% of cooked quantity.)
        </div>
        <div style={{ marginTop: 10 }}>
          <button onClick={load}>Refresh</button>
        </div>
        {err ? <div className="error" style={{ marginTop: 10 }}>{err}</div> : null}
      </div>

      {data ? (
        <div className="card">
          <h3>Target date: {data.target_date}</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Item</th>
                <th><b>Cook tomorrow</b></th>
                <th>Confidence</th>
                <th>History points</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((x) => (
                <tr key={x.item_id}>
                  <td>{x.item_name}</td>
                  <td><b>{x.recommended_cook_qty.toFixed(x.unit === "kg" ? 2 : 0)} {x.unit}</b></td>
                  <td><span className="badge">{x.confidence}</span></td>
                  <td className="small">{x.history_points_used}</td>
                </tr>
              ))}
              {data.items.length === 0 ? <tr><td colSpan="4" className="small">No active items.</td></tr> : null}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
