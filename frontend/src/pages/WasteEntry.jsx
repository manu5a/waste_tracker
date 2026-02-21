import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";

export default function WasteEntry() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [recent, setRecent] = useState([]);

  const today = new Date().toISOString().slice(0, 10);

  const [form, setForm] = useState({
    entry_date: today,
    item_id: "",
    quantity: "",
    note: "",
  });

  async function loadItems() {
    const data = await api.getItems(false);
    setItems(data);
    if (!form.item_id && data.length) setForm((f) => ({ ...f, item_id: String(data[0].id) }));
  }

  async function loadRecent() {
    const data = await api.getWaste({ limit: 20, offset: 0 });
    setRecent(data.rows);
  }

  useEffect(() => {
    (async () => {
      try {
        await loadItems();
        await loadRecent();
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, []);

  const selectedItem = useMemo(() => items.find((i) => String(i.id) === String(form.item_id)), [items, form.item_id]);

  async function submit(e) {
    e.preventDefault();
    setErr(""); setOk("");
    try {
      await api.createWaste({
        entry_date: form.entry_date,
        item_id: Number(form.item_id),
        quantity: Number(form.quantity),
        note: form.note || null,
      });
      setOk("Saved waste entry.");
      setForm((f) => ({ ...f, quantity: "", note: "" }));
      await loadRecent();
    } catch (e2) {
      setErr(e2.message);
    }
  }

  return (
    <div className="container">
      <h2>Waste Entry</h2>

      <div className="card">
        <h3>Add Waste (manual)</h3>
        <form onSubmit={submit}>
          <div className="row">
            <div>
              <label>Date</label>
              <input type="date" value={form.entry_date} onChange={(e) => setForm({ ...form, entry_date: e.target.value })} required />
            </div>
            <div>
              <label>Item</label>
              <select value={form.item_id} onChange={(e) => setForm({ ...form, item_id: e.target.value })} required>
                {items.map((it) => (
                  <option key={it.id} value={it.id}>{it.name} ({it.unit})</option>
                ))}
              </select>
              {!items.length ? <div className="small">No active items. Add items first.</div> : null}
            </div>
          </div>

          <div className="row" style={{ marginTop: 12 }}>
            <div>
              <label>Waste quantity {selectedItem ? `(${selectedItem.unit})` : ""}</label>
              <input type="number" step="0.01" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} required />
            </div>
            <div>
              <label>Note (optional)</label>
              <input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <button type="submit" disabled={!items.length}>Save</button>
          </div>
        </form>

        {ok ? <div className="small" style={{ marginTop: 10 }}>{ok}</div> : null}
        {err ? <div className="error" style={{ marginTop: 10 }}>{err}</div> : null}
      </div>

      <div className="card">
        <h3>Recent Waste Entries</h3>
        <table className="table">
          <thead><tr><th>Date</th><th>Item</th><th>Qty</th><th>Note</th></tr></thead>
          <tbody>
            {recent.map((r) => (
              <tr key={r.id}>
                <td>{r.entry_date}</td>
                <td>{r.item_name}</td>
                <td>{r.quantity} {r.unit}</td>
                <td className="small">{r.note || ""}</td>
              </tr>
            ))}
            {!recent.length ? <tr><td colSpan="4" className="small">No waste entries yet.</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
