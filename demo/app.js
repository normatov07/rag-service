(() => {
  const $ = (id) => document.getElementById(id);

  const state = {
    lastJobId: null,
  };

  function setStatus(el, data, ok = true) {
    el.classList.remove("ok", "err");
    el.classList.add(ok ? "ok" : "err");
    el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  }

  function authHeaders() {
    const token = $("bearerToken").value.trim();
    if (!token) {
      throw new Error("Bearer token is required");
    }
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  function baseUrl() {
    return $("baseUrl").value.trim().replace(/\/+$/, "");
  }

  function readMetadata() {
    const metadata = {
      type: "",
      url: $("metaUrl").value.trim(),
      url_unique_id: $("metaUrlUniqueId").value.trim(),
      source: $("sourceName").value.trim() || "platform",
      format: $("metaFormat").value.trim(),
      id: Number($("metaId").value) || undefined,
      uuid: $("metaUuid").value.trim(),
      permission: $("metaPermission").value.trim(),
      department: $("metaDepartment").value.trim(),
      division: $("metaDivision").value.trim(),
      user_id: Number($("metaUserId").value) || undefined,
      group: $("metaGroup").value.trim(),
    };

    Object.keys(metadata).forEach((k) => {
      if (metadata[k] === "" || metadata[k] === undefined || metadata[k] === null) {
        delete metadata[k];
      }
    });

    return metadata;
  }

  function mapSourceType() {
    const kind = $("sourceKind").value;
    if (kind === "text") {
      return "text";
    }
    if (kind === "video") {
      return "video";
    }
    if (kind === "audio") {
      // Current backend model supports text/file/video source types.
      // For audio testing, we send transcript using video pipeline.
      return "video";
    }
    return "file";
  }

  async function sendIngestion() {
    const statusEl = $("ingestionStatus");
    try {
      setStatus(statusEl, "Sending ingestion request...");
      const srcType = mapSourceType();
      const file = $("uploadFile").files[0] || null;
      const transcript = $("textContent").value.trim();
      const tenantId = $("tenantId").value.trim();

      const form = new FormData();
      form.append("source_type", srcType);
      if (tenantId) {
        form.append("tenant_id", tenantId);
      }

      const source = $("sourceName").value.trim() || "platform";
      form.append("source", source);

      if (file) {
        form.append("file", file);
      }

      if (srcType === "text") {
        form.append("text_content", transcript);
      } else if (srcType === "video") {
        // supports both video and audio transcript mode
        form.append("video_transcript", transcript);
      } else {
        // file flow can still accept text_content fallback
        if (transcript) {
          form.append("text_content", transcript);
        }
      }

      const metadata = readMetadata();
      metadata.type = $("sourceKind").value;

      // flatten known metadata contract fields
      [
        "url",
        "url_unique_id",
        "source",
        "format",
        "id",
        "uuid",
        "permission",
        "department",
        "division",
        "user_id",
        "group",
      ].forEach((k) => {
        if (metadata[k] !== undefined) {
          form.append(k, String(metadata[k]));
        }
      });

      const res = await fetch(`${baseUrl()}/ingestions/`, {
        method: "POST",
        headers: {
          ...authHeaders(),
        },
        body: form,
      });

      const body = await safeJson(res);
      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}\n${JSON.stringify(body, null, 2)}`);
      }

      state.lastJobId = body.id;
      setStatus(statusEl, body, true);
    } catch (err) {
      setStatus(statusEl, err.message || String(err), false);
    }
  }

  async function pollJob() {
    const statusEl = $("ingestionStatus");
    try {
      if (!state.lastJobId) {
        throw new Error("No job id yet. Send ingestion request first.");
      }
      setStatus(statusEl, `Polling job ${state.lastJobId} ...`);

      const res = await fetch(`${baseUrl()}/ingestions/${state.lastJobId}/`, {
        headers: {
          ...authHeaders(),
        },
      });

      const body = await safeJson(res);
      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}\n${JSON.stringify(body, null, 2)}`);
      }

      setStatus(statusEl, body, true);
    } catch (err) {
      setStatus(statusEl, err.message || String(err), false);
    }
  }

  function buildFilters() {
    const filters = {
      department: $("fDepartment").value.trim(),
      division: $("fDivision").value.trim(),
      group: $("fGroup").value.trim(),
      user_id: Number($("fUserId").value) || undefined,
    };

    Object.keys(filters).forEach((k) => {
      if (filters[k] === "" || filters[k] === undefined || filters[k] === null) {
        delete filters[k];
      }
    });

    return filters;
  }

  async function runQuery() {
    const statusEl = $("queryStatus");
    try {
      setStatus(statusEl, "Running semantic search...");
      const prompt = $("promptInput").value.trim();
      if (!prompt) {
        throw new Error("Prompt is required.");
      }

      const payload = {
        prompt,
        top_k: Number($("topK").value) || 5,
        filters: buildFilters(),
      };

      const tenantId = $("tenantId").value.trim();
      if (tenantId) {
        payload.tenant_id = tenantId;
      }

      const res = await fetch(`${baseUrl()}/query/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify(payload),
      });

      const body = await safeJson(res);
      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}\n${JSON.stringify(body, null, 2)}`);
      }

      setStatus(statusEl, body, true);
    } catch (err) {
      setStatus(statusEl, err.message || String(err), false);
    }
  }

  async function safeJson(res) {
    const txt = await res.text();
    if (!txt) {
      return {};
    }
    try {
      return JSON.parse(txt);
    } catch {
      return { raw: txt };
    }
  }

  $("btnIngest").addEventListener("click", sendIngestion);
  $("btnPollJob").addEventListener("click", pollJob);
  $("btnQuery").addEventListener("click", runQuery);
})();
