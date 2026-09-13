import React, { useState } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function XmlUploadZone({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFile = async (file) => {
    if (!file || !file.name.endsWith(".xml")) {
      setError("Please provide a valid Untis XML 3.8 document (.xml)");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const summary = await pipelineApi.uploadUntisXml(file);
      setResult(summary);
      if (onUploadSuccess) onUploadSuccess(summary);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to ingest Untis XML timetable",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
          dragActive
            ? "border-emerald-400 bg-emerald-950/10"
            : "border-slate-800 hover:border-slate-700 bg-slate-900/30"
        }`}
        onClick={() => document.getElementById("untis-file-input").click()}
      >
        <input
          type="file"
          id="untis-file-input"
          accept=".xml"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="p-3 bg-slate-800/80 rounded-full text-slate-300">
            {loading ? (
              <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
            ) : (
              <UploadCloud className="w-6 h-6" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-200">
              Drag & drop your Untis XML 3.8 timetable file
            </p>
            <p className="text-xs text-slate-400 mt-1">
              or click to browse local filesystem
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-950/40 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-slate-200">
                {result.filename}
              </span>
              <span className="text-[11px] text-slate-400">
                ({result.school_name})
              </span>
            </div>
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" /> Parsed & Staged
            </span>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 text-center text-xs">
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <p className="text-slate-400 text-[10px]">Time Periods</p>
              <p className="font-semibold text-slate-200">
                {result.summary.periods_detected}
              </p>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <p className="text-slate-400 text-[10px]">Teachers</p>
              <p className="font-semibold text-slate-200">
                {result.summary.teachers_detected}
              </p>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <p className="text-slate-400 text-[10px]">Classes</p>
              <p className="font-semibold text-slate-200">
                {result.summary.classes_detected}
              </p>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
              <p className="text-slate-400 text-[10px]">Lessons</p>
              <p className="font-semibold text-slate-200">
                {result.summary.lessons_parsed}
              </p>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-emerald-500/20">
              <p className="text-emerald-400 text-[10px]">Clean Slots</p>
              <p className="font-semibold text-emerald-300">
                {result.summary.clean_slots_ready}
              </p>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-rose-500/20">
              <p className="text-rose-400 text-[10px]">Quarantined</p>
              <p className="font-semibold text-rose-300">
                {result.summary.quarantined_count}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
