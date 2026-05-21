import React from "react";
import { useResearchStore } from "@/store/researchStore";
import { X, ExternalLink, BookOpen, Bookmark } from "lucide-react";

export default function CitationSidePanel() {
  const { selectedPaper, setSelectedPaper } = useResearchStore();

  if (!selectedPaper) return null;

  return (
    <div className="absolute inset-y-0 right-0 w-80 glass-panel-heavy z-40 shadow-2xl border-l border-slate-800/80 p-5 flex flex-col transition-all duration-300 transform translate-x-0 animate-fade-in">
      {/* Panel header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-900 mb-4">
        <div className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest">
          <BookOpen className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
          Paper Reference Details
        </div>
        <button
          onClick={() => setSelectedPaper(null)}
          className="p-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-all duration-150"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Panel scrollable content */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {/* Paper title */}
        <div>
          <h3 className="text-sm font-bold text-white leading-snug hover:text-emerald-400 transition-colors duration-200">
            {selectedPaper.title}
          </h3>
        </div>

        {/* Paper metadata metadata badges */}
        <div className="space-y-1.5 p-3 rounded-lg bg-slate-900/60 border border-slate-900/80 text-[11px] font-mono text-slate-300">
          <div>
            <span className="text-slate-500 font-semibold mr-1">Authors:</span>
            {selectedPaper.authors}
          </div>
          <div className="flex gap-4">
            <div>
              <span className="text-slate-500 font-semibold mr-1">Year:</span>
              {selectedPaper.year || "n.d."}
            </div>
            <div>
              <span className="text-slate-500 font-semibold mr-1">Catalog:</span>
              <span className="text-emerald-400 font-bold">{selectedPaper.source}</span>
            </div>
          </div>
          <div>
            <span className="text-slate-500 font-semibold mr-1">Paper ID:</span>
            {selectedPaper.id}
          </div>
        </div>

        {/* Paper abstract header */}
        <div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center">
            <Bookmark className="w-3 h-3 mr-1 text-indigo-400" />
            Abstract / Background
          </div>
          <p className="text-xs leading-relaxed text-slate-300 text-justify bg-slate-950/40 p-3 rounded-xl border border-slate-900">
            {selectedPaper.abstract}
          </p>
        </div>
      </div>

      {/* Panel footer button */}
      {selectedPaper.url && (
        <div className="pt-4 border-t border-slate-900">
          <a
            href={selectedPaper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center w-full px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-95 transition-all duration-200"
          >
            <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
            Access Publisher Link
          </a>
        </div>
      )}
    </div>
  );
}
