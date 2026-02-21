import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import StatCard from "../components/StatCard.jsx";
import { colorForId } from "../components/colors.js";
import {
  PieChart, Pie, Tooltip, Cell,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, ResponsiveContainer,
  Legend,
} from "recharts";

function pct(n) {
  if (n === null || n === undefined) return "—";
  return `${n.toFixed(1)}%`;
}

export default function Dashboard() {
  const today = new Date().toISOString().slice(0, 10);
  const [view, setView] = useState("week");
  const [anchorDate, setAnchorDate] = useState(today);
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    const d = await api.getDashboard({ view, anchorDate });
    setData(d);
  }

  useEffect(() => {
    load().catch((e) => setErr(e.message));
  }, [view, anchorDate]);

  const pieData = useMemo(() => (
    data ? data.by_item.map((x) => ({ id: x.item_id, name: x.item_name, value: x.total_waste })) : []
  ), [data]);

  const barData = useMemo(() => (
    data ? data.by_item.map((x) => ({ id: x.item_id, name: x.item_name, waste: x.total_waste })) : []
  ), [data]);

  const lineData = useMemo(() => (
    data ? data.trend.map((x) => ({ date: x.date, waste: x.total_waste })) : []
  ), [data]);

  return (
    <div className="container">
      <h2>Dashboard</h2>

      <div className="card">
        <div className="row">
          <div>
            <label>View</label>
            <select value={view} onChange={(e) => setView(e.target.value)}>
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
            </select>
          </div>
          <div>
            <label>Anchor date</label>
            <input type="date" value={anchorDate} onChange={(e) => setAnchorDate(e.target.value)} />
            <div className="small">This controls comparisons (today/week/month).</div>
          </div>
        </div>
        {err ? <div className="error" style={{ marginTop: 10 }}>{err}</div> : null}
      </div>

      {data ? (
        <>
          <div className="statGrid">
            <StatCard
              label={`Total waste (${data.range_start} → ${data.range_end})`}
              value={data.total_waste.toFixed(2)}
              sub="Sum of waste in selected range"
            />
            {data.comparisons.map((c) => (
              <StatCard
                key={c.label}
                label={c.label}
                value={(c.delta >= 0 ? "+" : "") + c.delta.toFixed(2)}
                sub={`Current: ${c.current_total.toFixed(2)} | Prev: ${c.previous_total.toFixed(2)} | ${pct(c.delta_pct)}`}
              />
            ))}
          </div>

          <div className="row">
            <div className="card">
              <h3>Waste share by item (Pie)</h3>
              <div style={{ width: "100%", height: 280 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={105}>
                      {pieData.map((entry) => (
                        <Cell key={entry.id} fill={colorForId(entry.id)} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <h3>Waste per item (Bar)</h3>
              <div style={{ width: "100%", height: 280 }}>
                <ResponsiveContainer>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" hide />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="waste" name="Waste">
                      {barData.map((entry) => (
                        <Cell key={entry.id} fill={colorForId(entry.id)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="small">Hover to see exact totals.</div>
            </div>
          </div>

          <div className="card">
            <h3>Daily total waste trend (Line)</h3>
            <div style={{ width: "100%", height: 320 }}>
              <ResponsiveContainer>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="waste" name="Total waste" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
