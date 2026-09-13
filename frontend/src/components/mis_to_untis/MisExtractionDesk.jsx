// frontend/src/components/mis_to_untis/MisExtractionDesk.jsx

import React, { useState } from "react";
import {
  DownloadCloud,
  CheckCircle2,
  RefreshCw,
  Server,
  Layers,
  Users,
  Calendar,
  Building,
  BookOpen,
} from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function MisExtractionDesk({
  targetMis,
  onExtractionCompleted,
}) {
  const [loading, setLoading] = useState(false);
  const [scheduleData, setScheduleData] = useState(null);
  const [downloadReady, setDownloadReady] = useState(false);

  const handleQueryMis = async () => {
    setLoading(true);
    try {
      const preview = await pipelineApi.previewMisSchedule(targetMis);
      setScheduleData(preview);
      setDownloadReady(true);
      if (onExtractionCompleted) onExtractionCompleted();
    } catch (err) {
      console.error("Failed to query MIS schedule:", err);
    } finally {
      setLoading(false);
    }
  };

  const downloadUrl = pipelineApi.getDifDownloadUrl(targetMis);

  return (
    <div className="space-y-6">
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" />
              Source MIS Schedule Extraction ({targetMis})
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Pull active teaching groups, staff allocations, and room bookings
              from {targetMis} into Untis DIF format (GPU001–GPU008).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleQueryMis}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`}
              />
              <span>Query Live {targetMis} Roster</span>
            </button>

            <a
              href={downloadUrl}
              download
              className={`flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl transition ${
                downloadReady
                  ? "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/30"
                  : "bg-slate-800/60 text-slate-500 pointer-events-none border border-slate-800"
              }`}
            >
              <DownloadCloud className="w-4 h-4" />
              <span>Download Untis DIF Package</span>
            </a>
          </div>
        </div>

        {scheduleData && (
          <div className="pt-4 border-t border-slate-800/80">
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <Calendar className="w-3.5 h-3.5 text-emerald-400" /> Periods
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {scheduleData.periods_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <Users className="w-3.5 h-3.5 text-emerald-400" /> Teachers
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {scheduleData.teachers_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <Users className="w-3.5 h-3.5 text-emerald-400" /> Classes
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {scheduleData.classes_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <Building className="w-3.5 h-3.5 text-emerald-400" /> Rooms
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {scheduleData.rooms_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <BookOpen className="w-3.5 h-3.5 text-emerald-400" /> Subjects
                </div>
                <div className="text-lg font-bold text-slate-100 mt-1">
                  {scheduleData.subjects_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <Layers className="w-3.5 h-3.5 text-amber-400" /> Lessons
                </div>
                <div className="text-lg font-bold text-amber-300 mt-1">
                  {scheduleData.lessons_count}
                </div>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Grid
                  Slots
                </div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {scheduleData.slots_count}
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-between text-xs text-emerald-300">
              <span>
                Schedule extraction succeeded. The DIF archive contains{" "}
                <strong>GPU001.txt</strong> through <strong>GPU008.txt</strong>,
                ready for import into desktop Untis.
              </span>
              <a
                href={downloadUrl}
                download
                className="underline font-semibold hover:text-emerald-200"
              >
                Download Now
              </a>
            </div>
          </div>
        )}
      </div>

      <div className="p-5 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-3">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
          How to Ingest into Untis Desktop
        </h3>
        <ol className="list-decimal list-inside text-xs text-slate-400 space-y-1.5">
          <li>
            Download and extract the{" "}
            <code className="text-emerald-400 font-mono">
              Untis_Complete_{targetMis}.zip
            </code>{" "}
            archive.
          </li>
          <li>
            Open Untis and select{" "}
            <strong>File → Import/Export → DIF Import</strong> (or{" "}
            <em>Data Exchange → DIF Format</em>).
          </li>
          <li>
            Choose the folder containing the extracted{" "}
            <code className="text-slate-300 font-mono">GPU001.txt</code> to{" "}
            <code className="text-slate-300 font-mono">GPU008.txt</code> files.
          </li>
          <li>
            Execute the import to populate your Untis timetable master with
            active MIS structures.
          </li>
        </ol>
      </div>
    </div>
  );
}
