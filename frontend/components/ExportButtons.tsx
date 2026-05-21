import React, { useState } from "react";
import { FileText, Presentation, Download, Loader2 } from "lucide-react";
import { useResearchStore } from "@/store/researchStore";
import { downloadPDF, downloadPPTX } from "@/lib/api";
import { exportReviewToPDF } from "@/lib/pdfExport";

export default function ExportButtons() {
  const { review, citations } = useResearchStore();
  const [exportingPDF, setExportingPDF] = useState(false);
  const [exportingPPT, setExportingPPT] = useState(false);
  const [exportingClientPDF, setExportingClientPDF] = useState(false);

  const handleServerPDF = async () => {
    if (!review) return;
    setExportingPDF(true);
    try {
      await downloadPDF(review, citations);
    } catch (e) {
      alert("Failed to export PDF from backend server. Trying client-side fallback...");
      await handleClientPDF();
    } finally {
      setExportingPDF(false);
    }
  };

  const handleClientPDF = async () => {
    setExportingClientPDF(true);
    try {
      await exportReviewToPDF("literature-review-doc");
    } finally {
      setExportingClientPDF(false);
    }
  };

  const handleServerPPT = async () => {
    if (!review) return;
    setExportingPPT(true);
    try {
      await downloadPPTX(review, citations);
    } catch (e) {
      alert("Failed to export PowerPoint presentation from server.");
    } finally {
      setExportingPPT(false);
    }
  };

  if (!review) return null;

  return (
    <div className="flex flex-wrap gap-2.5 mb-6 items-center p-3 rounded-xl glass-card">
      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-2">
        Export Options:
      </span>
      
      {/* Server PDF */}
      <button
        onClick={handleServerPDF}
        disabled={exportingPDF}
        className="flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all duration-200"
      >
        {exportingPDF ? (
          <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
        ) : (
          <FileText className="w-3.5 h-3.5 mr-1.5" />
        )}
        Report PDF
      </button>

      {/* Client PDF */}
      <button
        onClick={handleClientPDF}
        disabled={exportingClientPDF}
        className="flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all duration-200 border border-slate-700"
      >
        {exportingClientPDF ? (
          <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
        ) : (
          <Download className="w-3.5 h-3.5 mr-1.5" />
        )}
        Print PDF (Client)
      </button>

      {/* Server PPT */}
      <button
        onClick={handleServerPPT}
        disabled={exportingPPT}
        className="flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 disabled:opacity-50 disabled:active:scale-100 transition-all duration-200"
      >
        {exportingPPT ? (
          <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
        ) : (
          <Presentation className="w-3.5 h-3.5 mr-1.5" />
        )}
        Slide Deck PPTX
      </button>
    </div>
  );
}
