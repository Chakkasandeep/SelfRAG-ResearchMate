import React, { useState } from "react";
import { Search, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { useResearchStore } from "@/store/researchStore";
import { useSSEStream } from "@/hooks/useSSEStream";

export default function ChatInterface() {
  const [queryInput, setQueryInput] = useState("");
  const { isResearching, stage, error, setError } = useResearchStore();
  const { startResearch } = useSSEStream();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim() || isResearching) return;
    startResearch(queryInput);
  };

  const suggestions = [
    "Self-RAG hallucination reduction in clinical LLMs",
    "Transformer architectures in maritime deep oceanography",
    "Quantum annealing efficiency for public key cryptography",
    "Graph neural networks for drug discovery pipelines"
  ];

  const handleSuggestionClick = (text: string) => {
    if (isResearching) return;
    setQueryInput(text);
    startResearch(text);
  };

  return (
    <div className="p-4 flex flex-col space-y-4">
      {/* Query Search Form */}
      <form onSubmit={handleSearchSubmit} className="relative">
        <div className="relative rounded-xl overflow-hidden glass-panel border border-slate-800 focus-within:border-emerald-500/50 focus-within:shadow-[0_0_15px_rgba(16,185,129,0.1)] transition-all duration-300">
          <input
            type="text"
            value={queryInput}
            onChange={(e) => {
              setQueryInput(e.target.value);
              if (error) setError(null);
            }}
            disabled={isResearching}
            placeholder="Describe your research topic or query..."
            className="w-full pl-4 pr-12 py-3 bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={isResearching || !queryInput.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-900 border border-emerald-400/20 disabled:border-slate-800 disabled:opacity-40 text-slate-950 disabled:text-slate-600 transition-all duration-200 active:scale-95 disabled:active:scale-100"
          >
            {isResearching ? (
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>

      {/* Network Error display */}
      {error && (
        <div className="p-3 rounded-lg border border-red-500/30 bg-red-950/20 text-red-400 text-xs flex items-start gap-2 animate-fade-in">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Execution Error: </span>
            {error}
          </div>
        </div>
      )}

      {/* Query Suggestions List */}
      {!isResearching && (
        <div className="space-y-2">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center">
            <Sparkles className="w-3 h-3 mr-1 text-emerald-400 animate-float" />
            Suggested Research Queries
          </div>
          <div className="flex flex-col gap-1.5">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSuggestionClick(s)}
                className="text-left px-3 py-2 rounded-lg text-[11px] font-medium text-slate-400 hover:text-white bg-slate-900/40 hover:bg-slate-900 border border-slate-900 hover:border-slate-800 transition-all duration-150 leading-relaxed truncate"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
