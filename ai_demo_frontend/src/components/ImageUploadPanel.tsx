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

    // ---- VALIDATION: Allowed Formats ----
    const allowedTypes = ["image/jpeg", "image/png"];

    if (!allowedTypes.includes(file.type)) {
    alert("❌ Unsupported file format. Please upload JPEG or PNG.");
    e.target.value = ""; // clear input
    return;
    }

    // Optional: check file size (e.g., 20MB)
    const maxSizeMB = 20;
    if (file.size > maxSizeMB * 1024 * 1024) {
    alert(`❌ File too large. Max allowed size is ${maxSizeMB} MB.`);
    e.target.value = "";
    return;
    }

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
    <section className="yorkie-card">
      <h2 className="text-xl font-bold text-yorkieBrown flex items-center gap-2">
        📸 Image Match
      </h2>

      <p className="text-sm text-gray-600 mb-4">
        Upload a dessert photo to find similar menu items.
      </p>

      <label className="block dashed-upload rounded-xl p-6 text-center cursor-pointer">
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
