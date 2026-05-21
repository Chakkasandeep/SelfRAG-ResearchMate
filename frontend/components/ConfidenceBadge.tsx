import React from "react";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface ConfidenceBadgeProps {
  verdict: "Fully Supported" | "Partially Supported" | "Not Supported";
  reason?: string;
  size?: "sm" | "md";
}

export default function ConfidenceBadge({ verdict, reason, size = "sm" }: ConfidenceBadgeProps) {
  const styles = {
    "Fully Supported": "badge-emerald hover:bg-emerald-500/10",
    "Partially Supported": "badge-amber hover:bg-amber-500/10",
    "Not Supported": "badge-red hover:bg-red-500/10"
  };

  const icons = {
    "Fully Supported": <CheckCircle2 className="w-3 h-3 mr-1 inline-block" />,
    "Partially Supported": <AlertTriangle className="w-3 h-3 mr-1 inline-block" />,
    "Not Supported": <XCircle className="w-3 h-3 mr-1 inline-block" />
  };

  return (
    <span
      className={`inline-flex items-center select-none font-semibold rounded-full border px-2.5 py-0.5 text-[10px] cursor-help transition-all duration-300 ${styles[verdict]}`}
      title={reason || verdict}
    >
      {icons[verdict]}
      {verdict}
    </span>
  );
}
