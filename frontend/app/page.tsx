"use client";
import React from "react";
import ChatInterface from "@/components/ChatInterface";
import SelfRagPanel from "@/components/SelfRagPanel";
import ReviewDisplay from "@/components/ReviewDisplay";
import CitationGraph from "@/components/CitationGraph";
import CitationSidePanel from "@/components/CitationSidePanel";
import ExportButtons from "@/components/ExportButtons";
import { useResearchStore } from "@/store/researchStore";
import { Sparkles, Brain, Cpu, BookOpen, Loader2 } from "lucide-react";

export default function Home() {
  const { stage, review, citations, isResearching, query } = useResearchStore();

  const getStatusText = () => {
    switch (stage) {
      case "plan":
        return "Analyzing research query and mapping subtopics...";
      case "retrieve":
        return "Concurrent API Harvesting (arXiv, Semantic Scholar, OpenAlex)...";
      case "summarize":
        return "Synthesizing research claims and writing first draft...";
      case "critique":
        return "Running Self-RAG sentence-level fact checks...";
      case "gap_detect":
        return "Verifying coverage limits and planning retrieval expansion...";
      case "synthesize":
        return "Assembling, softening claims, and compiling bibliography...";
      default:
        return "Orchestrating autonomous agents...";
    }
  };

  return (
    <main className="h-screen max-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden">
      {/* Dynamic Navigation Header Panel */}
      <header className="border-b border-slate-900/80 px-6 py-4 flex items-center justify-between bg-slate-950/60 backdrop-blur-md z-10 select-none">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 shadow-[0_0_12px_rgba(16,185,129,0.15)] animate-float">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm md:text-base font-bold text-white tracking-wide flex items-center gap-1.5">
              ResearchMate
              <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded-full uppercase tracking-widest">
                v1.1
              </span>
            </h1>
            <p className="text-[10px] text-slate-500 font-medium">
              Zero-Hallucination Agentic Literature Review Assistant
            </p>
          </div>
        </div>

        {/* Floating status badge indicator */}
        {isResearching && (
          <div className="flex items-center gap-2 p-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 shadow-[0_0_10px_rgba(16,185,129,0.05)] animate-pulse-fast">
            <Loader2 className="w-3.5 h-3.5 text-emerald-400 animate-spin" />
            <span className="text-[10px] font-bold font-mono text-emerald-400 uppercase tracking-widest">
              {stage} active
            </span>
          </div>
        )}
      </header>

      {/* Triple Column Workspace Panels Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        
        {/* Left Column Panel: Chat Query Controls + Self-RAG Fact Logger */}
        <div className="w-80 md:w-96 border-r border-slate-900/80 flex flex-col bg-slate-950/40 backdrop-blur-sm z-10 shrink-0">
          <ChatInterface />
          <SelfRagPanel />
        </div>

        {/* Center Column Panel: Synthesized Review Markdown Viewer */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-950/20 z-10 flex flex-col min-w-0">
          {review ? (
            <div className="max-w-4xl mx-auto w-full animate-fade-in pb-12">
              <ExportButtons />
              <ReviewDisplay review={review} citations={citations} />
            </div>
          ) : (
            /* Premium pulsing Glassy Loader placeholder screen if search is executing */
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 max-w-lg mx-auto select-none">
              {isResearching ? (
                <div className="space-y-6 animate-pulse-fast w-full">
                  <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.2)] animate-bounce">
                    <Cpu className="w-8 h-8" />
                  </div>
                  <div className="space-y-3">
                    <h2 className="text-sm font-bold text-white tracking-widest uppercase font-mono">
                      Pipeline State: <span className="text-indigo-400">{stage}</span>
                    </h2>
                    <p className="text-xs text-slate-400 italic">
                      "{query}"
                    </p>
                    <p className="text-xs text-slate-500 font-medium">
                      {getStatusText()}
                    </p>
                  </div>
                  {/* Glassy skeleton paragraphs loaders */}
                  <div className="space-y-2.5 pt-4">
                    <div className="h-3 w-3/4 mx-auto rounded-full bg-slate-900 border border-slate-800" />
                    <div className="h-3 w-5/6 mx-auto rounded-full bg-slate-900 border border-slate-800" />
                    <div className="h-3 w-2/3 mx-auto rounded-full bg-slate-900 border border-slate-800" />
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-14 h-14 mx-auto rounded-2xl flex items-center justify-center text-slate-500 bg-slate-900 border border-slate-800 shadow-inner animate-float">
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <div className="space-y-1.5">
                    <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest">
                      Ready for Research
                    </h2>
                    <p className="text-xs text-slate-500 leading-normal max-w-sm">
                      Type your academic topic in the input panel or click one of the suggested search queries to launch the autonomous agent team.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column Panel: Dynamic Citation Network visualizer */}
        <div className="w-80 border-l border-slate-900/80 bg-slate-950/40 backdrop-blur-sm z-10 shrink-0 relative overflow-hidden hidden lg:block">
          <CitationGraph />
          {/* Absolute overlay glassy side panel Reference details drawer */}
          <CitationSidePanel />
        </div>
        
      </div>
    </main>
  );
}
