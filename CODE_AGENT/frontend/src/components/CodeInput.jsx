import React, { useState } from "react";
import Editor from "@monaco-editor/react";

const CodeInput = ({ onRun, loading }) => {
  const [value, setValue] = useState("");
  const [level, setLevel] = useState("Intermediate");

  const levels = ["Beginner", "Intermediate", "Advanced"];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onRun(value, level);
    }
  };

  return (
    <div className="bg-agent-surface p-6 rounded-xl border border-agent-border shadow-xl">
      <div className="space-y-4 mb-6">
        <h2 className="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-agent-primary to-agent-secondary tracking-tight">
          Request Intelligence
        </h2>
        <div className="flex flex-wrap items-center gap-2 p-1.5 bg-black/20 rounded-xl border border-agent-border/50">
          {levels.map((l) => (
            <button
              key={l}
              onClick={() => setLevel(l)}
              className={`flex-1 min-w-[70px] px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${
                level === l
                  ? "bg-agent-primary text-white shadow-lg shadow-agent-primary/20"
                  : "bg-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5"
              }`}
            >
              {l}
            </button>
          ))}
        </div>
      </div>

      <textarea
        className="w-full h-32 bg-agent-bg text-gray-200 p-4 rounded-lg border border-agent-border focus:ring-2 focus:ring-agent-primary focus:outline-none resize-none transition-all"
        placeholder="E.g., Write a Python function for Fibonacci with error handling..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={loading}
      />

      <button
        onClick={handleSubmit}
        disabled={loading || !value.trim()}
        className={`w-full mt-4 py-3 rounded-lg font-bold transition-all shadow-lg ${
          loading
            ? "bg-gray-700 cursor-not-allowed text-gray-400"
            : "bg-gradient-to-r from-agent-primary to-agent-secondary hover:brightness-110 active:scale-[0.98]"
        }`}
      >
        {loading ? "Executing Pipeline..." : "Start Pipeline"}
      </button>
    </div>
  );
};

export default CodeInput;
