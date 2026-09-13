// frontend/src/App.jsx

import React, { useState, useEffect } from "react";
import {
  Layers,
  ShieldAlert,
  PlusCircle,
  RefreshCw,
  Clock,
  FileCheck2,
} from "lucide-react";

import Header from "./components/layout/Header";
import ModeSwitch from "./components/layout/ModeSwitch";
import MetricCard from "./components/layout/MetricCard";
import XmlUploadZone from "./components/untis_deploy/XmlUploadZone";
import TimetableDiffGrid from "./components/untis_deploy/TimetableDiffGrid";
import OptionGroupViewer from "./components/untis_deploy/OptionGroupViewer";
import PreFlightRunner from "./components/untis_deploy/PreFlightRunner";
import QuarantineDesk from "./components/quarantine/QuarantineDesk";
import MisMasterPull from "./components/reverse_sync/MisMasterPull";
import DifExportAction from "./components/reverse_sync/DifExportAction";
import KeyRegistryDesk from "./components/registry/KeyRegistryDesk";
import { pipelineApi } from "./api/pipelineApi";

export default function App() {
  const [activeTab, setActiveTab] = useState("deploy");
  const [targetMis, setTargetMis] = useState("ARBOR");
  const [stagedDiffs, setStagedDiffs] = useState([]);
  const [quarantineSummary, setQuarantineSummary] = useState({
    total_quarantined: 0,
    pending_count: 0,
    resolved_count: 0,
    ignored_count: 0,
  });
  const [optionBlocks, setOptionBlocks] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadPipelineData = async () => {
    setLoading(true);
    try {
      const [diffs, qSummary] = await Promise.all([
        pipelineApi.getStagedDiffs(targetMis),
        pipelineApi.getQuarantineSummary(),
      ]);

      setStagedDiffs(diffs);
      setQuarantineSummary(qSummary);

      // Deduplicate option blocks across repeating timetable periods
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

          if (!groupsMap.has(groupId)) {
            groupsMap.set(groupId, {
              group_identifier: groupId,
              subject_code: d.slot_payload?.subject_code,
              academic_cohort: d.slot_payload?.class_code,
              student_count: d.slot_payload?.assigned_students?.length || 0,
              students: (d.slot_payload?.assigned_students || []).map((id) => ({
                untis_student_id: id,
                student_name: id.replace("ST_", ""),
                base_class: d.slot_payload?.class_code,
              })),
            });
          } else {
            const existing = groupsMap.get(groupId);
            const assigned = d.slot_payload?.assigned_students || [];
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
    } catch {
      // Backend diagnostic logs capture connection/parsing failures
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPipelineData();
  }, [targetMis]);

  const handleUploadSuccess = () => {
    loadPipelineData();
  };

  const createsCount = stagedDiffs.filter(
    (d) => d.change_type === "CREATE",
  ).length;
  const updatesCount = stagedDiffs.filter(
    (d) => d.change_type === "UPDATE",
  ).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased">
      <Header targetMis={targetMis} setTargetMis={setTargetMis} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">
        <ModeSwitch
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          quarantineCount={quarantineSummary.pending_count}
        />

        {/* Global Pipeline Telemetry Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetricCard
            title="Staged Changes"
            value={stagedDiffs.length}
            icon={Layers}
            subtitle={`${createsCount} creates, ${updatesCount} modifications`}
            variant={stagedDiffs.length > 0 ? "success" : "default"}
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
            title="Target Environment"
            value={targetMis}
            icon={Clock}
            subtitle="API v1 Connected"
            badge="Live Mode"
          />
          <MetricCard
            title="Elective Blocks"
            value={optionBlocks.length}
            icon={FileCheck2}
            subtitle="Identified option groups"
            variant={optionBlocks.length > 0 ? "warning" : "default"}
            loading={loading}
          />
        </div>

        {/* Primary Pipeline View: Untis Deploy */}
        {activeTab === "deploy" && (
          <div className="space-y-6">
            <XmlUploadZone onUploadSuccess={handleUploadSuccess} />

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
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-300 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors"
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

        {/* Quarantine Desk View */}
        {activeTab === "quarantine" && (
          <QuarantineDesk onResolved={loadPipelineData} />
        )}

        {/* Reverse Sync View: MIS to Untis DIF */}
        {activeTab === "reverse_sync" && (
          <div className="space-y-6">
            <MisMasterPull targetMis={targetMis} />
            <DifExportAction targetMis={targetMis} />
          </div>
        )}

        {/* Key Registry Cross-Reference Explorer */}
        {activeTab === "registry" && <KeyRegistryDesk />}
      </main>
    </div>
  );
}
