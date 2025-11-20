// App.tsx
import { useState } from "react";
import YorkieHeader from "./components/YorkieHeader";
import AIInput from "./components/AIInput";
import AIResponse from "./components/AIResponse";
import RetrievedItemsPanel from "./components/RetrievedItemsPanel";
import ImageUploadPanel from "./components/ImageUploadPanel";
import DebugPanel from "./components/DebugPanel";
import type { AIDebugTrace } from "./types";

export default function App() {
  const [trace, setTrace] = useState<AIDebugTrace | null>(null);

  // Function to handle image analysis results
  const handleImageAnalysis = (data: any) => {
    // Convert image analysis data to the same format as text queries
    setTrace({
      query: "Image analysis",
      filters: {},
      retrieved_items: data.similar_items || [],
      raw: data
    });
  };

  return (
    <div className="min-h-screen bg-[var(--yorkie-bg)] py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* LEFT COLUMN - Main content + Debug */}
          <div className="lg:col-span-2 space-y-8">
            <YorkieHeader />
            <AIInput setTrace={setTrace} />
            <DebugPanel trace={trace} />
            <AIResponse trace={trace} />
            <RetrievedItemsPanel trace={trace} />
          </div>

          {/* RIGHT COLUMN - Image upload only */}
          <div className="space-y-8">
            <ImageUploadPanel onAnalysisComplete={handleImageAnalysis} />
          </div>

        </div>
      </div>
    </div>
  );
}