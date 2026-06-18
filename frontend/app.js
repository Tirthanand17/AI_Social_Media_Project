const api = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(async () => ({ message: await response.text().catch(() => "") }));
  if (!response.ok) throw new Error(data.message || `Request failed: ${response.status}`);
  return data;
};

const pretty = (value) => JSON.stringify(value, null, 2);
const byId = (id) => document.getElementById(id);
const setText = (id, value) => {
  const el = byId(id);
  if (!el) return;
  el.textContent = typeof value === "string" ? value : pretty(value);
};
const formJson = (form) => Object.fromEntries(new FormData(form).entries());
const platformForApi = (value) => (value === "X" ? "Twitter" : value);

let currentBrief = null;
let generatedCaption = "";
let currentPackage = null;

if ("scrollRestoration" in history) history.scrollRestoration = "manual";

function friendlyError(error) {
  const msg = String(error?.message || error || "Something went wrong");
  if (msg.includes("401") || msg.toLowerCase().includes("token")) return "API key missing or token not configured. Please check .env.";
  if (msg.includes("404")) return "API route not found. Please restart the backend after git pull.";
  if (msg.toLowerCase().includes("failed to fetch")) return "Backend is not running. Start uvicorn and open /app from port 8010.";
  return msg;
}

function showResult(id, result, successMessage = "Done") {
  if (result?.message) setText(id, `${result.message}\n\n${pretty(result)}`);
  else setText(id, `${successMessage}\n\n${pretty(result)}`);
}

function activateTab(target) {
  document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item.dataset.tab === target));
  document.querySelectorAll(".workspace").forEach((item) => item.classList.toggle("active", item.id === target));
  window.scrollTo({ top: 0, behavior: "auto" });
  if (target === "dashboard") loadDashboard();
  if (target === "analytics") loadAnalytics();
  if (target === "calendar") loadCalendar();
  if (target === "admin") {
    injectAdminWorkflow();
    loadCompetitors();
    loadIntegrations();
  }
}

function openLogin() {
  byId("loginModal")?.classList.add("open");
  byId("loginModal")?.setAttribute("aria-hidden", "false");
}

function closeLogin() {
  byId("loginModal")?.classList.remove("open");
  byId("loginModal")?.setAttribute("aria-hidden", "true");
}

function setUser(result) {
  if (!result?.success) return;
  const user = result.user || {};
  byId("userPill").textContent = `${user.role || "user"}: ${user.username || "logged in"}`;
}

function loginSummary(result) {
  if (!result?.success) return result;
  return { success: true, role: result.user?.role, username: result.user?.username, brand: result.user?.brand_name };
}

async function handleLogin(event, outputId) {
  event.preventDefault();
  try {
    const result = await api("/api/login", { method: "POST", body: JSON.stringify(formJson(event.currentTarget)) });
    setUser(result);
    showResult(outputId, loginSummary(result), "Login successful");
    if (result.success) closeLogin();
  } catch (error) {
    setText(outputId, friendlyError(error));
  }
}

async function checkHealth() {
  try {
    const [health, config] = await Promise.all([api("/api/health"), api("/api/config")]);
    const online = health.status === "ok";
    byId("apiStatus").textContent = online ? "Online" : "Issue";
    byId("apiStatus").classList.toggle("ok", online);
    byId("postingModeBadge").textContent = config.posting_mode || health.posting_mode || "dry_run";
    byId("postingMode").textContent = config.posting_mode || health.posting_mode || "dry_run";
  } catch (error) {
    byId("apiStatus").textContent = "Offline";
    setText("rawPostOutput", friendlyError(error));
  }
}

async function loadDashboard() {
  try {
    const [overview, integrations] = await Promise.all([api("/api/dataset-overview"), api("/api/integrations")]);
    const datasets = overview.datasets || [];
    byId("datasetCount").textContent = Array.isArray(datasets) ? datasets.length : overview.total_datasets || "--";
    byId("postingMode").textContent = integrations.posting_mode || "dry_run";
    byId("postingModeBadge").textContent = integrations.posting_mode || "dry_run";
    renderPlatformReadiness(integrations);
  } catch (error) {
    byId("datasetCount").textContent = "--";
    byId("platformReadiness").innerHTML = `<article class="platform-card warn"><strong>API</strong><span>${friendlyError(error)}</span></article>`;
  }
}

