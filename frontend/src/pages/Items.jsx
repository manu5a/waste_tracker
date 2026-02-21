import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const empty = { name: "", unit: "pieces", is_active: true };

export default function Items() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(empty);
  const [editingId, setEditingId] = useState(null);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    const data = await api.getItems(true);
    setItems(data);
  }

  useEffect(() => {
    load().catch((e) => setErr(e.message));
  }, []);

  function startEdit(item) {
    setEditingId(item.id);
    setForm({ name: item.name, unit: item.unit, is_active: item.is_active });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(empty);
  }

  async function submit(e) {
    e.preventDefault();
    setErr("");
    try {
      if (editingId) await api.updateItem({ id: editingId, ...form });
      else await api.createItem(form);
      cancelEdit();
      await load();
    } catch (e2) {
      setErr(e2.message);
    }
  }

  async function toggleActive(item) {
    setErr("");
    try {
      await api.updateItem({ id: item.id, name: item.name, unit: item.unit, is_active: !item.is_active });
      await load();
    } catch (e) {
      setErr(e.message);
    }
  }

  return (
    <div className="container">
      <h2>Items</h2>

      <div className="card">
        <h3>{editingId ? "Edit Item" : "Add Item"}</h3>
        <form onSubmit={submit}>
          <div className="row">
            <div>
              <label>Item name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div>
              <label>Unit</label>
              <select value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })}>
                <option value="pieces">pieces</option>
                <option value="kg">kg</option>
              </select>
            </div>
          </div>

          <div className="row" style={{ marginTop: 12 }}>
            <div>
              <label>Status</label>
              <select
                value={form.is_active ? "active" : "inactive"}
                onChange={(e) => setForm({ ...form, is_active: e.target.value === "active" })}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive (out-of-stock)</option>
              </select>
            </div>
            <div style={{ display: "flex", gap: 10, alignItems: "end" }}>
              <button type="submit">{editingId ? "Save" : "Add"}</button>
              {editingId ? <button type="button" className="secondary" onClick={cancelEdit}>Cancel</button> : null}
            </div>
          </div>
        </form>
        {err ? <div className="error" style={{ marginTop: 10 }}>{err}</div> : null}
      </div>

      <div className="card">
        <h3>Item List</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th><th>Unit</th><th>Status</th><th style={{ width: 220 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td>{it.name}</td>
                <td>{it.unit}</td>
                <td><span className="badge">{it.is_active ? "Active" : "Inactive"}</span></td>
                <td>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="secondary" onClick={() => startEdit(it)}>Edit</button>
                    <button className="secondary" onClick={() => toggleActive(it)}>{it.is_active ? "Deactivate" : "Activate"}</button>
                  </div>
                </td>
              </tr>
            ))}
            {!items.length ? <tr><td colSpan="4" className="small">No items yet.</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
