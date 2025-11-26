import React, { useState } from "react";
import { API_BASE } from "../config";

interface Props {
  setTrace: (trace: any) => void;
}

export default function AIInput({ setTrace }: Props) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const examplePrompts = [
    "Recommend something fruity",
    "Show me Taiwanese desserts",
    "Find pastry under $10",
    "Suggest something with matcha",
    "What’s similar to macarons?",
  ];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/ai/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      console.log("AI response:", data);

      setTrace({
        query: data.query,
        filters: data.filters,
        retrieved_items: data.items,
        raw: data,
      });
    } catch (err) {
      console.error("AIInput error:", err);
    }

    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="yorkie-card w-full flex flex-col space-y-3">
      <label className="font-semibold text-yorkieBrown text-lg">
        Ask Yorkie something:
      </label>

      <input
        type="text"
        placeholder="e.g. 'Recommend something fruity'"
        className="border border-[var(--yorkie-border)] rounded-xl p-3 w-full focus:ring-2 focus:ring-yellow-300 shadow-sm bg-white"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <div className="flex flex-wrap gap-2 text-sm">
        {examplePrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => setMessage(prompt)}
            className="pill-btn"
          >
            {prompt}
          </button>
        ))}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="primary-btn disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Ask"}
      </button>
    </form>
  );
}