function renderPlatformReadiness(data = {}) {
  const linkedinReady = data.linkedin?.live_ready || data.linkedin?.access_token === "configured";
  const xReady = data.x?.live_ready || data.x?.bearer_token === "configured";
  const rows = [
    ["Instagram", true, "Dry-run ready. Live posting requires Meta permissions."],
    ["Facebook", true, "Dry-run ready. Live posting requires page token."],
    ["X", xReady, xReady ? "Live/status ready" : "Dry-run ready; write OAuth required for live posts."],
    ["LinkedIn", linkedinReady, linkedinReady ? "Live ready" : "Token/author setup needed for live publishing."],
  ];
  byId("platformReadiness").innerHTML = rows.map(([name, ok, note]) => `<article class="platform-card ${ok ? "ok" : "warn"}"><strong>${name}</strong><span>${note}</span></article>`).join("");
}

async function loadBrief() {
  try {
    const platform = platformForApi(byId("briefPlatform").value);
    currentBrief = await api(`/api/content/brief?platform=${encodeURIComponent(platform)}`);
    setText("briefOutput", {
      platform: currentBrief.platform,
      recommended_topic: currentBrief.recommended_topic,
      top_trends: currentBrief.top_trends,
      best_time: currentBrief.best_time,
      caption_examples: currentBrief.caption_examples,
    });
  } catch (error) {
    setText("briefOutput", friendlyError(error));
  }
}

function extractHashtags(data) {
  return data?.hashtag_string || data?.hashtags?.join(" ") || data?.recommended_hashtags?.join(" ") || (data ? pretty(data) : "Ready.");
}

function extractPredictionScore(prediction) {
  return prediction?.predicted_engagement_score ?? prediction?.engagement_score ?? prediction?.score ?? prediction?.prediction ?? 0;
}

function updateGauge(score) {
  const gauge = byId("predictionGauge");
  if (!gauge) return;
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
  const deg = Math.round((safeScore / 100) * 360);
  gauge.style.background = `radial-gradient(circle at center, #ffffff 0 58%, transparent 59%), conic-gradient(var(--primary) ${deg}deg, #edf2f7 ${deg}deg)`;
  gauge.querySelector("span").textContent = safeScore ? Math.round(safeScore) : "--";
}

function applyPostPackage(data) {
  currentPackage = data;
  generatedCaption = data.caption || "";
  const best = data.best_time ? `${data.best_time.day_of_week || data.best_time.day || ""} ${data.best_time.hour_posted ?? data.best_time.hour ?? ""}:00`.trim() : "Not available";
  setText("rawPostOutput", {
    platform: data.platform,
    campaign_goal: data.campaign_goal,
    caption: data.caption,
    hashtags: extractHashtags(data.hashtags),
    best_time: best,
    predicted_score: extractPredictionScore(data.engagement_prediction),
    publish_status: data.publish_preview?.status || data.publish_preview?.message || "dry_run preview",
  });
  setText("captionOutput", data.caption || "Ready.");
  setText("hashtagOutput", extractHashtags(data.hashtags));
  setText("safetyOutput", { moderation: data.moderation, plagiarism: data.plagiarism });
  setText("imagePromptOutput", data.image_prompt || "Ready.");
  updateGauge(extractPredictionScore(data.engagement_prediction));
  setText("predictionOutput", data.engagement_prediction || "Ready.");
  if (byId("publishCaption")) byId("publishCaption").value = data.caption || "";
  if (byId("publishPlatform")) byId("publishPlatform").value = data.platform === "Twitter" ? "X" : data.platform || "Instagram";
}

async function saveGeneratedPost() {
  const caption = generatedCaption || currentPackage?.caption || byId("captionOutput")?.textContent || "";
  if (!caption || caption.includes("Ready")) return setText("rawPostOutput", "Generate a caption/package before saving.");
  try {
    const result = await api("/api/db/posts", {
      method: "POST",
      body: JSON.stringify({
        caption,
        platform: currentPackage?.platform || platformForApi(byId("generateForm")?.elements.platform?.value || "Instagram"),
        hashtags: extractHashtags(currentPackage?.hashtags || {}),
        title: currentPackage?.campaign_goal || "Generated social post",
        image_prompt: pretty(currentPackage?.image_prompt || {}),
        content_type: "reel",
        created_by: "editor_creator",
      }),
    });
    showResult("rawPostOutput", result, "Post saved");
  } catch (error) {
    setText("rawPostOutput", friendlyError(error));
  }
}

