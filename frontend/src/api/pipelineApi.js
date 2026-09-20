// frontend/src/api/pipelineApi.js

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

  // Primary: MIS to Untis Extraction & Synthetic Ingestion
  previewMisSchedule: async (targetMis = "ARBOR") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    const response = await apiClient.get(`/reverse-sync/preview`, {
      params: { target_mis: normalizedMis },
    });
    return response.data;
  },

  uploadSyntheticMisFile: async (file, targetMis = "ARBOR") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post(
      `/reverse-sync/upload-synthetic?target_mis=${encodeURIComponent(normalizedMis)}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  },

  getDifDownloadUrl: (targetMis = "ARBOR") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    return `/api/v1/reverse-sync/export-dif?target_mis=${encodeURIComponent(normalizedMis)}`;
  },

  // Quarantine Conflict Desk
  getQuarantineItems: async (status = "PENDING") => {
    const response = await apiClient.get("/quarantine", {
      params: { status: status.toUpperCase() },
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

  // Secondary / Optional: Untis to MIS Deployment
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

  getStagedDiffs: async (targetMis = "ARBOR", status = "STAGED") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    const response = await apiClient.get("/diff", {
      params: {
        target_mis: normalizedMis,
        status: status.toUpperCase(),
      },
    });
    return response.data;
  },

  runDryRun: async (targetMis = "ARBOR") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    const response = await apiClient.post("/diff/dry-run", null, {
      params: {
        target_mis: normalizedMis,
      },
    });
    return response.data;
  },

  publishDeployment: async (targetMis = "ARBOR") => {
    const normalizedMis = (targetMis || "ARBOR").toUpperCase();
    const response = await apiClient.post("/publish", null, {
      params: {
        target_mis: normalizedMis,
      },
    });
    return response.data;
  },

  // Identity Cross-Reference Registry
  getKeyRegistry: async (search = "", entityType = "") => {
    const params = {};
    if (search) params.search = search;
    if (entityType) params.entity_type = entityType;
    const response = await apiClient.get("/registry", { params });
    return response.data;
  },
};

export default pipelineApi;
