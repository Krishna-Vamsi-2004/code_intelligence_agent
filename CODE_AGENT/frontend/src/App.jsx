import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AgenticUI from "./pages/AgenticUI";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-slate-100">
        <Routes>
          <Route path="/" element={<AgenticUI />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
