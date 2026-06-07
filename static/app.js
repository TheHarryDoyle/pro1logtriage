const elements = {
  apiStatus: document.querySelector("#apiStatus"),
  textTab: document.querySelector("#textTab"),
  fileTab: document.querySelector("#fileTab"),
  textView: document.querySelector("#textView"),
  fileView: document.querySelector("#fileView"),
  rawLog: document.querySelector("#rawLog"),
  logFile: document.querySelector("#logFile"),
  fileName: document.querySelector("#fileName"),
  analyzeText: document.querySelector("#analyzeText"),
  analyzeFile: document.querySelector("#analyzeFile"),
  resultCard: document.querySelector("#resultCard"),
  severityRules: document.querySelector("#severityRules"),
  componentRules: document.querySelector("#componentRules"),
  triageRules: document.querySelector("#triageRules"),
  severityForm: document.querySelector("#severityForm"),
  severityName: document.querySelector("#severityName"),
  severityKeywords: document.querySelector("#severityKeywords"),
  componentForm: document.querySelector("#componentForm"),
  componentName: document.querySelector("#componentName"),
  componentKeywords: document.querySelector("#componentKeywords"),
  triageForm: document.querySelector("#triageForm"),
  triageCategory: document.querySelector("#triageCategory"),
  triageConfidence: document.querySelector("#triageConfidence"),
  triageKeywords: document.querySelector("#triageKeywords"),
  triageAction: document.querySelector("#triageAction"),
  triageCommands: document.querySelector("#triageCommands"),
  ruleMessage: document.querySelector("#ruleMessage"),
  recentLogs: document.querySelector("#recentLogs"),
  refreshRules: document.querySelector("#refreshRules"),
  refreshRecent: document.querySelector("#refreshRecent"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setStatus(text, className) {
  elements.apiStatus.textContent = text;
  elements.apiStatus.className = `status-pill ${className || ""}`.trim();
}

function showTab(tabName) {
  const isText = tabName === "text";
  elements.textTab.classList.toggle("active", isText);
  elements.fileTab.classList.toggle("active", !isText);
  elements.textView.classList.toggle("active", isText);
  elements.fileView.classList.toggle("active", !isText);
}

function setLoading(message) {
  elements.resultCard.innerHTML = `<div class="loading-state">${escapeHtml(message)}</div>`;
}

function setError(message) {
  elements.resultCard.innerHTML = `<div class="error-state">${escapeHtml(message)}</div>`;
}

function setRuleMessage(message, className) {
  elements.ruleMessage.textContent = message;
  elements.ruleMessage.className = `form-message ${className || ""}`.trim();
}

function parseCommaList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseLineList(value) {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

function renderAnalysis(result) {
  const commands = result.commands_to_check?.length
    ? result.commands_to_check
    : ["No command suggestions returned."];

  const lines = result.analyzed_lines?.length
    ? result.analyzed_lines
    : ["No analyzed lines returned."];

  elements.resultCard.innerHTML = `
    <div class="summary-grid">
      <div class="metric"><span>Severity</span><strong>${escapeHtml(result.severity)}</strong></div>
      <div class="metric"><span>Component</span><strong>${escapeHtml(result.component)}</strong></div>
      <div class="metric"><span>Category</span><strong>${escapeHtml(result.category)}</strong></div>
      <div class="metric"><span>Confidence</span><strong>${escapeHtml(Math.round((result.confidence || 0) * 100))}%</strong></div>
      <div class="metric"><span>Lines</span><strong>${escapeHtml(result.line_count)}</strong></div>
    </div>
    <div class="detail-block">
      <h3>Suggested Action</h3>
      <p>${escapeHtml(result.suggested_actions)}</p>
    </div>
    <div class="detail-block">
      <h3>Commands to Check</h3>
      <ul class="command-list">
        ${commands.map((command) => `<li>${escapeHtml(command)}</li>`).join("")}
      </ul>
    </div>
    <div class="detail-block">
      <h3>Analyzed Lines</h3>
      <ul class="line-list">
        ${lines.map((line) => `<li>${escapeHtml(line)}</li>`).join("")}
      </ul>
    </div>
  `;
}

async function analyzeText() {
  const rawLog = elements.rawLog.value.trim();
  if (!rawLog) {
    setError("Paste a log entry first.");
    return;
  }

  elements.analyzeText.disabled = true;
  setLoading("Analyzing pasted log...");

  try {
    const result = await fetchJson("/logs/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_log: rawLog }),
    });
    renderAnalysis(result);
    await loadRecent();
  } catch (error) {
    setError(error.message);
  } finally {
    elements.analyzeText.disabled = false;
  }
}

async function analyzeFile() {
  const file = elements.logFile.files[0];
  if (!file) {
    setError("Choose a log file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  elements.analyzeFile.disabled = true;
  setLoading(`Analyzing ${file.name}...`);

  try {
    const result = await fetchJson("/logs/analyze-file", {
      method: "POST",
      body: formData,
    });
    renderAnalysis(result);
    await loadRecent();
  } catch (error) {
    setError(error.message);
  } finally {
    elements.analyzeFile.disabled = false;
  }
}

function renderTupleRule(rule) {
  const name = Array.isArray(rule) ? rule[0] : rule.name || rule.component || "Rule";
  const keywords = Array.isArray(rule) ? rule[1] : rule.keywords || [];
  return `
    <div class="rule-card">
      <div class="rule-title">${escapeHtml(name)}</div>
      <div class="chips">
        ${keywords.map((keyword) => `<span class="chip">${escapeHtml(keyword)}</span>`).join("")}
      </div>
    </div>
  `;
}

function renderTriageRule(rule) {
  return `
    <div class="rule-card">
      <div class="rule-title">
        <span>${escapeHtml(rule.category)}</span>
        <span class="confidence">${escapeHtml(Math.round((rule.confidence || 0) * 100))}%</span>
      </div>
      <div class="chips">
        ${(rule.keywords || []).map((keyword) => `<span class="chip">${escapeHtml(keyword)}</span>`).join("")}
      </div>
      <p class="rule-note">${escapeHtml(rule.suggested_actions)}</p>
    </div>
  `;
}

async function loadRules() {
  elements.refreshRules.disabled = true;
  try {
    const [severity, components, triage] = await Promise.all([
      fetchJson("/rules/severity"),
      fetchJson("/rules/components"),
      fetchJson("/rules/triage"),
    ]);

    elements.severityRules.innerHTML = severity.rules.map(renderTupleRule).join("");
    elements.componentRules.innerHTML = components.rules.map(renderTupleRule).join("");
    elements.triageRules.innerHTML = triage.rules.map(renderTriageRule).join("");
  } catch (error) {
    elements.triageRules.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  } finally {
    elements.refreshRules.disabled = false;
  }
}

async function createRule(url, payload) {
  return fetchJson(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function addSeverityRule(event) {
  event.preventDefault();
  const name = elements.severityName.value.trim();
  const keywords = parseCommaList(elements.severityKeywords.value);

  if (!name || keywords.length === 0) {
    setRuleMessage("Severity needs a name and at least one keyword.", "error");
    return;
  }

  const button = elements.severityForm.querySelector("button");
  button.disabled = true;
  setRuleMessage("Adding severity rule...", "");

  try {
    await createRule("/rules/severity", { name, keywords });
    elements.severityForm.reset();
    setRuleMessage("Severity rule added.", "success");
    await loadRules();
  } catch (error) {
    setRuleMessage(error.message, "error");
  } finally {
    button.disabled = false;
  }
}

async function addComponentRule(event) {
  event.preventDefault();
  const component = elements.componentName.value.trim();
  const keywords = parseCommaList(elements.componentKeywords.value);

  if (!component || keywords.length === 0) {
    setRuleMessage("Component needs a name and at least one keyword.", "error");
    return;
  }

  const button = elements.componentForm.querySelector("button");
  button.disabled = true;
  setRuleMessage("Adding component rule...", "");

  try {
    await createRule("/rules/components", { component, keywords });
    elements.componentForm.reset();
    setRuleMessage("Component rule added.", "success");
    await loadRules();
  } catch (error) {
    setRuleMessage(error.message, "error");
  } finally {
    button.disabled = false;
  }
}

async function addTriageRule(event) {
  event.preventDefault();
  const category = elements.triageCategory.value.trim();
  const confidence = Number(elements.triageConfidence.value);
  const keywords = parseCommaList(elements.triageKeywords.value);
  const suggested_actions = elements.triageAction.value.trim();
  const commands_to_check = parseLineList(elements.triageCommands.value);

  if (!category || keywords.length === 0 || !suggested_actions) {
    setRuleMessage("Triage needs a category, keywords, and suggested action.", "error");
    return;
  }

  if (Number.isNaN(confidence) || confidence < 0 || confidence > 1) {
    setRuleMessage("Confidence must be between 0 and 1.", "error");
    return;
  }

  const button = elements.triageForm.querySelector("button");
  button.disabled = true;
  setRuleMessage("Adding triage rule...", "");

  try {
    await createRule("/rules/triage", {
      category,
      keywords,
      confidence,
      suggested_actions,
      commands_to_check,
    });
    elements.triageForm.reset();
    elements.triageConfidence.value = "0.8";
    setRuleMessage("Triage rule added.", "success");
    await loadRules();
  } catch (error) {
    setRuleMessage(error.message, "error");
  } finally {
    button.disabled = false;
  }
}

function renderRecentCard(log) {
  const firstLines = (log.analyzed_lines || []).slice(0, 4).join("\n") || log.raw_log || "";
  return `
    <article class="recent-card">
      <h3>${escapeHtml(log.category)} / ${escapeHtml(log.severity)}</h3>
      <p>${escapeHtml(log.component)} | ${escapeHtml(Math.round((log.confidence || 0) * 100))}% | ${escapeHtml(log.created_at)}</p>
      <pre>${escapeHtml(firstLines)}</pre>
    </article>
  `;
}

async function loadRecent() {
  elements.refreshRecent.disabled = true;
  try {
    const data = await fetchJson("/logs/recent");
    const logs = data.logs || [];
    elements.recentLogs.innerHTML = logs.length
      ? logs.map(renderRecentCard).join("")
      : `<div class="empty-state">No recent analyses yet.</div>`;
  } catch (error) {
    elements.recentLogs.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  } finally {
    elements.refreshRecent.disabled = false;
  }
}

async function checkApi() {
  try {
    await fetchJson("/health");
    setStatus("API ready", "ready");
  } catch {
    setStatus("API offline", "error");
  }
}

elements.textTab.addEventListener("click", () => showTab("text"));
elements.fileTab.addEventListener("click", () => showTab("file"));
elements.analyzeText.addEventListener("click", analyzeText);
elements.analyzeFile.addEventListener("click", analyzeFile);
elements.refreshRules.addEventListener("click", loadRules);
elements.refreshRecent.addEventListener("click", loadRecent);
elements.severityForm.addEventListener("submit", addSeverityRule);
elements.componentForm.addEventListener("submit", addComponentRule);
elements.triageForm.addEventListener("submit", addTriageRule);
elements.logFile.addEventListener("change", () => {
  elements.fileName.textContent = elements.logFile.files[0]?.name || "Choose a .log or .txt file";
});

checkApi();
loadRules();
loadRecent();
