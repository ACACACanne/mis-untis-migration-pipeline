import React, { useState } from "react";
import { X, CheckCircle2, Ban } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function ResolutionModal({ item, onClose }) {
  const [overrideStaffId, setOverrideStaffId] = useState("");
  const [overrideRoomId, setOverrideRoomId] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResolve = async (actionStatus) => {
    setLoading(true);
    try {
      const overrides = {};
      if (overrideStaffId) overrides.override_mis_staff_id = overrideStaffId;
      if (overrideRoomId) overrides.override_mis_room_id = overrideRoomId;

      await pipelineApi.resolveQuarantineItem(item.id, actionStatus, overrides);
      onClose(true);
    } catch {
      // Handled via UI alert or state
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-semibold text-slate-100">
            Resolve Quarantine #{item.id} ({item.error_type})
          </h3>
          <button
            onClick={() => onClose(false)}
            className="text-slate-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2 text-xs">
          <p className="text-slate-300 font-medium">Failure Diagnostics:</p>
          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded text-slate-400 font-mono text-[11px]">
            {item.details}
          </div>
        </div>

        <div className="space-y-3">
          <h4 className="text-xs font-medium text-slate-300">
            Administrative Overrides:
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">
                Override Staff / Teacher ID
              </label>
              <input
                type="text"
                value={overrideStaffId}
                onChange={(e) => setOverrideStaffId(e.target.value)}
                placeholder="e.g. 104"
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:border-emerald-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">
                Override Room ID
              </label>
              <input
                type="text"
                value={overrideRoomId}
                onChange={(e) => setOverrideRoomId(e.target.value)}
                placeholder="e.g. 302"
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:border-emerald-500 outline-none"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-800 pt-3">
          <button
            onClick={() => handleResolve("IGNORED")}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          >
            <Ban className="w-3.5 h-3.5" /> Ignore
          </button>
          <button
            onClick={() => handleResolve("RESOLVED")}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            <CheckCircle2 className="w-3.5 h-3.5" /> Save Resolution
          </button>
        </div>
      </div>
    </div>
  );
}
