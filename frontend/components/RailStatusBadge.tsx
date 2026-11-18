import React from "react";
import { Shield, ShieldAlert } from "lucide-react";
import { useResearchStore } from "@/store/researchStore";

export default function RailStatusBadge() {
  const railStatus = useResearchStore((state) => state.railStatus);

  if (railStatus?.blocked) {
    return (
      <div className="inline-flex items-center rounded-full border border-red-500/30 bg-red-500/10 px-2 py-1 text-[9px] font-bold text-red-300">
        <ShieldAlert className="mr-1 h-3 w-3" />
        Blocked at {railStatus.stage}
      </div>
    );
  }

  return (
    <div className="inline-flex items-center rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-1 text-[9px] font-bold text-emerald-300">
      <Shield className="mr-1 h-3 w-3" />
      Guardrails: active
    </div>
  );
}
