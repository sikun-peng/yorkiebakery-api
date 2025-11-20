import React, { useState } from "react";

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
      const res = await fetch("http://localhost:8000/ai/demo", {
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
    <form
      onSubmit={handleSubmit}
      className="yorkie-card w-full flex flex-col space-y-3"
    >
      <label className="font-semibold text-yorkieBrown">
        Ask Yorkie something:
      </label>

      <input
        type="text"
        placeholder="e.g. 'Recommend something fruity'"
        className="border border-gray-300 rounded-lg p-3 w-full focus:ring-2 focus:ring-yellow-300"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      {/* ---- Example Prompts ---- */}
      <div className="flex flex-wrap gap-2 text-sm">
        {examplePrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => setMessage(prompt)}
            className="px-3 py-1 rounded-full bg-amber-100 border border-amber-300
                       text-yorkieBrown hover:bg-amber-200 shadow-sm transition"
          >
            {prompt}
          </button>
        ))}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-yellow-300 hover:bg-yellow-400 text-yorkieBrown font-bold py-2 px-4 rounded-lg transition disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Ask"}
      </button>
    </form>
  );
}