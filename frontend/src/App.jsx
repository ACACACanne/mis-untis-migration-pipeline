// frontend/src/App.jsx

import React, { useState, useEffect, useCallback } from "react";
import {
  Server,
  ShieldAlert,
  Clock,
  DownloadCloud,
  Layers,
  FileCheck2,
  RefreshCw,
} from "lucide-react";

import Header from "./components/layout/Header";
import ModeSwitch from "./components/layout/ModeSwitch";
import MetricCard from "./components/layout/MetricCard";
import MisExtractionDesk from "./components/mis_to_untis/MisExtractionDesk";
import QuarantineDesk from "./components/quarantine/QuarantineDesk";
import XmlUploadZone from "./components/untis_deploy/XmlUploadZone";
import PreFlightRunner from "./components/untis_deploy/PreFlightRunner";
import OptionGroupViewer from "./components/untis_deploy/OptionGroupViewer";
import TimetableDiffGrid from "./components/untis_deploy/TimetableDiffGrid";
import KeyRegistryDesk from "./components/registry/KeyRegistryDesk";
import { pipelineApi } from "./api/pipelineApi";

export default function App() {
  // Primary pipeline default: MIS to Untis extraction
  const [activeTab, setActiveTab] = useState("mis_to_untis");
  const [targetMis, setTargetMis] = useState("ARBOR");
  const [misStats, setMisStats] = useState(null);
  const [stagedDiffs, setStagedDiffs] = useState([]);
  const [optionBlocks, setOptionBlocks] = useState([]);
  const [quarantineSummary, setQuarantineSummary] = useState({
    total_quarantined: 0,
    pending_count: 0,
    resolved_count: 0,
    ignored_count: 0,
  });
  const [loading, setLoading] = useState(false);

  // Unified telemetry refresh handler across all pipeline stores
  const loadPipelineData = useCallback(async () => {
    setLoading(true);
    try {
      const [stats, qSummary, diffs] = await Promise.all([
        pipelineApi.previewMisSchedule(targetMis).catch(() => null),
        pipelineApi
          .getQuarantineSummary()
          .catch(() => ({
            total_quarantined: 0,
            pending_count: 0,
            resolved_count: 0,
            ignored_count: 0,
          })),
        pipelineApi.getStagedDiffs(targetMis).catch(() => []),
      ]);

      setMisStats(stats);
      setQuarantineSummary(qSummary);
      setStagedDiffs(diffs);

      // Consolidate elective options for secondary Untis deploy tab
      const groupsMap = new Map();
      diffs
        .filter(
          (d) =>
            d.slot_payload?.studentgroup_id ||
            d.slot_payload?.assigned_students?.length,
        )
        .forEach((d) => {
          const groupId =
            d.slot_payload?.studentgroup_id || d.slot_payload?.class_code;
          if (!groupId) return;

          const assigned = d.slot_payload?.assigned_students || [];
          if (!groupsMap.has(groupId)) {
            groupsMap.set(groupId, {
              group_identifier: groupId,
              subject_code: d.slot_payload?.subject_code,
              academic_cohort: d.slot_payload?.class_code,
              student_count: assigned.length,
              students: assigned.map((id) => ({
                untis_student_id: id,
                student_name: id.replace("ST_", ""),
                base_class: d.slot_payload?.class_code,
              })),
            });
          } else {
            const existing = groupsMap.get(groupId);
            if (assigned.length > existing.student_count) {
              existing.student_count = assigned.length;
              existing.students = assigned.map((id) => ({
                untis_student_id: id,
                student_name: id.replace("ST_", ""),
                base_class: d.slot_payload?.class_code,
              }));
            }
          }
        });

      setOptionBlocks(Array.from(groupsMap.values()));
    } finally {
      setLoading(false);
    }
  }, [targetMis]);

  useEffect(() => {
    loadPipelineData();
  }, [loadPipelineData]);

  const createsCount = stagedDiffs.filter(
    (d) => d.change_type === "CREATE",
  ).length;
  const updatesCount = stagedDiffs.filter(
    (d) => d.change_type === "UPDATE",
  ).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased">
      {/* Header bar hosting the global metrics refresh button adjacent to target switches */}
      <Header
        targetMis={targetMis}
        setTargetMis={setTargetMis}
        onRefresh={loadPipelineData}
        loading={loading}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <ModeSwitch
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            quarantineCount={quarantineSummary.pending_count}
          />

          {/* Quick Refresh All Action Button */}
          <button
            onClick={loadPipelineData}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold text-slate-200 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 hover:border-slate-700 transition-all disabled:opacity-50 shrink-0"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`}
            />
            <span>Refresh All Metrics</span>
          </button>
        </div>

        {/* Global Pipeline Telemetry Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetricCard
            title="MIS Active Slots"
            value={misStats ? misStats.slots_count : 0}
            icon={Server}
            subtitle={`${misStats ? misStats.lessons_count : 0} scheduled courses`}
            variant="success"
            loading={loading}
          />
          <MetricCard
            title="Quarantine Queue"
            value={quarantineSummary.pending_count}
            icon={ShieldAlert}
            subtitle={`${quarantineSummary.resolved_count} resolved overrides`}
            variant={quarantineSummary.pending_count > 0 ? "danger" : "default"}
            loading={loading}
            onClick={() => setActiveTab("quarantine")}
          />
          <MetricCard
            title="Active Target MIS"
            value={targetMis}
            icon={Clock}
            subtitle="Live API Connected"
            badge="Primary Source"
          />
          <MetricCard
            title="Untis DIF Output"
            value="GPU001–008"
            icon={DownloadCloud}
            subtitle="Master & Slots Ready"
            variant="warning"
          />
        </div>

        {/* PRIMARY PIPELINE TAB: MIS to Untis Extraction */}
        {activeTab === "mis_to_untis" && (
          <MisExtractionDesk
            targetMis={targetMis}
            onExtractionCompleted={loadPipelineData}
          />
        )}

        {/* QUARANTINE DESK TAB */}
        {activeTab === "quarantine" && (
          <QuarantineDesk onResolved={loadPipelineData} />
        )}

        {/* SECONDARY / OPTIONAL PIPELINE TAB: Untis to MIS Deployment */}
        {activeTab === "untis_to_mis" && (
          <div className="space-y-6">
            <div className="p-3 bg-slate-900/50 border border-slate-800 rounded-xl text-xs text-slate-400">
              <span className="font-semibold text-emerald-400">
                Secondary Pipeline:
              </span>{" "}
              Ingest an Untis XML timetable file to stage schedule deltas and
              deploy directly to {targetMis}.
            </div>

            <XmlUploadZone onUploadSuccess={loadPipelineData} />

            <PreFlightRunner
              targetMis={targetMis}
              onPublishComplete={loadPipelineData}
            />

            {optionBlocks.length > 0 && (
              <OptionGroupViewer optionBlocks={optionBlocks} />
            )}

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                    Timetable Diff Ledger
                  </h3>
                  <p className="text-xs text-slate-400">
                    Calculated differences between incoming Untis schedule and
                    active {targetMis} timetable
                  </p>
                </div>
                <button
                  onClick={loadPipelineData}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-300 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                  <RefreshCw
                    className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
                  />
                  <span>Refresh Delta</span>
                </button>
              </div>

              <TimetableDiffGrid diffs={stagedDiffs} />
            </div>
          </div>
        )}

        {/* KEY REGISTRY TAB */}
        {activeTab === "registry" && <KeyRegistryDesk />}
      </main>
    </div>
  );
}
