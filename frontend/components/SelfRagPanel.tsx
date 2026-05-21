import React, { useEffect, useRef } from "react";
import { useResearchStore, Verdict } from "@/store/researchStore";
import ConfidenceBadge from "./ConfidenceBadge";
import { Terminal, Shield, Cpu, RefreshCw, Layers } from "lucide-react";

export default function SelfRagPanel() {
  const { stage, verdicts, isResearching } = useResearchStore();
  const consoleEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal log to bottom as new claims verify
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [verdicts, stage]);

  const stagesDef = [
    { key: "plan", label: "Planning", icon: <Layers className="w-3.5 h-3.5" /> },
    { key: "retrieve", label: "Harvesting", icon: <Layers className="w-3.5 h-3.5" /> },
    { key: "summarize", label: "Drafting", icon: <Layers className="w-3.5 h-3.5" /> },
    { key: "critique", label: "Self-RAG Critique", icon: <Shield className="w-3.5 h-3.5" /> },
    { key: "gap_detect", label: "Gap Checks", icon: <RefreshCw className="w-3.5 h-3.5" /> },
    { key: "synthesize", label: "Synthesis", icon: <Cpu className="w-3.5 h-3.5" /> }
  ];

  const getStageClass = (stepKey: string) => {
    if (stage === stepKey) return "text-emerald-400 font-bold border-emerald-500 bg-emerald-500/10 shadow-[0_0_8px_rgba(16,185,129,0.15)] animate-pulse-fast";
    
    // Check if stage is subsequent
    const keys = stagesDef.map(s => s.key);
    const currIdx = keys.indexOf(stage);
    const stepIdx = keys.indexOf(stepKey);
    
    if (currIdx > stepIdx && stage !== "error" && stage !== "idle") {
      return "text-emerald-500 border-emerald-500 bg-emerald-500/5 opacity-70";
    }
    
    return "text-slate-500 border-slate-800 bg-slate-900/40 opacity-40";
  };

  return (
    <div className="flex flex-col flex-1 p-4 overflow-hidden border-t border-slate-800/80 bg-slate-950/70 backdrop-blur-md">
      {/* Dynamic Agent Graph Progress Indicator */}
      {isResearching && (
        <div className="mb-4">
          <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2.5 flex items-center">
            <Cpu className="w-3 h-3 mr-1 text-emerald-400" />
            Agent Orchestrator Pipeline
          </h3>
          <div className="grid grid-cols-6 gap-1 border-b border-slate-900 pb-3">
            {stagesDef.map((s) => (
              <div
                key={s.key}
                className={`flex flex-col items-center justify-center p-1.5 rounded-lg border text-center transition-all duration-300 ${getStageClass(
                  s.key
                )}`}
              >
                <div className="mb-1">{s.icon}</div>
                <span className="text-[8px] font-bold tracking-tight leading-none truncate max-w-full">
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Terminal fact checker feed header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center text-xs font-semibold text-slate-300">
          <Terminal className="w-3.5 h-3.5 mr-1.5 text-indigo-400" />
          Self-RAG Critique Feed
        </div>
        {isResearching && (
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
        )}
      </div>

      {/* Terminal logs list */}
      <div className="flex-1 overflow-y-auto rounded-xl p-3 bg-slate-950 border border-slate-900 text-xs font-mono space-y-2.5 shadow-inner">
        {verdicts.map((v, idx) => (
          <div
            key={idx}
            className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/40 hover:border-slate-800 transition-all duration-200"
          >
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <ConfidenceBadge verdict={v.verdict} reason={v.reason} />
              {v.source_id && (
                <span className="text-[9px] font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-1.5 py-0.5 rounded">
                  {v.source_id}
                </span>
              )}
            </div>
            <p className="text-slate-300 text-[11px] leading-relaxed break-words font-sans">
              "{v.claim}"
            </p>
            {v.reason && (
              <p className="text-[10px] text-slate-500 mt-1 pl-1 border-l border-slate-800 italic font-sans leading-none">
                Reason: {v.reason}
              </p>
            )}
          </div>
        ))}

        {verdicts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-6 text-slate-600">
            <Terminal className="w-8 h-8 mb-2 opacity-25" />
            {isResearching ? (
              <p className="text-[11px] italic animate-pulse">
                Orchestrating agent workflows... Waiting for critique verdicts.
              </p>
            ) : (
              <p className="text-[11px] italic">
                Initialize query to run LangGraph Self-RAG fact-checks.
              </p>
            )}
          </div>
        )}
        <div ref={consoleEndRef} />
      </div>
    </div>
  );
}
