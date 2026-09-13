import React, { useEffect, useState } from "react";
import { Database, Server, RefreshCw, Layers } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function Header({ targetMis, setTargetMis }) {
  const [health, setHealth] = useState({
    database: "loading",
    arbor_api: "loading",
    bromcom_api: "loading",
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchStatus = async () => {
    setIsRefreshing(true);
    try {
      const res = await pipelineApi.getHealth();
      setHealth(res);
    } catch {
      setHealth({
        database: "offline",
        arbor_api: "offline",
        bromcom_api: "offline",
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getBadge = (status) => {
    const isOnline = status === "connected";
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
          isOnline
            ? "bg-emerald-950/60 border-emerald-500/30 text-emerald-400"
            : "bg-rose-950/60 border-rose-500/30 text-rose-400"
        }`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full ${isOnline ? "bg-emerald-400" : "bg-rose-400"}`}
        />
        {status}
      </span>
    );
  };

  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-center text-emerald-400">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-white">
              Untis <span className="text-emerald-400">↔</span> UK MIS Bridge
            </h1>
            <p className="text-xs text-slate-400">
              Production Timetable Migration & Reverse Sync
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Database className="w-3.5 h-3.5" /> DB:
            </span>
            {getBadge(health.database)}

            <span className="text-slate-400 flex items-center gap-1 ml-2">
              <Server className="w-3.5 h-3.5" /> Arbor:
            </span>
            {getBadge(health.arbor_api)}

            <span className="text-slate-400 flex items-center gap-1 ml-2">
              <Server className="w-3.5 h-3.5" /> Bromcom:
            </span>
            {getBadge(health.bromcom_api)}

            <button
              onClick={fetchStatus}
              className="ml-2 text-slate-400 hover:text-white transition-colors"
              title="Refresh connection status"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`}
              />
            </button>
          </div>

          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs font-medium">
            <button
              onClick={() => setTargetMis("ARBOR")}
              className={`px-3 py-1 rounded-md transition-colors ${
                targetMis === "ARBOR"
                  ? "bg-emerald-500 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Arbor
            </button>
            <button
              onClick={() => setTargetMis("BROMCOM")}
              className={`px-3 py-1 rounded-md transition-colors ${
                targetMis === "BROMCOM"
                  ? "bg-emerald-500 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Bromcom
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
