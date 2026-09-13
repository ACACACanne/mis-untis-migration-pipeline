import React from "react";
import { Loader2 } from "lucide-react";

const VARIANT_STYLES = {
  default: {
    border: "border-slate-800",
    iconBg: "bg-slate-800/80 text-slate-300",
    value: "text-slate-100",
  },
  success: {
    border: "border-emerald-500/30",
    iconBg: "bg-emerald-500/10 text-emerald-400",
    value: "text-emerald-300",
  },
  warning: {
    border: "border-amber-500/30",
    iconBg: "bg-amber-500/10 text-amber-400",
    value: "text-amber-300",
  },
  danger: {
    border: "border-rose-500/30",
    iconBg: "bg-rose-500/10 text-rose-400",
    value: "text-rose-300",
  },
};

export default function MetricCard({
  title,
  value,
  icon: Icon,
  subtitle,
  variant = "default",
  loading = false,
  badge,
  onClick,
}) {
  const styles = VARIANT_STYLES[variant] || VARIANT_STYLES.default;

  return (
    <div
      onClick={onClick}
      className={`relative bg-slate-900/60 backdrop-blur-sm border rounded-xl p-4 transition-all duration-150 ${
        styles.border
      } ${onClick ? "cursor-pointer hover:bg-slate-800/40 hover:border-slate-700" : ""}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
            {title}
          </p>
          <div className="flex items-baseline gap-2">
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin text-slate-500 mt-1" />
            ) : (
              <span
                className={`text-2xl font-bold tracking-tight font-mono ${styles.value}`}
              >
                {value ?? "—"}
              </span>
            )}
            {badge && (
              <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-[11px] text-slate-500 font-sans">{subtitle}</p>
          )}
        </div>

        {Icon && (
          <div className={`p-2.5 rounded-lg shrink-0 ${styles.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
}
