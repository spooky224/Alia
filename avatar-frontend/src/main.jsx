import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Rep from "./pages/Rep";
import Doctor from "./pages/Doctor";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/rep" element={<Rep />} />
      <Route path="/doctor" element={<Doctor />} />
    </Routes>
  </BrowserRouter>
);