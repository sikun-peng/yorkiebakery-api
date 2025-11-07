// static/chat_client.js

async function yorkieSuggest(query) {
  const url = `/ai/suggest?q=${encodeURIComponent(query)}&top_k=5`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Suggest failed: ${res.status}`);
  return await res.json();
}

async function yorkieChat(message) {
  const res = await fetch(`/ai/chat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message, top_k: 5 })
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return await res.json();
}

async function sendMessage() {
  const input = document.getElementById("chat-input");
  const output = document.getElementById("response");

  const text = input.value.trim();
  if (!text) return;

  output.textContent = "Thinking...";

  try {
    // Expecting: { results: [ { menu_item_id, title, price, cuisine, dish_type, ... }, ... ] }
    const result = await yorkieChat(text);
    const items = Array.isArray(result.results) ? result.results : [];

    // Text summary for debugging
    const lines = items.map(it => {
      const price = Number(it.price || 0).toFixed(2);
      return `• ${it.title} — $${price}`;
    });
    output.textContent = `Suggestions:\n${lines.join("\n")}`;

    // Also render rich cards with "Add to cart" buttons (defined in index.html)
    if (typeof window.renderSuggestions === "function") {
      window.renderSuggestions(items);
    }
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
}