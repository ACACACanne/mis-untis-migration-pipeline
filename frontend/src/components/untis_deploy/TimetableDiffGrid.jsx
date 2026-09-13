// frontend/src/components/untis_deploy/TimetableDiffGrid.jsx

import React from "react";
import { PlusCircle, RefreshCw, Trash2, Check } from "lucide-react";

export default function TimetableDiffGrid({ diffs = [] }) {
  if (!diffs.length) {
    return (
      <div className="p-8 text-center border border-slate-800 rounded-xl bg-slate-900/20">
        <p className="text-xs text-slate-400">
          No staged timetable diffs found for this MIS.
        </p>
      </div>
    );
  }

  const getBadge = (type) => {
    switch (type) {
      case "CREATE":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <PlusCircle className="w-3 h-3" /> CREATE
          </span>
        );
      case "UPDATE":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <RefreshCw className="w-3 h-3" /> UPDATE
          </span>
        );
      case "DELETE":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <Trash2 className="w-3 h-3" /> DELETE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <Check className="w-3 h-3" /> UNCHANGED
          </span>
        );
    }
  };

  return (
    <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Lesson ID</th>
              <th className="py-3 px-4">Schedule Slot</th>
              <th className="py-3 px-4">Class / Cohort</th>
              <th className="py-3 px-4">Teacher</th>
              <th className="py-3 px-4">Room</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
            {diffs.map((diff) => {
              const payload = diff.slot_payload || {};
              return (
                <tr
                  key={diff.id}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="py-2.5 px-4 font-sans">
                    {getBadge(diff.change_type)}
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">
                    {diff.untis_lesson_id || "—"}
                  </td>
                  <td className="py-2.5 px-4 font-sans">
                    Day {diff.day_number}, P{diff.period_number}
                  </td>
                  <td className="py-2.5 px-4">
                    {payload.class_code || payload.mis_group_code || "—"}
                  </td>
                  <td className="py-2.5 px-4">
                    {payload.teacher_id || payload.mis_staff_id || "—"}
                  </td>
                  <td className="py-2.5 px-4">
                    {payload.room_code || payload.mis_room_id || "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
