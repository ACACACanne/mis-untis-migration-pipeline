// frontend/src/components/mis_to_untis/MisExtractionDesk.jsx

import React, { useState, useRef } from "react";
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
  UploadCloud,
  FileCode,
  Check,
} from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function MisExtractionDesk({
  targetMis = "ARBOR",
  setTargetMis,
  onExtractionCompleted,
}) {
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [scheduleData, setScheduleData] = useState(null);
  const [downloadReady, setDownloadReady] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const fileInputRef = useRef(null);

  const activeMis = (targetMis || "ARBOR").toUpperCase();

  const handleSelectMis = (misKey) => {
    if (setTargetMis) {
      setTargetMis(misKey);
    }
    setScheduleData(null);
    setDownloadReady(false);
    setUploadedFileName(null);
  };

  const handleQueryMis = async () => {
    setLoading(true);
    try {
      const preview = await pipelineApi.previewMisSchedule(activeMis);
      setScheduleData(preview);
      setDownloadReady(true);
      setUploadedFileName(null);
      if (onExtractionCompleted) onExtractionCompleted();
    } catch (err) {
      console.error(`Failed to query live ${activeMis} schedule:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await pipelineApi.uploadSyntheticMisFile(file, activeMis);
      setScheduleData(res);
      setUploadedFileName(file.name);
      setDownloadReady(true);
      if (onExtractionCompleted) onExtractionCompleted();
    } catch (err) {
      console.error(`Failed to upload synthetic ${activeMis} file:`, err);
    } finally {
      setLoading(false);
    }
  };

  // Safe In-Memory Blob Download Handler (Uses relative path for Vercel/Render proxy)
  const handleDownloadPackage = async (e) => {
    if (e) e.preventDefault();
    if (!downloadReady || downloading) return;

    setDownloading(true);
    try {
      const response = await fetch(
        `/api/v1/reverse-sync/export-dif?target_mis=${activeMis}`,
        { method: "GET" },
      );

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `Untis_Complete_${activeMis}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("Download failed:", err);
      alert(`Could not download DIF package: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const fixtureExampleName =
    activeMis === "ARBOR"
      ? "mock_arbor_response.json"
      : "mock_bromcom_response.json";

  return (
    <div className="space-y-6">
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl space-y-5">
        {/* Source MIS Selector & Action Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider">
                Source MIS Schedule Extraction ({activeMis})
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Select your source MIS to query live schedules or drop synthetic
              JSON fixtures to export Untis DIF files.
            </p>
          </div>

          {/* MIS Switcher Tabs */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1">
            <button
              type="button"
              onClick={() => handleSelectMis("ARBOR")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeMis === "ARBOR"
                  ? "bg-emerald-500 text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {activeMis === "ARBOR" && <Check className="w-3.5 h-3.5" />}
              <span>Arbor MIS</span>
            </button>
            <button
              type="button"
              onClick={() => handleSelectMis("BROMCOM")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeMis === "BROMCOM"
                  ? "bg-emerald-500 text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {activeMis === "BROMCOM" && <Check className="w-3.5 h-3.5" />}
              <span>Bromcom Cloud</span>
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs text-slate-400">
            Current Target:{" "}
            <strong className="text-emerald-400">{activeMis}</strong> (API v1)
          </span>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleQueryMis}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`}
              />
              <span>Query Live {activeMis} API</span>
            </button>

            {/* Changed from <a> to <button> with safe Blob download */}
            <button
              type="button"
              onClick={handleDownloadPackage}
              disabled={!downloadReady || downloading}
              className={`flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl transition ${
                downloadReady && !downloading
                  ? "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/30 cursor-pointer"
                  : "bg-slate-800/60 text-slate-500 pointer-events-none border border-slate-800 cursor-not-allowed"
              }`}
            >
              {downloading ? (
                <RefreshCw className="w-4 h-4 animate-spin text-emerald-300" />
              ) : (
                <DownloadCloud className="w-4 h-4" />
              )}
              <span>
                {downloading
                  ? "Generating Archive..."
                  : "Download Untis DIF Package"}
              </span>
            </button>
          </div>
        </div>

        {/* Drag & Drop File Zone */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
            isDragging
              ? "border-emerald-500 bg-emerald-500/10"
              : "border-slate-800 hover:border-slate-700 bg-slate-950/40"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => handleFileUpload(e.target.files?.[0])}
            accept=".json,.csv"
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="h-10 w-10 bg-slate-900 border border-slate-800 rounded-full flex items-center justify-center text-slate-400">
              {uploadedFileName ? (
                <FileCode className="h-5 w-5 text-emerald-400" />
              ) : (
                <UploadCloud className="h-5 w-5 text-emerald-400" />
              )}
            </div>
            <div className="text-xs">
              <span className="font-semibold text-slate-200">
                {uploadedFileName
                  ? `Loaded: ${uploadedFileName}`
                  : `Drag & drop your synthetic ${activeMis} JSON fixture`}
              </span>
              <p className="text-[11px] text-slate-500 mt-0.5">
                or click to browse local filesystem (e.g. {fixtureExampleName})
              </p>
            </div>
          </div>
        </div>

        {/* Schedule preview telemetry cards */}
        {scheduleData && (
          <div className="pt-2 border-t border-slate-800/80">
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
                Schedule parsed successfully (
                {uploadedFileName
                  ? `Source: ${uploadedFileName}`
                  : `Live ${activeMis} API`}
                ). Ready to download <strong>GPU001.txt</strong> through{" "}
                <strong>GPU008.txt</strong>.
              </span>
              <button
                type="button"
                onClick={handleDownloadPackage}
                disabled={downloading}
                className="underline font-semibold hover:text-emerald-200 bg-transparent border-0 p-0 cursor-pointer text-xs"
              >
                {downloading ? "Downloading..." : "Download Package"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Dynamic Untis Ingestion & Verification Card */}
      <div className="p-5 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
        {/* Card Header with Dynamic Target MIS Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-800/60">
          <div>
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
              How to Ingest or Verify Output
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Instructions automatically adapt for {activeMis} DIF exports and
              verification
            </p>
          </div>

          {/* Interactive Target MIS Switcher */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 p-1 rounded-xl">
            <span className="text-[10px] text-slate-400 uppercase font-mono px-1.5">
              Target:
            </span>
            <button
              type="button"
              onClick={() => setTargetMis && setTargetMis("ARBOR")}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-all ${
                activeMis === "ARBOR"
                  ? "bg-emerald-500 text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              ARBOR
            </button>
            <button
              type="button"
              onClick={() => setTargetMis && setTargetMis("BROMCOM")}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-all ${
                activeMis === "BROMCOM"
                  ? "bg-emerald-500 text-slate-950 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              BROMCOM
            </button>
          </div>
        </div>

        {/* Instruction Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400">
          {/* Option A: Full Untis Desktop Import */}
          <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
            <span className="font-semibold text-emerald-400 flex items-center gap-1.5">
              Option A: Ingest into Untis Desktop
            </span>
            <ol className="list-decimal list-inside space-y-1.5 leading-relaxed">
              <li>
                Download and extract{" "}
                <code className="text-emerald-300 font-mono bg-emerald-950/40 px-1 py-0.5 rounded border border-emerald-800/50">
                  Untis_Complete_{activeMis}.zip
                </code>
                .
              </li>
              <li>
                Open Untis and go to{" "}
                <strong>File → Import/Export → DIF Import</strong> (or{" "}
                <em>Data Exchange → DIF Format</em>).
              </li>
              <li>
                Select the folder containing{" "}
                <code className="text-slate-300 font-mono">GPU001.txt</code>{" "}
                through{" "}
                <code className="text-slate-300 font-mono">GPU008.txt</code>.
              </li>
              <li>
                Execute import to populate your timetable master with active{" "}
                <strong className="text-emerald-400">{activeMis}</strong>{" "}
                records.
              </li>
            </ol>
          </div>

          {/* Option B: Offline / Spreadsheet Inspection */}
          <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
            <span className="font-semibold text-amber-400 flex items-center gap-1.5">
              Option B: Quick Text/Spreadsheet Inspection (No Untis Needed)
            </span>
            <p className="leading-relaxed">
              If Untis Desktop is not installed on this workstation:
            </p>
            <ul className="list-disc list-inside space-y-1 leading-relaxed text-slate-400">
              <li>
                Unzip the package and inspect the comma-separated text files in
                Notepad or Excel.
              </li>
              <li>
                <strong className="text-slate-200 font-mono">GPU001.txt</strong>
                : Bell schedule & period grid times.
              </li>
              <li>
                <strong className="text-slate-200 font-mono">
                  GPU002 / GPU003
                </strong>
                : {activeMis} staff codes & form cohorts.
              </li>
              <li>
                <strong className="text-slate-200 font-mono">
                  GPU007 / GPU008
                </strong>
                : Course definitions & room placements.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
