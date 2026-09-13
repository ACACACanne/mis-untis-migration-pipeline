import React, { useState, useEffect } from "react";
import { Search, KeyRound } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function KeyRegistryDesk() {
  const [query, setQuery] = useState("");
  const [entityType, setEntityType] = useState("");
  const [records, setRecords] = useState([]);

  const search = async () => {
    try {
      const res = await pipelineApi.searchRegistry(query, entityType);
      setRecords(res);
    } catch {
      // Handled via state
    }
  };

  useEffect(() => {
    search();
  }, [entityType]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-emerald-400" />
          <h2 className="text-sm font-semibold text-slate-200">
            Cross-System Key Registry
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 outline-none"
          >
            <option value="">All Entities</option>
            <option value="teacher">Teachers</option>
            <option value="room">Rooms</option>
            <option value="class">Classes</option>
            <option value="student">Students</option>
          </select>

          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="Search code or identifier..."
              className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 outline-none w-56 focus:border-emerald-500"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          </div>
        </div>
      </div>

      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-900 text-slate-400 text-[10px] uppercase font-sans border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Entity</th>
              <th className="py-3 px-4">Untis ID</th>
              <th className="py-3 px-4">Arbor UUID</th>
              <th className="py-3 px-4">Bromcom ID</th>
              <th className="py-3 px-4 font-sans">Display Label</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {!records.length ? (
              <tr>
                <td
                  colSpan="5"
                  className="py-6 text-center text-slate-500 font-sans"
                >
                  No registry cross-references found.
                </td>
              </tr>
            ) : (
              records.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/20">
                  <td className="py-2.5 px-4 font-sans text-slate-400">
                    {r.entity_type}
                  </td>
                  <td className="py-2.5 px-4 text-emerald-400">{r.untis_id}</td>
                  <td className="py-2.5 px-4 text-slate-400">
                    {r.arbor_id || "—"}
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">
                    {r.bromcom_id || "—"}
                  </td>
                  <td className="py-2.5 px-4 font-sans">
                    {r.display_name || r.short_code || "—"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
