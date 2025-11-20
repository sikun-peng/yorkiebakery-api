import type { AIDebugTrace, VisionMatch } from "../types";

interface Props {
  trace: AIDebugTrace | null;
}

export default function AIResponse({ trace }: Props) {
  if (!trace) return null;

  // Standardize backend structure
  const backend = trace.raw || trace;

  // Unified items extraction logic:
  // 1. Vision: backend.matches[]
  // 2. Text query: backend.items[]
  // 3. Fallback: trace.retrieved_items (older behavior)
  const items: VisionMatch[] =
    (backend.matches && backend.matches.length > 0)
      ? backend.matches
      : (backend.items && backend.items.length > 0)
        ? backend.items
        : (trace.retrieved_items || []);

  const summary =
    items.length > 0
      ? `I found ${items.length} items that may match your request.`
      : `No matching menu items were found.`;

  return (
    <section className="yorkie-card space-y-3">
      <h2 className="text-lg font-bold text-yorkieBrown">💬 Yorkie Says</h2>

      {/* Summary line */}
      <p className="text-sm text-gray-700">{summary}</p>

      {/* Query bubble */}
      <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <strong>You asked:</strong>
        <div className="mt-1 italic">{trace.query}</div>
      </div>

      {/* Render result cards */}
      {items.length > 0 && (
        <ul className="mt-3 space-y-2">
          {items.map((item, idx) => (
            <li
              key={idx}
              className="p-3 rounded-lg bg-white border border-gray-200 shadow"
            >
              <div className="font-semibold">{item.title}</div>

              <div className="text-xs text-gray-500">
                {item.origin || "unknown origin"} •{" "}
                {item.category || "unknown category"} •{" "}
                {item.price !== undefined ? `$${item.price}` : "no price"}
              </div>

              {/* Extra bonus: show flavor tags if available */}
              {item.flavor_profiles && (
                <div className="text-xs text-gray-400 mt-1">
                  Flavors: {Array.isArray(item.flavor_profiles)
                    ? item.flavor_profiles.join(", ")
                    : item.flavor_profiles}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}