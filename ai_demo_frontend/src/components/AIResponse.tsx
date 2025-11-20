import type { AIDebugTrace, VisionMatch } from "../types";

interface Props {
  trace: AIDebugTrace | null;
}

export default function AIResponse({ trace }: Props) {
  if (!trace) return null;

  // Backend payload is inside trace.raw
  const backend = trace.raw || trace;

  const items: VisionMatch[] =
    backend.matches && backend.matches.length > 0
      ? backend.matches
      : backend.retrieved_items || [];

  const summary = items.length
    ? `I found ${items.length} items that may match your request.`
    : `No matching menu items were found.`;

  return (
    <section className="yorkie-card space-y-3">
      <h2 className="text-lg font-bold text-yorkieBrown">💬 Yorkie Says</h2>

      <p className="text-sm text-gray-700">{summary}</p>

      <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <strong>You asked:</strong>
        <div className="mt-1 italic">{trace.query}</div>
      </div>

      {items.length > 0 && (
        <ul className="mt-3 space-y-2">
          {items.map((item, idx) => (
            <li
              key={idx}
              className="p-3 rounded-lg bg-white border border-gray-200 shadow"
            >
              <div className="font-semibold">{item.title}</div>
              <div className="text-xs text-gray-500">
                {item.origin} • {item.category} • ${item.price}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}