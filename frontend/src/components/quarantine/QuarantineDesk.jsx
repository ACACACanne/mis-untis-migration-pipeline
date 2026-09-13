import React, { useState, useEffect } from "react";
import { ShieldAlert, AlertTriangle, CheckCircle2, Wrench } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";
import ResolutionModal from "./ResolutionModal";

export default function QuarantineDesk({ onResolved }) {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({
    total_quarantined: 0,
    pending_count: 0,
  });
  const [filter, setFilter] = useState("PENDING");
  const [selectedItem, setSelectedItem] = useState(null);

  const loadData = async () => {
    try {
      const [listRes, sumRes] = await Promise.all([
        pipelineApi.getQuarantineItems(filter),
        pipelineApi.getQuarantineSummary(),
      ]);
      setItems(listRes);
      setSummary(sumRes);
    } catch {
      // Backend handles logging
    }
  };

  useEffect(() => {
    loadData();
  }, [filter]);

  const handleModalClose = (refreshNeeded) => {
    setSelectedItem(null);
    if (refreshNeeded) {
      loadData();
      if (onResolved) onResolved();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <h2 className="text-sm font-semibold text-slate-200">
            Quarantine & Collision Desk
          </h2>
          <span className="text-xs text-slate-400">
            ({summary.pending_count} pending resolution)
          </span>
        </div>

        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-xs">
          {["PENDING", "RESOLVED", "IGNORED"].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 rounded-md transition-colors ${
                filter === status
                  ? "bg-slate-800 text-white font-medium"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {!items.length ? (
        <div className="p-8 text-center border border-slate-800 rounded-xl bg-slate-900/20 text-xs text-slate-400">
          No quarantine records currently under {filter} status.
        </div>
      ) : (
        <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 text-[10px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Error Type</th>
                <th className="py-3 px-4">Details</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans text-slate-300">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/20">
                  <td className="py-2.5 px-4 font-mono font-medium text-slate-200">
                    {item.entity_type} ({item.lesson_id || "—"})
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                      <AlertTriangle className="w-3 h-3" /> {item.error_type}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 max-w-md truncate">
                    {item.details}
                  </td>
                  <td className="py-2.5 px-4">
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                        item.status === "RESOLVED"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <button
                      onClick={() => setSelectedItem(item)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                    >
                      <Wrench className="w-3 h-3" /> Resolve
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedItem && (
        <ResolutionModal item={selectedItem} onClose={handleModalClose} />
      )}
    </div>
  );
}
