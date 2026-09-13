import React from "react";
import {
  UploadCloud,
  ShieldAlert,
  DownloadCloud,
  KeyRound,
} from "lucide-react";

export default function ModeSwitch({
  activeTab,
  setActiveTab,
  quarantineCount = 0,
}) {
  const tabs = [
    { id: "deploy", label: "Untis Deployment", icon: UploadCloud },
    {
      id: "quarantine",
      label: "Quarantine Desk",
      icon: ShieldAlert,
      badge: quarantineCount,
    },
    { id: "reverse_sync", label: "Reverse Master Sync", icon: DownloadCloud },
    { id: "registry", label: "Key Registry", icon: KeyRound },
  ];

  return (
    <nav className="flex space-x-2 border-b border-slate-800 pb-2">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              isActive
                ? "bg-slate-800 text-emerald-400 border border-slate-700 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{tab.label}</span>
            {tab.badge > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
