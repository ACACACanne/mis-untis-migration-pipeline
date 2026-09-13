import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
  headers: {
    Accept: "application/json",
  },
});

export const pipelineApi = {
  // System Health
  getHealth: async () => {
    const { data } = await client.get("/health");
    return data;
  },

  // Upload & Stage Untis XML
  uploadUntisXml: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await client.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  // Timetable Diffs & Simulator
  getStagedDiffs: async (targetMis = "ARBOR", status = "STAGED") => {
    const { data } = await client.get("/diff", {
      params: { target_mis: targetMis, status },
    });
    return data;
  },

  runDryRunSimulation: async (targetMis = "ARBOR") => {
    const { data } = await client.post("/diff/dry-run", null, {
      params: { target_mis: targetMis },
    });
    return data;
  },

  // Publish / Commit to MIS
  publishToMis: async (targetMis = "ARBOR") => {
    const { data } = await client.post("/publish", null, {
      params: { target_mis: targetMis },
    });
    return data;
  },

  // Quarantine Management
  getQuarantineItems: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const { data } = await client.get("/quarantine", { params });
    return data;
  },

  getQuarantineSummary: async () => {
    const { data } = await client.get("/quarantine/summary");
    return data;
  },

  resolveQuarantineItem: async (itemId, status, resolvedOverride) => {
    const { data } = await client.patch(`/quarantine/${itemId}/resolve`, {
      status,
      resolved_override: resolvedOverride,
    });
    return data;
  },

  // Reverse Sync (MIS to Untis)
  previewMisCatalog: async (targetMis = "ARBOR") => {
    const { data } = await client.get("/reverse-sync/preview", {
      params: { target_mis: targetMis },
    });
    return data;
  },

  getDifExportUrl: (targetMis = "ARBOR") => {
    return `/api/v1/reverse-sync/export-dif?target_mis=${targetMis}`;
  },

  // Key Registry
  searchRegistry: async (query = "", entityType = "") => {
    const params = {};
    if (query) params.query = query;
    if (entityType) params.entity_type = entityType;
    const { data } = await client.get("/registry", { params });
    return data;
  },

  registerKeyMapping: async (mapping) => {
    const { data } = await client.post("/registry", mapping);
    return data;
  },
};
