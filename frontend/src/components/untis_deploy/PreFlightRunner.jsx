import React, { useState } from "react";
import { Play, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function PreFlightRunner({ targetMis, onPublishComplete }) {
  const [simulating, setSimulating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [publishResult, setPublishResult] = useState(null);
  const [error, setError] = useState(null);

  const runSimulation = async () => {
    setError(null);
    setSimulating(true);
    try {
      const res = await pipelineApi.runDryRunSimulation(targetMis);
      setSimulationResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Pre-flight simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  const executePublish = async () => {
    if (
      !window.confirm(`Deploy all staged timetable diffs to live ${targetMis}?`)
    )
      return;
    setError(null);
    setPublishing(true);
    try {
      const res = await pipelineApi.publishToMis(targetMis);
      setPublishResult(res);
      if (onPublishComplete) onPublishComplete(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Publication failed");
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Pre-Flight Simulation & Live Deployment
          </h3>
          <p className="text-xs text-slate-400">Target platform: {targetMis}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={runSimulation}
            disabled={simulating || publishing}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 disabled:opacity-50 transition-colors"
          >
            <Play
              className={`w-3.5 h-3.5 ${simulating ? "animate-spin" : ""}`}
            />
            <span>{simulating ? "Simulating..." : "Run Dry-Run"}</span>
          </button>

          <button
            onClick={executePublish}
            disabled={publishing || simulating}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 transition-colors shadow"
          >
            <ArrowRight className="w-3.5 h-3.5" />
            <span>{publishing ? "Publishing..." : "Deploy to MIS"}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-950/40 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {simulationResult && (
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
          <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <CheckCircle2 className="w-4 h-4" />
            <span>Pre-Flight Simulation Succeeded</span>
          </div>
          <div className="grid grid-cols-4 gap-2 text-center text-[11px] font-mono">
            <div className="p-1.5 bg-slate-900 rounded">
              Creates: {simulationResult.projected_creates}
            </div>
            <div className="p-1.5 bg-slate-900 rounded">
              Updates: {simulationResult.projected_updates}
            </div>
            <div className="p-1.5 bg-slate-900 rounded">
              Deletions: {simulationResult.projected_deletions}
            </div>
            <div className="p-1.5 bg-slate-900 rounded">
              Unchanged: {simulationResult.projected_unchanged}
            </div>
          </div>
        </div>
      )}

      {publishResult && (
        <div className="p-3 bg-emerald-950/30 border border-emerald-500/30 rounded-lg text-xs space-y-1">
          <p className="font-semibold text-emerald-400">Deployment Complete</p>
          <p className="text-slate-300 text-[11px]">
            Successfully committed: {publishResult.committed_count} slots |
            Failed: {publishResult.failed_count}
          </p>
        </div>
      )}
    </div>
  );
}
