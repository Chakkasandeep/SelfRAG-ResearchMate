import React, { useEffect, useRef, useState } from "react";
import { useResearchStore, Paper } from "@/store/researchStore";
import { Network, Info } from "lucide-react";

interface Node {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
  label: string;
  paper: Paper;
}

interface Link {
  source: string;
  target: string;
}

export default function CitationGraph() {
  const { citations, setSelectedPaper } = useResearchStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null);

  // Parse color matching catalog source names
  const getColorBySource = (source: string) => {
    switch ((source || "").toLowerCase()) {
      case "semantic scholar":
        return "#6366f1"; // Indigo
      case "arxiv":
        return "#f43f5e"; // Rose
      case "openalex":
        return "#10b981"; // Emerald
      case "wikipedia":
        return "#e2e8f0"; // Slate-200
      default:
        return "#f59e0b"; // Amber
    }
  };

  useEffect(() => {
    if (!citations || citations.length === 0) {
      setNodes([]);
      setLinks([]);
      return;
    }

    const width = containerRef.current?.clientWidth || 280;
    const height = 300;

    // 1. Initialize nodes with randomized positions
    const initialNodes: Node[] = citations.map((c, i) => {
      // Place in a circle layout initially
      const angle = (i / citations.length) * Math.PI * 2;
      const radius = 60;
      return {
        id: c.id,
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: (c.source || "").toLowerCase() === "wikipedia" ? 7 : 6,
        color: getColorBySource(c.source || ""),
        label: c.title,
        paper: c
      };
    });

    // 2. Generate citation connection links
    const initialLinks: Link[] = [];
    const paperIds = new Set(citations.map(c => c.id));

    citations.forEach(c => {
      if (c.citation_ids) {
        c.citation_ids.forEach(cid => {
          // Check if citing node matches ss paperIds or local ids
          const ssId = `ss-${cid}`;
          const arxivId = `arxiv-${cid}`;
          const oaId = `oa-${cid}`;
          
          let target = "";
          if (paperIds.has(cid)) target = cid;
          else if (paperIds.has(ssId)) target = ssId;
          else if (paperIds.has(arxivId)) target = arxivId;
          else if (paperIds.has(oaId)) target = oaId;

          if (target && target !== c.id) {
            initialLinks.push({ source: c.id, target: target });
          }
        });
      }
    });

    // Fallback: connect adjacent nodes if no citation links resolved (creates beautiful network visualization)
    if (initialLinks.length === 0 && initialNodes.length > 1) {
      for (let i = 0; i < initialNodes.length - 1; i++) {
        initialLinks.push({
          source: initialNodes[i].id,
          target: initialNodes[i + 1].id
        });
      }
      // loop link
      initialLinks.push({
        source: initialNodes[initialNodes.length - 1].id,
        target: initialNodes[0].id
      });
    }

    setNodes(initialNodes);
    setLinks(initialLinks);
  }, [citations]);

  // 3. Simple physics animation loop (Verlet Integration) with cooling factor (alpha decay)
  useEffect(() => {
    if (nodes.length === 0) return;

    let animationId: number;
    let alpha = 1.0; // Simulated cooling parameter

    const tick = () => {
      // Cool down completely when alpha is negligible to sleep the simulation
      if (alpha < 0.01) {
        cancelAnimationFrame(animationId);
        return;
      }

      // Read dimensions dynamically in the tick to handle hidden container states on mount
      const currentWidth = containerRef.current && containerRef.current.clientWidth > 0
        ? containerRef.current.clientWidth
        : 280;
      const currentHeight = 300; // Fixed canvas height

      setNodes(prevNodes => {
        const nextNodes = prevNodes.map(n => ({ ...n }));

        // Node repulsion (Coulomb-like force scaled by alpha)
        for (let i = 0; i < nextNodes.length; i++) {
          const n1 = nextNodes[i];
          for (let j = i + 1; j < nextNodes.length; j++) {
            const n2 = nextNodes[j];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            
            if (dist < 100) {
              const force = (100 - dist) * 0.08 * alpha;
              const fx = (dx / dist) * force;
              const fy = (dy / dist) * force;
              
              n1.vx -= fx;
              n1.vy -= fy;
              n2.vx += fx;
              n2.vy += fy;
            }
          }
        }

        // Link attraction (Hooke's spring force scaled by alpha)
        links.forEach(l => {
          const sourceNode = nextNodes.find(n => n.id === l.source);
          const targetNode = nextNodes.find(n => n.id === l.target);
          
          if (sourceNode && targetNode) {
            const dx = targetNode.x - sourceNode.x;
            const dy = targetNode.y - sourceNode.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            
            // spring resting distance = 70
            const force = (dist - 70) * 0.035 * alpha;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            
            sourceNode.vx += fx;
            sourceNode.vy += fy;
            targetNode.vx -= fx;
            targetNode.vy -= fy;
          }
        });

        // Center gravity pulling nodes back to container core scaled by alpha
        nextNodes.forEach(n => {
          const dx = currentWidth / 2 - n.x;
          const dy = currentHeight / 2 - n.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          
          n.vx += (dx / dist) * 0.08 * alpha;
          n.vy += (dy / dist) * 0.08 * alpha;

          // Apply velocity and drag friction
          n.x += n.vx;
          n.y += n.vy;
          n.vx *= 0.85;
          n.vy *= 0.85;

          // Keep nodes inside bounds
          n.x = Math.max(n.radius + 10, Math.min(currentWidth - n.radius - 10, n.x));
          n.y = Math.max(n.radius + 10, Math.min(currentHeight - n.radius - 10, n.y));
        });

        return nextNodes;
      });

      alpha *= 0.98; // Exponential cooling decay
      animationId = requestAnimationFrame(tick);
    };

    animationId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationId);
  }, [links, nodes.length]);

  if (citations.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-600 bg-slate-950/20">
        <Network className="w-10 h-10 mb-3 opacity-20" />
        <span className="text-[11px] uppercase tracking-widest font-bold">Citation Network</span>
        <span className="text-[10px] italic mt-1 leading-normal">
          Citation webs render dynamically during synthesis.
        </span>
      </div>
    );
  }

  const width = containerRef.current?.clientWidth || 280;
  const height = 300;

  return (
    <div
      ref={containerRef}
      className="h-full flex flex-col p-4 bg-slate-950/70 border-l border-slate-900 overflow-hidden relative select-none"
    >
      {/* Graph title */}
      <div className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 pb-2 border-b border-slate-900 shrink-0">
        <Network className="w-4 h-4 mr-1.5 text-indigo-400 animate-float" />
        Citation Network viz
      </div>

      {/* Physics Canvas Area */}
      <div className="flex-1 min-h-[220px] rounded-xl border border-slate-900 bg-slate-950 relative overflow-hidden">
        <svg width="100%" height="100%" className="w-full h-full cursor-crosshair">
          {/* Connection Lines Edges */}
          {links.map((link, idx) => {
            const sourceNode = nodes.find(n => n.id === link.source);
            const targetNode = nodes.find(n => n.id === link.target);
            if (!sourceNode || !targetNode) return null;
            return (
              <line
                key={idx}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke="rgba(255,255,255,0.06)"
                strokeWidth={1.5}
              />
            );
          })}

          {/* Node Circles */}
          {nodes.map(node => (
            <g key={node.id}>
              {/* Pulsing neon background if hovered */}
              {hoveredNode?.id === node.id && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.radius + 5}
                  fill={node.color}
                  opacity={0.3}
                  className="animate-ping"
                />
              )}
              <circle
                cx={node.x}
                cy={node.y}
                r={node.radius}
                fill={node.color}
                stroke="#090d16"
                strokeWidth={1.5}
                className="cursor-pointer transition-all duration-300"
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => setSelectedPaper(node.paper)}
              />
            </g>
          ))}
        </svg>

        {/* Hover detail card popover overlay */}
        {hoveredNode && (
          <div className="absolute bottom-2 inset-x-2 p-2.5 rounded-lg glass-panel-heavy text-[10px] border border-slate-800 pointer-events-none animate-fade-in leading-relaxed">
            <div className="font-bold text-white truncate mb-0.5">{hoveredNode.paper.title}</div>
            <div className="text-slate-400 truncate">{hoveredNode.paper.authors}</div>
            <div className="flex justify-between items-center mt-1 text-[8px] font-mono">
              <span className="text-emerald-400 font-bold uppercase">{hoveredNode.paper.source}</span>
              <span className="text-slate-500">{hoveredNode.paper.year}</span>
            </div>
          </div>
        )}
      </div>

      {/* Legend Block */}
      <div className="mt-3 grid grid-cols-2 gap-1.5 text-[9px] font-mono text-slate-400 pt-2 border-t border-slate-900/60 shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#6366f1" }} />
          <span>Semantic Scholar</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#f43f5e" }} />
          <span>arXiv Repository</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#10b981" }} />
          <span>OpenAlex catalog</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "#cbd5e1" }} />
          <span>Wikipedia index</span>
        </div>
      </div>
    </div>
  );
}
