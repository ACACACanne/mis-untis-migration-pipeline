import React from "react";
import { Download, FileSpreadsheet } from "lucide-react";
import { pipelineApi } from "../../api/pipelineApi";

export default function DifExportAction({ targetMis }) {
  const handleDownload = () => {
    window.location.href = pipelineApi.getDifExportUrl(targetMis);
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
          <FileSpreadsheet className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-xs font-semibold text-slate-200">
            Untis DIF Export Archive (GPU001–GPU005)
          </h4>
          <p className="text-xs text-slate-400">
            Bundles GPU001.txt through GPU005.txt ready for direct desktop Untis
            import.
          </p>
        </div>
      </div>

      <button
        onClick={handleDownload}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow transition-colors"
      >
        <Download className="w-3.5 h-3.5" />
        <span>Download Zip</span>
      </button>
    </div>
  );
}
