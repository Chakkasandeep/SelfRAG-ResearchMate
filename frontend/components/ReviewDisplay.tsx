import React from "react";
import { useResearchStore, Paper } from "@/store/researchStore";
import { Award, BookOpen, ExternalLink, Calendar } from "lucide-react";

interface ReviewDisplayProps {
  review: string;
  citations: Paper[];
}

export default function ReviewDisplay({ review, citations = [] }: ReviewDisplayProps) {
  const { setSelectedPaper, papers } = useResearchStore();

  const handleCitationClick = (paperId: string) => {
    // Find the paper in the active citation or papers list
    const safeCitations = citations || [];
    const found = papers.find(p => p.id === paperId) || safeCitations.find(p => p.id === paperId);
    if (found) {
      setSelectedPaper(found);
    }
  };

  // Helper custom parser to translate Markdown strings and [cite:id] tags to React elements safely
  const parseMarkdown = (text: string) => {
    if (!text) return null;
    
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      let trimmed = line.trim();
      if (!trimmed) return <div key={idx} className="h-3" />;

      // 1. Headers H1
      if (trimmed.startsWith("# ")) {
        return (
          <h1 key={idx} className="text-xl md:text-2xl font-bold text-white border-b border-slate-900 pb-2.5 mt-6 mb-4">
            {_parseInlineFormatting(trimmed.replace("# ", ""))}
          </h1>
        );
      }

      // 2. Headers H2
      if (trimmed.startsWith("## ")) {
        return (
          <h2 key={idx} className="text-base md:text-lg font-bold text-emerald-400 mt-6 mb-3">
            {_parseInlineFormatting(trimmed.replace("## ", ""))}
          </h2>
        );
      }

      // 3. Headers H3
      if (trimmed.startsWith("### ")) {
        return (
          <h3 key={idx} className="text-sm font-bold text-white mt-4 mb-2">
            {_parseInlineFormatting(trimmed.replace("### ", ""))}
          </h3>
        );
      }

      // 4. Standard Paragraph
      return (
        <p key={idx} className="text-xs md:text-sm text-slate-300 leading-relaxed mb-4 text-justify">
          {_parseInlineFormatting(trimmed)}
        </p>
      );
    });
  };

  const _parseInlineFormatting = (text: string) => {
    if (typeof text !== "string") return "";
    // Escape HTML tags to protect integrity
    let safe = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Find bold and italics
    // Split text by cite tags: [cite:some_id]
    const parts = safe.split(/(\[cite:[^\]]+\])/g);
    
    const elements = parts.map((part, i) => {
      const citeMatch = part.match(/\[cite:([^\]]+)\]/);
      if (citeMatch) {
        const paperId = citeMatch[1].trim();
        const safeCitations = citations || [];
        
        // Resolve a short name tag (e.g. index position of citation)
        const citeIndex = safeCitations.findIndex(c => c.id === paperId) + 1;
        const displayName = citeIndex > 0 ? `[${citeIndex}]` : `[Reference]`;
        
        return (
          <button
            key={`cite-${i}-${paperId}`}
            onClick={() => handleCitationClick(paperId)}
            className="px-1.5 py-0.5 mx-0.5 text-[9px] font-bold text-indigo-400 bg-indigo-500/10 hover:bg-indigo-500/20 active:scale-95 border border-indigo-500/20 rounded transition-all duration-150 inline-flex items-center align-middle"
            title={`View citation metadata for ${paperId}`}
          >
            <BookOpen className="w-2.5 h-2.5 mr-0.5" />
            {displayName}
          </button>
        );
      }
      
      // Basic Bold/Italic parser for raw elements
      // Matches **text** -> Bold
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bp, bpIdx) => {
        if (bp.startsWith("**") && bp.endsWith("**")) {
          return (
            <strong key={`bold-${i}-${bpIdx}`} className="font-bold text-white">
              {bp.slice(2, -2)}
            </strong>
          );
        }
        
        // Matches *text* -> Italic
        const italicParts = bp.split(/(\*[^*]+\*)/g);
        return italicParts.map((ip, ipIdx) => {
          if (ip.startsWith("*") && ip.endsWith("*")) {
            return (
              <em key={`italic-${i}-${bpIdx}-${ipIdx}`} className="italic text-slate-200">
                {ip.slice(1, -1)}
              </em>
            );
          }
          return ip;
        });
      });
    });

    return elements.flat(Infinity);
  };

  return (
    <div
      id="literature-review-doc"
      className="p-6 md:p-8 rounded-2xl border border-slate-800/80 bg-[#090d16]/75 backdrop-blur-lg shadow-xl relative overflow-hidden"
    >
      {/* Decorative top-right badge */}
      <div className="absolute top-4 right-4 flex items-center text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.1)] select-none">
        <Award className="w-3.5 h-3.5 mr-1" />
        SELF-RAG VERIFIED
      </div>

      {/* Structured review content */}
      <div className="prose prose-invert max-w-none">
        {parseMarkdown(review)}
      </div>

      {/* Dynamic References List block */}
      {citations.length > 0 && (
        <div className="mt-8 pt-6 border-t border-slate-900 select-text">
          <h2 className="text-sm font-bold text-emerald-400 mb-4 flex items-center uppercase tracking-widest">
            <BookOpen className="w-4 h-4 mr-2" />
            Academic Bibliography
          </h2>
          <div className="space-y-4">
            {citations.map((c, idx) => (
              <div
                key={c.id}
                onClick={() => setSelectedPaper(c)}
                className="flex items-start gap-3 p-3 rounded-xl border border-slate-900/60 bg-slate-950/40 hover:border-slate-800/60 hover:bg-slate-900/25 transition-all duration-200 cursor-pointer"
              >
                {/* Index circle */}
                <div className="w-6 h-6 shrink-0 rounded-full flex items-center justify-center text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 shadow-[0_0_8px_rgba(16,185,129,0.05)]">
                  {idx + 1}
                </div>
                
                {/* Reference citation text */}
                <div className="flex-1 space-y-1">
                  <h4 className="text-xs font-bold text-white group-hover:text-emerald-400 transition-colors duration-150 leading-tight">
                    {c.title}
                  </h4>
                  <p className="text-[10px] text-slate-400">
                    {c.authors}
                  </p>
                  <div className="flex items-center gap-4 text-[9px] font-mono text-slate-500 mt-1">
                    <span className="flex items-center">
                      <Calendar className="w-2.5 h-2.5 mr-0.5" />
                      {c.year || "n.d."}
                    </span>
                    <span className="text-indigo-400 font-semibold uppercase">
                      {c.source}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
