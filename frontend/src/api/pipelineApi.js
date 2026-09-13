import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

export const pipelineApi = {
  // System Health & Telemetry
  getHealth: async () => {
    const response = await apiClient.get("/health");
    return response.data;
  },

  // Primary Ingestion: Untis XML Upload
  uploadUntisXml: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Staged Delta Management & Pre-Flight Simulation
  getStagedDiffs: async (targetMis = "ARBOR", status = "STAGED") => {
    const response = await apiClient.get("/diff", {
      params: {
        target_mis: targetMis.toUpperCase(),
        status: status.toUpperCase(),
      },
    });
    return response.data;
  },

  runDryRun: async (targetMis = "ARBOR") => {
    const response = await apiClient.post("/diff/dry-run", null, {
      params: {
        target_mis: targetMis.toUpperCase(),
      },
    });
    return response.data;
  },

  // Target MIS Live Deployment
  publishDeployment: async (targetMis = "ARBOR") => {
    const response = await apiClient.post("/publish", null, {
      params: {
        target_mis: targetMis.toUpperCase(),
      },
    });
    return response.data;
  },

  // Quarantine Desk & Conflict Remediation
  getQuarantineItems: async (status = "PENDING") => {
    const response = await apiClient.get("/quarantine", {
      params: {
        status: status.toUpperCase(),
      },
    });
    return response.data;
  },

  getQuarantineSummary: async () => {
    const response = await apiClient.get("/quarantine/summary");
    return response.data;
  },

  resolveQuarantineItem: async (itemId, overridePayload) => {
    const response = await apiClient.patch(
      `/quarantine/${itemId}/resolve`,
      overridePayload,
    );
    return response.data;
  },

  // Reverse Master Sync (MIS to Untis DIF)
  previewMisSchedule: async (targetMis = "ARBOR") => {
    const response = await apiClient.get("/reverse-sync/preview", {
      params: {
        target_mis: targetMis.toUpperCase(),
      },
    });
    return response.data;
  },

  getMisMasterPreview: async (targetMis = "ARBOR") => {
    const response = await apiClient.get("/reverse-sync/preview", {
      params: {
        target_mis: targetMis.toUpperCase(),
      },
    });
    return response.data;
  },

  getDifDownloadUrl: (targetMis = "ARBOR") => {
    return `/api/v1/reverse-sync/export-dif?target_mis=${targetMis.toUpperCase()}`;
  },

  // Cross-System Key Registry
  getKeyRegistry: async (search = "", entityType = "") => {
    const params = {};
    if (search) params.search = search;
    if (entityType) params.entity_type = entityType;
    const response = await apiClient.get("/registry", { params });
    return response.data;
  },
};

export default pipelineApi;
