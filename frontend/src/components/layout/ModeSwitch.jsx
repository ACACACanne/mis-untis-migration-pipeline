// frontend/src/components/layout/ModeSwitch.jsx

import React from "react";
import { DownloadCloud, ShieldAlert, UploadCloud, Key } from "lucide-react";

export default function ModeSwitch({
  activeTab,
  setActiveTab,
  quarantineCount = 0,
}) {
  const tabs = [
    {
      id: "mis_to_untis",
      label: "MIS ➔ Untis Extraction",
      sublabel: "Primary Pipeline",
      icon: DownloadCloud,
      badge: "Primary",
    },
    {
      id: "quarantine",
      label: "Quarantine Desk",
      sublabel: "Collision Resolution",
      icon: ShieldAlert,
      badgeCount: quarantineCount,
    },
    {
      id: "untis_to_mis",
      label: "Untis ➔ MIS Deployment",
      sublabel: "Secondary / Optional",
      icon: UploadCloud,
      badge: "Secondary",
    },
    {
      id: "registry",
      label: "Key Registry",
      sublabel: "Cross-Reference Map",
      icon: Key,
    },
  ];

  return (
    <div className="flex border-b border-slate-800 space-x-2">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2.5 px-4 py-3 text-xs font-medium border-b-2 transition-all ${
              isActive
                ? "border-emerald-500 text-emerald-400 bg-slate-900/40"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700"
            }`}
          >
            <Icon
              className={`w-4 h-4 ${
                isActive ? "text-emerald-400" : "text-slate-400"
              }`}
            />
            <div className="text-left">
              <div className="flex items-center gap-1.5">
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded font-semibold border ${
                      tab.badge === "Primary"
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
                {tab.badgeCount > 0 && (
                  <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    {tab.badgeCount}
                  </span>
                )}
              </div>
              <p className="text-[10px] text-slate-500">{tab.sublabel}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
