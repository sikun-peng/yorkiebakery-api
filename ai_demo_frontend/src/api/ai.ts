// src/api/ai.ts

// Auto-detect backend URL
const BASE =
  window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "";  // production → same domain

// ------------------------------
// TEXT QUERY (Chat / RAG)
// ------------------------------
export async function askYorkieAI(query: string) {
  const resp = await fetch(`${BASE}/ai/demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),   // backend expects { query }
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Server error: ${resp.status} ${text}`);
  }

  return await resp.json();
}

// ------------------------------
// IMAGE ANALYSIS (Vision + RAG)
// ------------------------------
export async function analyzeImage(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const resp = await fetch(`${BASE}/ai/vision`, {
    method: "POST",
    body: formData,
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Server error: ${resp.status} ${text}`);
  }

  return await resp.json();
}