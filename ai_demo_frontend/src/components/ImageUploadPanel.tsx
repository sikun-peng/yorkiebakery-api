import { useState } from "react";
import { analyzeImage } from "../api/ai";

interface Props {
  onAnalysisComplete: (data: any) => void;
}

export default function ImageUploadPanel({ onAnalysisComplete }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // show preview
    setPreview(URL.createObjectURL(file));
    setLoading(true);

    try {
      const result = await analyzeImage(file);  // ✔ pass file, not FormData
      onAnalysisComplete(result);
    } catch (err) {
      console.error("Image analysis failed", err);
      alert("Image analysis failed");
    }

    setLoading(false);
  }

  return (
    <section className="yorkie-card mt-6">
      <h2 className="text-xl font-bold text-yorkieBrown flex items-center gap-2">
        📸 Image Match
      </h2>

      <p className="text-sm text-gray-600 mb-4">
        Upload a dessert photo to find similar menu items.
      </p>

      <label className="block border-2 border-dashed border-gray-400 rounded-xl p-6 text-center cursor-pointer hover:bg-gray-50 transition">
        👉 Click to upload image (JPG / PNG)
        <input type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
      </label>

      {preview && (
        <img
          src={preview}
          alt="Preview"
          className="mt-4 rounded-lg shadow-md border"
        />
      )}

      {loading && <p className="text-sm text-blue-500 mt-2">Analyzing...</p>}
    </section>
  );
}