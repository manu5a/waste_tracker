import React from "react";

export default function StatCard({ label, value, sub }) {
  return (
    <div className="statCard">
      <div className="statLabel">{label}</div>
      <div className="statValue">{value}</div>
      {sub ? <div className="small">{sub}</div> : null}
    </div>
  );
}
