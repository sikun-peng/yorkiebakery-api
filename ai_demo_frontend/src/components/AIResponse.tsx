import type { AIDebugTrace } from "../types";

interface Props {
  trace: AIDebugTrace | null;
}

export default function AIResponse({ trace }: Props) {
  if (!trace) return null;

  // Construct a pretty top-line summary for the user
  const summary = trace.retrieved_items?.length
    ? `I found ${trace.retrieved_items.length} items that may match your request.`
    : `No matching menu items were found.`;

  return (
    <section className="yorkie-card space-y-3">
      <h2 className="text-lg font-bold text-yorkieBrown">💬 Yorkie Says</h2>

      <p className="text-sm text-gray-700">{summary}</p>

      {/* Show what user asked */}
      <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <strong>You asked:</strong>
        <div className="mt-1 italic">{trace.query}</div>
      </div>
    </section>
  );
}