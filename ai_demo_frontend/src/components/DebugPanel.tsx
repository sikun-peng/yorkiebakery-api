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

        <div className="mt-3 space-y-2">
          <div>
            <h4 className="font-semibold text-yorkieBrown">Query</h4>
            <p>{trace?.query || "(none yet)"}</p>
          </div>

          <div>
            <h4 className="font-semibold text-yorkieBrown">Parsed Filters</h4>
            <pre className="bg-gray-100 p-2 rounded">
              {JSON.stringify(trace?.filters || {}, null, 2)}
            </pre>
          </div>

          <div>
            <h4 className="font-semibold text-yorkieBrown">Retrieved Vector Items</h4>
            <pre className="bg-gray-100 p-2 rounded">
              {JSON.stringify(trace?.retrieved_items || [], null, 2)}
            </pre>
          </div>

          <div>
            <h4 className="font-semibold text-yorkieBrown">Raw JSON From Backend</h4>
            <pre className="bg-gray-100 p-2 rounded">
              {JSON.stringify(trace?.raw || {}, null, 2)}
            </pre>
          </div>
        </div>
      </details>
    </section>
  );
}