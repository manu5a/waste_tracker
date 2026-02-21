import React from "react";

export default function Nav({ route, setRoute }) {
  const links = [
    { key: "dashboard", label: "Dashboard" },
    { key: "waste", label: "Waste Entry" },
    { key: "items", label: "Items" },
    { key: "tomorrow", label: "Tomorrow Plan" }
  ];

  return (
    <div className="nav">
      {links.map((l) => (
        <a
          key={l.key}
          href="#"
          className={route === l.key ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            setRoute(l.key);
          }}
        >
          {l.label}
        </a>
      ))}
    </div>
  );
}
