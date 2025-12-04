// App.tsx
import { useState } from "react";
import YorkieHeader from "./components/YorkieHeader";
import AIInput from "./components/AIInput";
import AIResponse from "./components/AIResponse";
import RetrievedItemsPanel from "./components/RetrievedItemsPanel";
import ImageUploadPanel from "./components/ImageUploadPanel";
import DebugPanel from "./components/DebugPanel";
import GraphQLPanel from "./components/GraphQLPanel";
import type { AIDebugTrace } from "./types";

export default function App() {
  const [trace, setTrace] = useState<AIDebugTrace | null>(null);

  const handleImageAnalysis = (data: any) => {
    setTrace({
      query: "Image analysis",
      filters: {},
      retrieved_items: data.similar_items || [],
      raw: data,
      matches: data.matches || [],     // ensure matches stays wired
      vision_description: data.vision_description || ""
    });
  };

  return (
    <div className="min-h-screen bg-[var(--yorkie-bg)] py-8">
      <div className="max-w-6xl mx-auto px-4">
        <YorkieHeader />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">

          {/* LEFT COLUMN (2/3) */}
          <div className="lg:col-span-2 space-y-8">
            <AIInput setTrace={setTrace} />
            <AIResponse trace={trace} />
            <RetrievedItemsPanel trace={trace} />
          </div>

          {/* RIGHT COLUMN (1/3) */}
          <div className="space-y-8 lg:self-start">
            <ImageUploadPanel onAnalysisComplete={handleImageAnalysis} />
            {/* Debug Panel moved here */}
            <DebugPanel trace={trace} />
            <GraphQLPanel />
          </div>

        </div>
      </div>
    </div>
  );
}
