import React, { useState } from "react";

export default function ImageUploadPanel() {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [vision, setVision] = useState<string | null>(null);
  const [matches, setMatches] = useState<any[] | null>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPreview(URL.createObjectURL(file));
    setLoading(true);
    setVision(null);
    setMatches(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/ai/vision", {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      console.log("VISION RESPONSE:", data);

      setVision(data.vision_description || null);
      setMatches(data.matches || []);
    } catch (err) {
      console.error("Vision API error:", err);
    }

    setLoading(false);
  };

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
        <input type="file" accept="image/*" className="hidden" onChange={handleFile} />
      </label>

      {/* Preview */}
      {preview && (
        <img src={preview} className="mt-4 rounded-xl border border-yellow-200" />
      )}

      {loading && <p className="mt-3 text-sm text-gray-500">Analyzing image…</p>}

      {/* Vision Description */}
      {vision && (
        <p className="mt-4 text-yorkieBrown font-medium italic">
          🔍 Interpretation: {vision}
        </p>
      )}

      {/* Matches */}
      {matches && matches.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-bold text-yorkieBrown">
            🧁 Recommended Items
          </h3>

          <div className="grid grid-cols-1 gap-4">
            {matches.map((item, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-yellow-200 bg-white shadow p-4"
              >
                <h4 className="text-lg font-semibold text-yorkieBrown">
                  {item.title}
                </h4>
                <p className="text-sm text-gray-500">${item.price?.toFixed(2)}</p>

                <p className="text-xs text-gray-600 mt-1">
                  {item.origin} · {item.category}
                </p>

                <p className="text-xs mt-1">
                  <b>Tags:</b> {item.tags?.join(", ")}
                </p>
                <p className="text-xs">
                  <b>Flavors:</b> {item.flavor_profiles?.join(", ")}
                </p>
                <p className="text-xs">
                  <b>Dietary:</b> {item.dietary_features?.join(", ")}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}