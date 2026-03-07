import React from "react";
import { Gauge, Zap, TrendingUp, Layers } from "lucide-react";

const OptimalityScore = ({ scoreData, loading }) => {
  if (loading)
    return (
      <div className="bg-agent-surface p-6 rounded-xl border border-agent-border shadow-xl h-full animate-pulse">
        <div className="w-1/3 h-6 bg-slate-700/50 rounded mb-6"></div>
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-24 h-24 bg-slate-700/50 rounded-full"></div>
          <div className="w-1/2 h-4 bg-slate-700/50 rounded"></div>
        </div>
      </div>
    );

  if (!scoreData) return null;

  const { score, metrics, error } = scoreData;

  const scoreColor =
    score > 80
      ? "text-emerald-400"
      : score > 50
        ? "text-amber-400"
        : "text-rose-400";
  const progressColor =
    score > 80 ? "bg-emerald-400" : score > 50 ? "bg-amber-400" : "bg-rose-400";

  return (
    <div className="bg-agent-surface p-6 rounded-xl border border-agent-border shadow-xl h-full flex flex-col">
      <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-emerald-600 mb-6 flex items-center gap-2">
        <Gauge size={20} /> Optimality Score
      </h2>

      {error ? (
        <div className="text-rose-400 text-sm italic p-4 bg-rose-900/10 rounded-lg border border-rose-500/20">
          {error}
        </div>
      ) : (
        <div className="flex-1 space-y-8">
          <div className="flex flex-col items-center">
            <div className="relative flex items-center justify-center">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="58"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  className="text-slate-800"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="58"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={364.4}
                  strokeDashoffset={364.4 - (score / 100) * 364.4}
                  className={`${scoreColor} transition-all duration-1000 ease-out`}
                  strokeLinecap="round"
                />
              </svg>
              <span className={`absolute text-3xl font-black ${scoreColor}`}>
                {score}
              </span>
            </div>
            <p className="mt-2 text-gray-500 text-xs uppercase tracking-widest font-bold">
              Performance Index
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 xl:grid-cols-1 gap-3">
            <MetricItem
              icon={<Layers size={14} className="text-emerald-400" />}
              label="Node Count"
              value={metrics?.node_count}
            />
            <MetricItem
              icon={<TrendingUp size={14} className="text-emerald-400" />}
              label="Complexity"
              value={metrics?.complexity}
            />
            <MetricItem
              icon={<Zap size={14} className="text-emerald-400" />}
              label="Density"
              value={metrics?.density}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const MetricItem = ({ icon, label, value }) => (
  <div className="flex items-center justify-between p-3 bg-black/20 rounded-lg border border-agent-border">
    <div className="flex items-center gap-2 text-gray-400 text-xs">
      {icon}
      <span>{label}</span>
    </div>
    <span className="text-white font-mono font-bold text-sm tracking-tight">
      {value}
    </span>
  </div>
);

export default OptimalityScore;
