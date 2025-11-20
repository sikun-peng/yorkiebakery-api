export async function askYorkieAI(message: string) {
  const resp = await fetch("http://localhost:8000/ai/demo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Server error: ${resp.status} - ${text}`);
  }

  return await resp.json();
}