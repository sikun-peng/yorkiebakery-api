import { useState } from "react";
import { API_BASE } from "../config";

const PRESETS = [
  {
    id: "pastryTop",
    label: "Top pastries + reviews",
    query: `
{
  menuItems(category: "pastry", limit: 3) {
    id
    title
    price
    tags
    reviews(limit: 2) {
      rating
      comment
      user { name }
    }
  }
}
    `,
  },
  {
    id: "chefSpecials",
    label: "Chef specials (by tag)",
    query: `
{
  menuItems(limit: 5, tags: ["chef special"]) {
    id
    title
    price
    tags
  }
}
    `,
  },
  {
    id: "lightFilters",
    label: "Filter by category + tag",
    query: `
{
  menuItems(category: "appetizer", tags: ["spicy"], limit: 5) {
    id
    title
    price
    tags
  }
}
    `,
  },
  {
    id: "appetizerSpicy",
    label: "Spicy appetizers",
    query: `
{
  menuItems(category: "appetizer", tags: ["spicy"], limit: 5) {
    id
    title
    price
    tags
  }
}
    `,
  },
  {
    id: "desserts",
    label: "Desserts (first 5)",
    query: `
{
  menuItems(category: "dessert", limit: 5, offset: 0) {
    id
    title
    price
    tags
  }
}
    `,
  },
  {
    id: "withReviews",
    label: "Pastries with 2 reviews",
    query: `
{
  menuItems(category: "pastry", limit: 4) {
    id
    title
    price
    reviews(limit: 2) {
      rating
      comment
      user { name }
    }
  }
}
    `,
  },
  {
    id: "custom",
    label: "Custom (editable below)",
    query: `
{
  menuItems(limit: 3) {
    id
    title
    price
  }
}
    `,
  },
];

export default function GraphQLPanel() {
  const [selected, setSelected] = useState(PRESETS[0].id);
  const [customQuery, setCustomQuery] = useState(PRESETS.find(p => p.id === "custom")?.query.trim() || "");
  const [output, setOutput] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runQuery = async () => {
    const preset = PRESETS.find((p) => p.id === selected);
    if (!preset) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/graphql`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ query: selected === "custom" ? customQuery : preset.query }),
      });
      const data = await res.json();
      if (data.errors) {
        setError(data.errors.map((e: any) => e.message).join("; "));
      }
      setOutput(data);
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="yorkie-card space-y-3">
      <h3 className="font-semibold text-yorkieBrown text-lg">GraphQL Demo</h3>
      <p className="text-sm text-gray-600 leading-relaxed">
        Fetch menu data via <code>/graphql</code>. Pick a preset query, run it, and inspect the JSON response.
      </p>

      <div className="space-y-2">
        <label className="text-sm font-semibold text-yorkieBrown">Preset</label>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="w-full border rounded px-2 py-2 text-sm"
        >
          {PRESETS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
      </div>

      <button
        className="w-full justify-center text-lg py-3 rounded-xl font-semibold text-yorkieBrown bg-gradient-to-r from-amber-300 to-amber-500 shadow-md hover:shadow-lg transition active:translate-y-px disabled:opacity-60 disabled:cursor-not-allowed"
        onClick={runQuery}
        disabled={loading}
      >
        {loading ? "Running…" : "▶ Run GraphQL Query"}
      </button>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-2 py-2">
          {error}
        </div>
      )}

      <details className="bg-gray-50 border border-gray-200 rounded p-2 text-xs">
        <summary className="cursor-pointer font-semibold text-yorkieBrown">
          View query
        </summary>
        <textarea
          className="w-full bg-gray-100 p-2 rounded text-gray-700 font-mono text-xs"
          style={{ minHeight: "160px" }}
          value={selected === "custom" ? customQuery : (PRESETS.find((p) => p.id === selected)?.query.trim() || "")}
          onChange={(e) => {
            if (selected === "custom") {
              setCustomQuery(e.target.value);
              setOutput(null);
              setError(null);
            }
          }}
          disabled={selected !== "custom"}
        />
      </details>

      <details className="bg-gray-50 border border-gray-200 rounded p-2 text-xs">
        <summary className="cursor-pointer font-semibold text-yorkieBrown">
          Response JSON
        </summary>
        <pre className="whitespace-pre-wrap break-words mt-2 text-gray-700">
          {JSON.stringify(output || {}, null, 2)}
        </pre>
      </details>
    </section>
  );
}
