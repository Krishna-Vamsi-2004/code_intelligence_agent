import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { pipelineService } from "../services/apiService";
import CodeInput from "../components/CodeInput";
import VisualFlow from "../components/VisualFlow";
import OptimalityScore from "../components/OptimalityScore";
import PipelineProgress from "../components/PipelineProgress";
import {
  Terminal,
  ShieldCheck,
  Code,
  Play,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";

const AgenticUI = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [stageErrors, setStageErrors] = useState({});
  const [regeneratingDiagram, setRegeneratingDiagram] = useState(false);

  const handleRegenerateDiagram = async () => {
    if (!result?.code_generation?.code && !result?.debugging?.fixed_code) {
      return;
    }

    setRegeneratingDiagram(true);
    
    try {
      const code = result?.debugging?.fixed_code || result?.code_generation?.code;
      
      // Call the mermaid generation endpoint
      const response = await fetch('http://localhost:8000/api/mermaid/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code_to_visualize: code }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        // Update only the visual_flow part of the result
        setResult(prev => ({
          ...prev,
          visual_flow: data.data
        }));
      } else {
        setStageErrors(prev => ({
          ...prev,
          visual_flow: data.message || 'Failed to regenerate diagram'
        }));
      }
    } catch (err) {
      setStageErrors(prev => ({
        ...prev,
        visual_flow: err.message || 'Failed to regenerate diagram'
      }));
    } finally {
      setRegeneratingDiagram(false);
    }
  };

  const handleRunPipeline = async (userInput, experienceLevel) => {
    setLoading(true);
    setResult(null);
    setError(null);
    setStageErrors({});
    setCompletedSteps([]);
    setCurrentStep("code_generation");

    try {
      const response = await pipelineService.run(userInput, experienceLevel);

      if (response.status === "success") {
        const data = response.data;
        setResult(data);

        // Process each stage
        const newCompletedSteps = [];
        const newStageErrors = {};

        Object.keys(data).forEach((stage) => {
          if (data[stage].status === "success") {
            newCompletedSteps.push(stage);
          } else if (data[stage].status === "error") {
            newStageErrors[stage] = data[stage].message;
          }
        });

        setCompletedSteps(newCompletedSteps);
        setStageErrors(newStageErrors);

        // If the very first step failed, set a global error
        if (data.code_generation.status === "error") {
          setError(data.code_generation.message);
        }

        setCurrentStep(null);
      } else {
        setError(response.message || "Pipeline execution failed.");
        setCurrentStep(null);
      }
    } catch (err) {
      setError(err.message || "An unexpected error occurred.");
      setCurrentStep(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-agent-bg text-gray-100 p-8 font-sans selection:bg-agent-primary/30">
      {/* Header */}
      <header className="max-w-screen-2xl mx-auto mb-12 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-tr from-agent-primary to-agent-secondary rounded-xl flex items-center justify-center shadow-lg shadow-agent-primary/20">
            <Terminal className="text-white w-7 h-7" />
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-tighter text-white">
              CODE INTELLIGENCE AGENT
            </h1>
            <p className="text-gray-500 text-sm font-medium uppercase tracking-[0.2em] flex items-center gap-2">
              <ShieldCheck size={14} className="text-agent-primary" />{" "}
              Self-Healing Agentic Pipeline v1.0
            </p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-8 text-xs font-bold text-gray-500 uppercase tracking-widest">
          <span className="flex items-center gap-2 hover:text-white transition-colors cursor-default">
            <div className="w-2 h-2 rounded-full bg-emerald-500" /> API Online
          </span>
          <span className="flex items-center gap-2 hover:text-white transition-colors cursor-default">
            <div className="w-2 h-2 rounded-full bg-blue-500" /> GPU Local
          </span>
          <span className="flex items-center gap-2 hover:text-white transition-colors cursor-default">
            <div className="w-2 h-2 rounded-full bg-violet-500" /> Kroki Sync
          </span>
        </div>
      </header>

      <main className="max-w-screen-2xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Left Column: Input & Progress (Fixed Width) */}
        <div className="col-span-12 lg:col-span-4 xl:col-span-3 space-y-8 sticky top-8">
          <CodeInput onRun={handleRunPipeline} loading={loading} />
          <PipelineProgress
            currentStep={currentStep}
            completedSteps={completedSteps}
            errors={stageErrors}
          />

          {error && (
            <div className="bg-rose-950/20 border border-rose-500/20 p-5 rounded-2xl flex items-start gap-4">
              <AlertTriangle className="text-rose-500 shrink-0 w-5 h-5 mt-0.5" />
              <div className="min-w-0 flex-1">
                <h3 className="text-rose-400 font-bold text-sm tracking-tight">
                  Pipeline Alert
                </h3>
                <p className="text-rose-300/80 text-xs mt-1 leading-relaxed break-words">
                  {error}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Results (Expansive) */}
        <div className="col-span-12 lg:col-span-8 xl:col-span-9 space-y-10">
          {/* Main Code Workspace */}
          <div className="bg-agent-surface rounded-2xl border border-agent-border shadow-2xl overflow-hidden flex flex-col min-h-[550px] transition-all duration-500">
            <div className="bg-black/40 px-6 py-4 border-b border-agent-border flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 font-bold text-xs uppercase tracking-widest text-gray-300">
                <div className="p-2 bg-agent-secondary/10 rounded-lg">
                  <Code size={18} className="text-agent-secondary" />
                </div>
                {result?.debugging?.status === "success"
                  ? "Enhanced Traceability Module"
                  : "Core Generation Logic"}
              </div>
              <div className="flex flex-wrap justify-end gap-2">
                {(result?.code_generation?.code || result?.debugging?.fixed_code) && (
                  <button
                    onClick={() => {
                      const code = result?.debugging?.fixed_code || result?.code_generation?.code;
                      navigator.clipboard.writeText(code);
                      // Show toast notification
                      const toast = document.createElement('div');
                      toast.className = 'fixed top-4 right-4 bg-emerald-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm font-bold';
                      toast.textContent = '✓ Code copied to clipboard!';
                      document.body.appendChild(toast);
                      setTimeout(() => toast.remove(), 2000);
                    }}
                    className="flex items-center gap-2 text-[10px] bg-agent-primary/10 text-agent-primary px-3 py-1.5 rounded-lg border border-agent-primary/20 font-bold uppercase hover:bg-agent-primary/20 transition-colors"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy Code
                  </button>
                )}
                {result?.code_generation?.retries > 0 && (
                  <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/20 font-black uppercase">
                    Auto-Healed ({result?.code_generation?.retries}x)
                  </span>
                )}
                {result?.debugging?.status === "error" && (
                  <span className="text-[9px] bg-amber-500/10 text-amber-500 px-3 py-1 rounded-full border border-amber-500/20 font-black uppercase">
                    Fallback Mode Active
                  </span>
                )}
              </div>
            </div>
            <div className="flex-1 w-full min-h-[450px]">
              <Editor
                height="450px"
                theme="vs-dark"
                defaultLanguage="python"
                value={
                  result?.debugging?.fixed_code ||
                  result?.code_generation?.code ||
                  "# [SYSTEM] Initializing Agentic Context...\n# [SYSTEM] Waiting for user requirements input."
                }
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  scrollBeyondLastLine: false,
                  padding: { top: 24, bottom: 24 },
                  backgroundColor: "#1e293b",
                  automaticLayout: true,
                  fontFamily: "'Fira Code', 'Cascadia Code', monospace",
                  lineNumbersMinChars: 4,
                }}
              />
            </div>
          </div>

          {/* Visualization & Metrics Row */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-10">
            <div className="min-w-0 h-full">
              <VisualFlow
                svgUrl={result?.visual_flow?.svg_url}
                svgDataUri={result?.visual_flow?.svg_data_uri}
                mermaidSyntax={result?.visual_flow?.mermaid_syntax}
                renderedLocally={result?.visual_flow?.rendered_locally}
                error={
                  result?.visual_flow?.status === "error"
                    ? result.visual_flow.message
                    : null
                }
                loading={loading && currentStep === "visual_flow"}
                onRegenerate={handleRegenerateDiagram}
                regenerating={regeneratingDiagram}
                hasCode={!!(result?.code_generation?.code || result?.debugging?.fixed_code)}
              />
            </div>
            <div className="min-w-0 h-full">
              <OptimalityScore
                scoreData={
                  result?.score?.status === "error"
                    ? { error: result.score.message, score: 0 }
                    : result?.score
                }
                loading={loading && currentStep === "score"}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-screen-2xl mx-auto mt-24 pb-12 border-t border-agent-border pt-10 flex flex-col md:flex-row justify-between items-center text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] gap-8">
        <p className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-agent-primary animate-pulse" />
          Neural Code Pipeline v1.0.4-STABLE
        </p>
        <div className="flex items-center gap-10">
          <span className="hover:text-white transition-colors cursor-pointer">
            Framework Docs
          </span>
          <span className="hover:text-white transition-colors cursor-pointer">
            Security Tiers
          </span>
          <span className="hover:text-white transition-colors cursor-pointer">
            Hardware Acceleration
          </span>
        </div>
      </footer>
    </div>
  );
};

export default AgenticUI;
