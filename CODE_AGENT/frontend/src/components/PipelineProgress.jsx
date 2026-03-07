import React from "react";
import { CheckCircle2, Circle, AlertCircle, Loader2 } from "lucide-react";

const PipelineProgress = ({ currentStep, completedSteps, errors }) => {
  const steps = [
    {
      id: "code_generation",
      name: "Generation",
      label: "Adaptive Context Injection",
    },
    { id: "debugging", name: "Debugging", label: "Error Recovery & Fix" },
    { id: "score", name: "Optimality", label: "AST-based Scoring" },
    { id: "visual_flow", name: "Visualization", label: "Mermaid Flowchart" },
  ];

  return (
    <div className="bg-agent-surface p-6 rounded-xl border border-agent-border shadow-xl h-full">
      <h2 className="text-xl font-bold text-gray-200 mb-8 border-b border-agent-border pb-4">
        Pipeline Execution
      </h2>
      <div className="space-y-10 relative">
        <div className="absolute left-4 top-4 bottom-4 w-1 bg-agent-border -z-10" />
        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(step.id);
          const isCurrent = currentStep === step.id;
          const hasError = !!errors[step.id];

          return (
            <div key={step.id} className="flex gap-6 items-start relative">
              <div
                className={`w-9 h-9 flex items-center justify-center rounded-full transition-all shrink-0 z-10 ${
                  isCompleted
                    ? "bg-emerald-500 shadow-emerald-500/30 shadow-lg"
                    : hasError
                      ? "bg-rose-500 shadow-rose-500/30"
                      : isCurrent
                        ? "bg-sky-500 animate-pulse-slow"
                        : "bg-slate-800"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-white" />
                ) : hasError ? (
                  <AlertCircle className="w-5 h-5 text-white" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-500" />
                )}
              </div>
              <div className="flex flex-col min-w-0">
                <span
                  className={`font-black text-[10px] uppercase tracking-[0.2em] ${
                    isCompleted
                      ? "text-emerald-400"
                      : isCurrent
                        ? "text-sky-400 font-black animate-pulse"
                        : hasError
                          ? "text-rose-400"
                          : "text-slate-600"
                  }`}
                >
                  {step.name}
                </span>
                <span
                  className={`text-[10px] mt-0.5 transition-colors font-bold ${
                    isCurrent ? "text-gray-200" : "text-slate-500"
                  }`}
                >
                  {step.label}
                </span>
                {hasError && (
                  <span className="text-[9px] text-rose-500 mt-2 font-mono leading-relaxed break-words border-l-2 border-rose-500/20 pl-2 py-1 bg-rose-500/5 rounded-r">
                    {errors[step.id]}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PipelineProgress;
