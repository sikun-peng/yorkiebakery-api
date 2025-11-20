import React from "react";
import type { AIDebugTrace } from "../types";

interface Props {
  trace: AIDebugTrace | null;
}

export default function RetrievedItemsPanel({ trace }: Props) {
  if (!trace || !trace.raw || !trace.raw.items) return null;

  const items = trace.raw.items;

  if (items.length === 0) return null;

  return (
    <section className="yorkie-card space-y-4">
      <h2 className="text-lg font-bold text-yorkieBrown">🧁 Suggested Menu Matches</h2>
      <p className="text-sm text-gray-500">(Top {items.length} items retrieved)</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {items.map((item: any, idx: number) => {
          const flavors = (item.flavor_profiles || "").split(",");
          const tags = (item.tags || "").split(",");
          const dietary = (item.dietary_features || "").split(",");

          return (
            <div
              key={idx}
              className="rounded-xl border border-yellow-200 bg-white p-4 shadow hover:shadow-lg transition"
            >
              <h3 className="text-lg font-semibold text-yorkieBrown">{item.title}</h3>

              <p className="text-sm text-gray-600">${item.price}</p>

              <p className="text-xs text-gray-500 mt-1">
                {item.origin} · {item.category}
              </p>

              <div className="mt-2">
                <p className="text-xs text-gray-400">Flavors:</p>
                <p className="text-sm">{flavors.join(", ")}</p>
              </div>

              <div className="mt-2">
                <p className="text-xs text-gray-400">Dietary:</p>
                <p className="text-sm">{dietary.join(", ")}</p>
              </div>

              <div className="mt-2">
                <p className="text-xs text-gray-400">Tags:</p>
                <p className="text-sm">{tags.join(", ")}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}