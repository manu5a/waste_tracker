import React, { useState } from "react";
import Nav from "./components/Nav.jsx";
import Items from "./pages/Items.jsx";
import WasteEntry from "./pages/WasteEntry.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import TomorrowPlan from "./pages/TomorrowPlan.jsx";

export default function App() {
  const [route, setRoute] = useState("dashboard");

  return (
    <>
      <Nav route={route} setRoute={setRoute} />
      {route === "dashboard" ? <Dashboard /> : null}
      {route === "waste" ? <WasteEntry /> : null}
      {route === "items" ? <Items /> : null}
      {route === "tomorrow" ? <TomorrowPlan /> : null}
    </>
  );
}
