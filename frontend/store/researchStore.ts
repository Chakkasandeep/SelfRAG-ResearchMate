import { create } from "zustand";

export interface Paper {
  id: string;
  title: string;
  authors: string;
  year?: number;
  abstract: string;
  url: string;
  source: string;
  citation_ids?: string[];
}

export interface Verdict {
  claim: string;
  verdict: "Fully Supported" | "Partially Supported" | "Not Supported";
  source_id: string | null;
  reason?: string;
}

export type PipelineStage = "idle" | "plan" | "retrieve" | "summarize" | "critique" | "gap_detect" | "synthesize" | "error";

interface ResearchState {
  stage: PipelineStage;
  query: string;
  subtopics: string[];
  papers: Paper[];
  draft: string;
  verdicts: Verdict[];
  review: string;
  citations: Paper[];
  isResearching: boolean;
  selectedPaper: Paper | null;
  activeCitationId: string | null;
  error: string | null;
  
  // Actions
  setStage: (stage: PipelineStage) => void;
  setQuery: (query: string) => void;
  setSubtopics: (subtopics: string[]) => void;
  setPapers: (papers: Paper[]) => void;
  setDraft: (draft: string) => void;
  addVerdict: (verdict: Verdict) => void;
  clearVerdicts: () => void;
  setReview: (review: string) => void;
  setCitations: (citations: Paper[]) => void;
  setSelectedPaper: (paper: Paper | null) => void;
  setActiveCitationId: (citationId: string | null) => void;
  setResearching: (isResearching: boolean) => void;
  setError: (error: string | null) => void;
  resetStore: () => void;
}

export const useResearchStore = create<ResearchState>((set) => ({
  stage: "idle",
  query: "",
  subtopics: [],
  papers: [],
  draft: "",
  verdicts: [],
  review: "",
  citations: [],
  isResearching: false,
  selectedPaper: null,
  activeCitationId: null,
  error: null,

  setStage: (stage) => set({ stage }),
  setQuery: (query) => set({ query }),
  setSubtopics: (subtopics) => set({ subtopics }),
  setPapers: (papers) => set({ papers }),
  setDraft: (draft) => set({ draft }),
  addVerdict: (verdict) => set((state) => {
    // Avoid duplicate claims in panel feed
    if (state.verdicts.some(v => v.claim === verdict.claim)) {
      return {};
    }
    return { verdicts: [...state.verdicts, verdict] };
  }),
  clearVerdicts: () => set({ verdicts: [] }),
  setReview: (review) => set({ review }),
  setCitations: (citations) => set({ citations }),
  setSelectedPaper: (paper) => set({ selectedPaper: paper }),
  setActiveCitationId: (citationId) => set({ activeCitationId: citationId }),
  setResearching: (isResearching) => set({ isResearching }),
  setError: (error) => set({ error, stage: error ? "error" : "idle" }),
  resetStore: () => set({
    stage: "idle",
    query: "",
    subtopics: [],
    papers: [],
    draft: "",
    verdicts: [],
    review: "",
    citations: [],
    isResearching: false,
    selectedPaper: null,
    activeCitationId: null,
    error: null,
  }),
}));
