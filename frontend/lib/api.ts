const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function downloadPDF(review: string, citations: any[]): Promise<void> {
  const response = await fetch(`${API_BASE}/api/export/pdf`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ review, citations }),
  });

  if (!response.ok) {
    throw new Error("Failed to export PDF from server.");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "Literature_Review_Report.pdf";
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadPPTX(review: string, citations: any[]): Promise<void> {
  const response = await fetch(`${API_BASE}/api/export/pptx`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ review, citations }),
  });

  if (!response.ok) {
    throw new Error("Failed to export PowerPoint slide deck from server.");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "Literature_Review_Deck.pptx";
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
