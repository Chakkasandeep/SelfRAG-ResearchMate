import { useResearchStore } from "@/store/researchStore";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useSSEStream() {
  const {
    resetStore,
    setStage,
    setQuery,
    setSubtopics,
    setPapers,
    setDraft,
    addVerdict,
    clearVerdicts,
    setReview,
    setCitations,
    setResearching,
    setError
  } = useResearchStore();

  const startResearch = async (query: string) => {
    if (!query.trim()) return;

    // Reset previous research pipeline parameters
    resetStore();
    setQuery(query);
    setResearching(true);
    setStage("plan");

    try {
      const response = await fetch(`${API_BASE}/api/research/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI server returned error status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to initialize stream reader on the client side.");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode binary stream chunks
        buffer += decoder.decode(value, { stream: true });
        
        // Split buffer by SSE newline boundaries
        const lines = buffer.split("\n");
        // Save uncompleted last line back to buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          // SSE format is: event: eventName \n data: JSONString
          if (trimmed.startsWith("data:")) {
            const dataStr = trimmed.replace("data:", "").trim();
            if (!dataStr) continue;

            try {
              const event = JSON.parse(dataStr);
              const { stage, data } = event;

              if (stage) {
                setStage(stage);
              }

              if (stage === "plan" && data?.subtopics) {
                setSubtopics(data.subtopics);
              }
              
              if (stage === "retrieve" && data?.papers) {
                setPapers(data.papers);
              }
              
              if (stage === "summarize" && data?.draft) {
                setDraft(data.draft);
                // Also set temporary review to see live updates
                setReview(data.draft);
              }
              
              if (stage === "critique" && data?.claim_verdicts) {
                clearVerdicts(); // reset list before updating
                data.claim_verdicts.forEach((v: any) => addVerdict(v));
              }
              
              if (stage === "synthesize" && data?.final_review) {
                setReview(data.final_review);
                if (data.citations) {
                  setCitations(data.citations);
                }
                setResearching(false);
              }
            } catch (err) {
              console.warn("Failed to parse streamed SSE event line: ", err);
            }
          }
        }
      }
    } catch (error: any) {
      console.error("Research SSE streaming failed: ", error);
      setError(error.message || "An unexpected network error occurred.");
      setResearching(false);
    }
  };

  return { startResearch };
}
