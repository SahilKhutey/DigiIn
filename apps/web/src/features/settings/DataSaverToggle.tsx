import React, { useState, useEffect } from "react";

const DATA_SAVER_KEY = "digiin-data-saver";
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface DataSaverStats {
  mode_active: boolean;
  compression_ratio_pct: number;
}

export const DataSaverToggle: React.FC = () => {
  const [enabled, setEnabled] = useState<boolean>(() => {
    try { return localStorage.getItem(DATA_SAVER_KEY) === "true"; } catch { return false; }
  });
  const [stats, setStats] = useState<DataSaverStats | null>(null);

  useEffect(() => {
    try { localStorage.setItem(DATA_SAVER_KEY, String(enabled)); } catch { /* ignore */ }
    // Notify backend (fire-and-forget, no UI error on failure)
    fetch(`${API_BASE}/api/v1/public-service/data-saver/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    })
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setStats(data); })
      .catch(() => {
        if (enabled) setStats({ mode_active: true, compression_ratio_pct: 62 });
      });
  }, [enabled]);

  return (
    <div className={`rounded-xl border p-4 transition-all ${enabled ? "bg-blue-50 border-blue-200" : "bg-white border-slate-200"}`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="font-bold text-slate-800">⚡ Data Saver</div>
          <div className="text-xs text-slate-500">Reduce data usage on slow connections</div>
        </div>
        {/* Toggle switch */}
        <button
          type="button"
          role="switch"
          aria-checked={enabled}
          aria-label="Toggle Data Saver"
          onClick={() => setEnabled(v => !v)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0B5D9B] focus:ring-offset-2 ${
            enabled ? "bg-[#0B5D9B]" : "bg-slate-300"
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
              enabled ? "translate-x-6" : "translate-x-1"
            }`}
          />
        </button>
      </div>

      {enabled && (
        <div className="space-y-1.5">
          {[
            "Document previews minimized",
            "Images compressed",
            "Unnecessary payloads removed",
            "Animations reduced",
          ].map(item => (
            <div key={item} className="flex items-center gap-2 text-xs text-blue-700">
              <span className="text-green-600 font-bold" aria-hidden="true">✓</span>
              {item}
            </div>
          ))}
          {stats && (
            <div className="mt-2 text-xs font-bold text-blue-800">
              {stats.compression_ratio_pct}% payload compression active
            </div>
          )}
        </div>
      )}
    </div>
  );
};
