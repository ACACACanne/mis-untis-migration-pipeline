import React, { useState } from "react";
import { DownloadCloud, Users, School, Home, RefreshCw } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function MisMasterPull({ targetMis }) {
  const [catalog, setCatalog] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const res = await pipelineApi.previewMisCatalog(targetMis);
      setCatalog(res);
    } catch {
      // Handled via logging
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Pull Active Master Roster ({targetMis})
          </h3>
          <p className="text-xs text-slate-400">
            Inspect teachers, cohorts, and rooms ready to be synced back into
            Untis DIF files.
          </p>
        </div>
        <button
          onClick={fetchCatalog}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
          />
          <span>{loading ? "Fetching..." : "Query Master API"}</span>
        </button>
      </div>

      {catalog && (
        <div className="grid grid-cols-3 gap-3 pt-2">
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center gap-3">
            <Users className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-[11px] text-slate-400">Teachers</p>
              <p className="text-sm font-semibold text-slate-200">
                {catalog.teachers_count}
              </p>
            </div>
          </div>
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center gap-3">
            <School className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-[11px] text-slate-400">Classes</p>
              <p className="text-sm font-semibold text-slate-200">
                {catalog.classes_count}
              </p>
            </div>
          </div>
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center gap-3">
            <Home className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-[11px] text-slate-400">Rooms</p>
              <p className="text-sm font-semibold text-slate-200">
                {catalog.rooms_count}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
