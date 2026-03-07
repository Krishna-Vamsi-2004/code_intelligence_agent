import React from "react";
import { Download, AlertCircle, Maximize2, Zap, RefreshCw } from "lucide-react";

const VisualFlow = ({ svgUrl, svgDataUri, mermaidSyntax, error, loading, renderedLocally, onRegenerate, regenerating, hasCode }) => {
  // Prefer local rendering (data URI) over external URL
  const displayUrl = svgDataUri || svgUrl;
  
  if (loading)
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-agent-surface rounded-xl border border-agent-border shadow-xl">
        <div className="w-12 h-12 border-4 border-agent-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-gray-400 font-medium">Rendering Diagram...</p>
      </div>
    );

  if (error)
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-agent-surface rounded-xl border border-rose-500/10 shadow-xl h-full">
        <div className="p-3 bg-rose-500/10 rounded-full mb-4">
          <AlertCircle className="w-6 h-6 text-rose-500" />
        </div>
        <h3 className="text-sm font-black text-gray-200 uppercase tracking-widest text-center">
          Diagram Rendering Halt
        </h3>
        <p className="text-gray-400 mt-2 text-center text-xs leading-relaxed max-w-[200px] break-words">
          {error}
        </p>
        {mermaidSyntax && (
          <details className="mt-6 w-full">
            <summary className="text-[10px] text-gray-500 cursor-pointer hover:text-gray-300 uppercase font-black tracking-widest text-center list-none outline-none">
              View Raw Syntax
            </summary>
            <pre className="mt-3 p-3 bg-black/40 text-[10px] text-emerald-400/80 rounded-lg overflow-x-auto border border-agent-border/50">
              {mermaidSyntax}
            </pre>
          </details>
        )}
      </div>
    );

  if (!displayUrl) return null;

  const downloadDiagram = () => {
    if (svgDataUri) {
      // Download from data URI
      const link = document.createElement('a');
      link.href = svgDataUri;
      link.download = 'diagram.svg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else if (svgUrl) {
      // Fallback to external URL
      window.open(svgUrl, '_blank');
    }
  };

  return (
    <div className="bg-agent-surface p-6 rounded-xl border border-agent-border shadow-xl h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-agent-accent to-agent-secondary">
            Visual Flow
          </h2>
          {renderedLocally && (
            <span className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded-full border border-emerald-500/20">
              <Zap size={10} />
              LOCAL
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasCode && onRegenerate && (
            <button
              onClick={onRegenerate}
              disabled={regenerating}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] bg-agent-primary/10 text-agent-primary hover:bg-agent-primary/20 transition-colors rounded-lg border border-agent-primary/20 font-bold uppercase disabled:opacity-50 disabled:cursor-not-allowed"
              title="Regenerate diagram from current code"
            >
              <RefreshCw size={12} className={regenerating ? 'animate-spin' : ''} />
              {regenerating ? 'Regenerating...' : 'Regenerate'}
            </button>
          )}
          <button
            onClick={() => window.open(displayUrl, "_blank")}
            className="p-1.5 text-gray-400 hover:text-white transition-colors"
            title="View Full Size"
          >
            <Maximize2 size={16} />
          </button>
          <button
            onClick={downloadDiagram}
            className="p-1.5 text-gray-400 hover:text-white transition-colors"
            title="Download SVG"
          >
            <Download size={16} />
          </button>
        </div>
      </div>

      <div className="flex-1 bg-white/5 rounded-lg border border-agent-border p-4 flex items-center justify-center overflow-hidden min-h-[300px]">
        <img
          src={displayUrl}
          alt="Visual Flow Diagram"
          className="max-w-full max-h-full object-contain filter invert opacity-80"
        />
      </div>
      
      {mermaidSyntax && (
        <details className="mt-4">
          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300 font-medium">
            View Mermaid Code
          </summary>
          <pre className="mt-2 p-3 bg-black/40 text-xs text-emerald-400/80 rounded-lg overflow-x-auto border border-agent-border/50">
            {mermaidSyntax}
          </pre>
        </details>
      )}
    </div>
  );
};

export default VisualFlow;