function renderTable(id, rows, columns) {
  const table = byId(id);
  if (!table) return;
  if (!rows || rows.length === 0) return (table.innerHTML = "<tbody><tr><td>No data available</td></tr></tbody>");
  table.innerHTML = `<thead><tr>${columns.map((c) => `<th>${c.label}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${columns.map((c) => `<td>${String(r[c.key] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

function renderMetrics(analytics) {
  byId("metricStrip").innerHTML = [
    ["Posts", analytics.records],
    ["Reach", analytics.total_reach],
    ["Likes", analytics.total_likes],
    ["Avg ER", analytics.avg_engagement_rate],
  ].map(([label, value]) => `<article class="metric"><span>${label}</span><strong>${value ?? "--"}</strong><em>From analytics dataset</em></article>`).join("");
}

function renderBars(posts = []) {
  const max = Math.max(...posts.map((p) => Number(p.engagement_rate) || 0), 1);
  byId("engagementBars").innerHTML = posts.slice(0, 14).map((p) => `<span class="bar" title="${p.platform || "post"}: ${p.engagement_rate}" style="height:${Math.max(18, Math.round(((Number(p.engagement_rate) || 0) / max) * 100))}%"></span>`).join("");
}

function renderTrendCloud(trends = []) {
  byId("trendCloud").innerHTML = trends.slice(0, 18).map((i) => `<span class="trend-chip" style="font-size:${12 + Math.min(12, Number(i.trend_score || 0) / 10)}px">${i.keyword}</span>`).join("");
}

async function loadAnalytics() {
  try {
    const [analytics, trends, dbCharts] = await Promise.all([api("/api/analytics"), api("/api/trends"), api("/api/db/charts").catch(() => null)]);
    renderMetrics(analytics);
    renderBars(analytics.top_posts || []);
    const trendRows = trends.trending_keywords || [];
    renderTrendCloud(trendRows);
    renderTable("topPostsTable", analytics.top_posts || [], [
      { key: "post_id", label: "Post" }, { key: "platform", label: "Platform" }, { key: "likes", label: "Likes" }, { key: "comments", label: "Comments" }, { key: "shares", label: "Shares" }, { key: "engagement_rate", label: "Engagement" },
    ]);
    renderTable("trendsTable", trendRows, [
      { key: "keyword", label: "Keyword" }, { key: "platform", label: "Platform" }, { key: "trend_score", label: "Score" }, { key: "trend_category", label: "Category" },
    ]);
    if (dbCharts?.status_breakdown?.length) console.log("SQLite chart data", dbCharts);
  } catch (error) {
    setText("metricStrip", friendlyError(error));
  }
}

function renderCalendarLane(rows = []) {
  byId("calendarLane").innerHTML = rows.slice(0, 6).map((row) => `<article class="schedule-card"><strong>${row.platform || "Platform"}</strong><span>${[row.scheduled_date, row.scheduled_time].filter(Boolean).join(" ") || "Scheduled"}</span><p>${String(row.caption_preview || row.caption || "").slice(0, 115)}</p></article>`).join("");
}

async function loadCalendar() {
  injectCalendarWorkflow();
  try {
    let rows = [];
    const db = await api("/api/db/schedules").catch(() => null);
    if (db?.schedules) rows = db.schedules;
    if (!rows.length) {
      const legacy = await api("/api/scheduler").catch(() => ({ pending: [] }));
      rows = legacy.pending || [];
    }
    renderCalendarLane(rows);
    renderTable("calendarTable", rows, [
      { key: "post_id", label: "Post" }, { key: "platform", label: "Platform" }, { key: "scheduled_date", label: "Date" }, { key: "scheduled_time", label: "Time" }, { key: "post_status", label: "Status" }, { key: "caption", label: "Caption" },
    ]);
  } catch (error) {
    byId("calendarLane").innerHTML = `<article class="schedule-card"><strong>Error</strong><p>${friendlyError(error)}</p></article>`;
  }
}

function injectCalendarWorkflow() {
  const calendar = byId("calendar");
  if (!calendar || byId("dbWorkflowCard")) return;
  const card = document.createElement("article");
  card.className = "tool-card";
  card.id = "dbWorkflowCard";
  card.innerHTML = `<div class="card-head"><div><span>SQLite workflow</span><h3>Save, schedule, reschedule</h3></div><a class="cta small" href="/static/workflow_runner.html">Open runner</a></div><div class="grid-2"><label>Post ID<input id="dbPostId" type="number" value="1"></label><label>Date<input id="dbDate" type="date"></label></div><div class="grid-2"><label>Time<input id="dbTime" type="time" value="19:00"></label><label>Reason<input id="dbReason" value="Better engagement slot"></label></div><div class="inline-actions"><button class="cta small" id="dbScheduleBtn" type="button">Schedule</button><button class="ghost small" id="dbRescheduleBtn" type="button">Reschedule</button></div><pre id="dbWorkflowOutput">Ready. Save a post first, then schedule or reschedule it here.</pre>`;
  calendar.appendChild(card);
  byId("dbScheduleBtn").addEventListener("click", async () => {
    try {
      const result = await api("/api/db/schedule", { method: "POST", body: JSON.stringify({ post_id: Number(byId("dbPostId").value || 1), scheduled_date: byId("dbDate").value, scheduled_time: byId("dbTime").value, username: "editor_creator" }) });
      showResult("dbWorkflowOutput", result, "Post scheduled");
      loadCalendar();
    } catch (error) { setText("dbWorkflowOutput", friendlyError(error)); }
  });
  byId("dbRescheduleBtn").addEventListener("click", async () => {
    try {
      const result = await api("/api/db/reschedule", { method: "POST", body: JSON.stringify({ post_id: Number(byId("dbPostId").value || 1), new_date: byId("dbDate").value, new_time: byId("dbTime").value, username: "editor_creator", reason: byId("dbReason").value }) });
      showResult("dbWorkflowOutput", result, "Post rescheduled");
      loadCalendar();
    } catch (error) { setText("dbWorkflowOutput", friendlyError(error)); }
  });
}

async function loadCompetitors() {
  try { setText("competitorOutput", await api("/api/competitors")); }
  catch (error) { setText("competitorOutput", friendlyError(error)); }
}

function renderIntegrationStatus(data = {}) {
  const rows = [
    ["Telegram", data.telegram?.configured && data.telegram?.status === "ok", data.telegram?.can_send_messages ? "ready" : "needs chat id"],
    ["LinkedIn", data.linkedin?.access_token === "configured" || data.linkedin?.live_ready, data.linkedin?.live_ready ? "ready" : "needs author urn"],
    ["X", data.x?.bearer_token === "configured" || data.x?.live_ready, data.x?.live_ready ? "ready" : "read/status only"],
  ];
  byId("integrationStatus").innerHTML = rows.map(([name, ok, note]) => `<span class="integration-pill ${ok ? "ok" : "warn"}"><strong>${name}</strong><span>${note}</span></span>`).join("");
}

async function loadIntegrations() {
  try { renderIntegrationStatus(await api("/api/integrations")); }
  catch (error) { byId("integrationStatus").innerHTML = `<span class="integration-pill warn">${friendlyError(error)}</span>`; }
}

function injectAdminWorkflow() {
  const adminGrid = document.querySelector("#admin .card-grid");
  if (!adminGrid || byId("dbReviewCard")) return;
  const review = document.createElement("article");
  review.className = "tool-card wide";
  review.id = "dbReviewCard";
  review.innerHTML = `<div class="card-head"><div><span>Feedback loop</span><h3>Store review for post improvement</h3></div><button class="ghost small" id="dbLoadReviewsBtn" type="button">Load reviews</button></div><div class="grid-2"><label>Post ID, optional<input id="reviewPostId" type="number" value="1"></label><label>Rating 1-5<input id="reviewRating" type="number" min="1" max="5" value="5"></label></div><label>Review notes<input id="reviewNotes" value="Good hook and CTA"></label><div class="inline-actions"><button class="cta small" id="dbReviewBtn" type="button">Save feedback</button><a class="ghost small" href="/static/workflow_runner.html">Open workflow runner</a></div><pre id="dbReviewOutput">Ready. Feedback will be stored in SQLite.</pre>`;
  adminGrid.appendChild(review);
  byId("dbReviewBtn").addEventListener("click", async () => {
    try {
      const result = await api("/api/db/review", { method: "POST", body: JSON.stringify({ post_id: Number(byId("reviewPostId").value || 0) || null, platform: platformForApi(byId("publishPlatform").value || "Instagram"), caption: byId("publishCaption").value || "AI automation test caption #AI", rating: Number(byId("reviewRating").value || 5), notes: byId("reviewNotes").value, created_by: "editor_creator" }) });
      showResult("dbReviewOutput", result, "Feedback saved");
    } catch (error) { setText("dbReviewOutput", friendlyError(error)); }
  });
  byId("dbLoadReviewsBtn").addEventListener("click", async () => {
    try { showResult("dbReviewOutput", await api("/api/db/reviews"), "Reviews loaded"); }
    catch (error) { setText("dbReviewOutput", friendlyError(error)); }
  });
}

function wireEvents() {
  document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => activateTab(b.dataset.tab)));
  document.querySelectorAll("[data-jump]").forEach((b) => b.addEventListener("click", () => activateTab(b.dataset.jump)));
  byId("loginOpen")?.addEventListener("click", openLogin);
  byId("loginClose")?.addEventListener("click", closeLogin);
  byId("loginModal")?.addEventListener("click", (e) => { if (e.target.id === "loginModal") closeLogin(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLogin(); });
  byId("topLoginForm")?.addEventListener("submit", (e) => handleLogin(e, "topLoginOutput"));
  byId("loginForm")?.addEventListener("submit", (e) => handleLogin(e, "loginOutput"));
  byId("loadBriefButton")?.addEventListener("click", loadBrief);
  byId("briefPlatform")?.addEventListener("change", loadBrief);
  byId("useBriefButton")?.addEventListener("click", async () => { if (!currentBrief) await loadBrief(); const f = byId("generateForm"); if (currentBrief && f) { f.elements.topic.value = currentBrief.recommended_topic || currentBrief.topic_seed || f.elements.topic.value; f.elements.platform.value = currentBrief.platform === "Twitter" ? "X" : currentBrief.platform; } });
  byId("copyToPublisherButton")?.addEventListener("click", () => { const caption = generatedCaption || byId("captionOutput").textContent; if (caption && !caption.includes("Ready")) { byId("publishCaption").value = caption; byId("publishPlatform").value = byId("generateForm").elements.platform.value; activateTab("admin"); } });
  byId("reviewPackageButton")?.addEventListener("click", () => { if (currentPackage) applyPostPackage(currentPackage); activateTab("generate"); });
  byId("publishPackageButton")?.addEventListener("click", () => { if (currentPackage) applyPostPackage(currentPackage); activateTab("admin"); });
  byId("refreshCalendar")?.addEventListener("click", loadCalendar);

  byId("rawPostForm")?.addEventListener("submit", async (e) => {
    e.preventDefault(); setText("rawPostOutput", "Building post package from raw data...");
    try { const p = formJson(e.currentTarget); p.platform = platformForApi(p.platform); applyPostPackage(await api("/api/full-pipeline", { method: "POST", body: JSON.stringify(p) })); }
    catch (error) { setText("rawPostOutput", friendlyError(error)); }
  });

  byId("generateForm")?.addEventListener("submit", async (e) => {
    e.preventDefault(); const p = formJson(e.currentTarget); p.platform = platformForApi(p.platform); setText("captionOutput", "Generating content package...");
    try {
      const caption = await api("/api/generate-caption", { method: "POST", body: JSON.stringify(p) });
      generatedCaption = caption.caption || caption.captions?.[0]?.caption || "";
      setText("captionOutput", generatedCaption || caption);
      const [hashtags, moderation, plagiarism, imagePrompt] = await Promise.all([
        api("/api/hashtags", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: p.platform }) }),
        api("/api/moderate", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: p.platform }) }),
        api("/api/plagiarism", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: p.platform }) }),
        api("/api/image-prompt", { method: "POST", body: JSON.stringify(p) }),
      ]);
      setText("hashtagOutput", extractHashtags(hashtags)); setText("safetyOutput", { moderation, plagiarism }); setText("imagePromptOutput", imagePrompt);
    } catch (error) { setText("captionOutput", friendlyError(error)); }
  });

  byId("predictForm")?.addEventListener("submit", async (e) => {
    e.preventDefault(); const p = formJson(e.currentTarget); p.platform = platformForApi(p.platform); p.hour_posted = Number(p.hour_posted); p.hashtags = (p.caption.match(/#\w+/g) || []).join(" ") || "#AI #SocialMedia"; p.sentiment_score = 0.7; p.has_image = 1;
    try { const prediction = await api("/api/predict-engagement", { method: "POST", body: JSON.stringify(p) }); updateGauge(extractPredictionScore(prediction)); setText("predictionOutput", prediction); }
    catch (error) { setText("predictionOutput", friendlyError(error)); }
  });

  byId("publishButton")?.addEventListener("click", async () => {
    try { showResult("publishOutput", await api("/api/publish", { method: "POST", body: JSON.stringify({ platform: platformForApi(byId("publishPlatform").value), caption: byId("publishCaption").value, media_url: byId("publishMediaUrl").value || null }) }), "Dry-run successful"); }
    catch (error) { setText("publishOutput", friendlyError(error)); }
  });
  byId("telegramButton")?.addEventListener("click", async () => {
    try { showResult("publishOutput", await api("/api/telegram", { method: "POST", body: JSON.stringify({ message: byId("publishCaption").value }) }), "Telegram request sent"); }
    catch (error) { setText("publishOutput", friendlyError(error)); }
  });
}

wireEvents();
checkHealth();
loadDashboard();
injectCalendarWorkflow();
injectAdminWorkflow();
