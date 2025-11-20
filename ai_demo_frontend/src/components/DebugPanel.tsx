import type { AIDebugTrace } from "../types";

interface Props {
  trace: AIDebugTrace | null;
}

export default function DebugPanel({ trace }: Props) {
  return (
    <section className="yorkie-card text-xs space-y-2">
      <details open>
        <summary className="cursor-pointer font-bold text-yorkieBrown">
          🐾 Debug Panel
        </summary>

        <div className="mt-3 space-y-3">

          {/* Query */}
          <div>
            <h4 className="font-semibold text-yorkieBrown">Query</h4>
            <p>{trace?.query || "(none yet)"}</p>
          </div>

          {/* Vision Description */}
          {trace?.vision_description && (
            <div>
              <h4 className="font-semibold text-yorkieBrown">Vision Description</h4>
              <div className="bg-gray-50 p-3 rounded text-gray-700 whitespace-pre-line break-words leading-relaxed">
                {trace.vision_description}
              </div>
            </div>
          )}

          {/* Parsed Filters */}
          <div>
            <h4 className="font-semibold text-yorkieBrown">Parsed Filters</h4>
            <pre className="bg-gray-100 p-2 rounded whitespace-pre overflow-x-auto">
              {JSON.stringify(trace?.filters || {}, null, 2)}
            </pre>
          </div>

          {/* Retrieved Items */}
          <div>
            <h4 className="font-semibold text-yorkieBrown">Retrieved Vector Items</h4>
            <pre className="bg-gray-100 p-2 rounded whitespace-pre overflow-x-auto">
              {JSON.stringify(trace?.retrieved_items || [], null, 2)}
            </pre>
          </div>

          {/* Raw JSON */}
          <div>
            <h4 className="font-semibold text-yorkieBrown">Raw JSON From Backend</h4>
            <pre className="bg-gray-100 p-2 rounded whitespace-pre overflow-x-auto">
              {JSON.stringify(trace?.raw || {}, null, 2)}
            </pre>
          </div>

        </div>
      </details>
    </section>
  );
}