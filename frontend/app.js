const api = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
};

const pretty = (value) => JSON.stringify(value, null, 2);
const byId = (id) => document.getElementById(id);
const setText = (id, value) => {
  const element = byId(id);
  if (!element) return;
  element.textContent = typeof value === "string" ? value : pretty(value);
};
const formJson = (form) => Object.fromEntries(new FormData(form).entries());
const platformForApi = (value) => (value === "X" ? "Twitter" : value);

let currentBrief = null;
let generatedCaption = "";
let currentUser = null;
let currentPackage = null;

if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}

function activateTab(target) {
  document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item.dataset.tab === target));
  document.querySelectorAll(".workspace").forEach((item) => item.classList.toggle("active", item.id === target));
  window.scrollTo({ top: 0, behavior: "auto" });
  if (target === "dashboard") loadDashboard();
  if (target === "analytics") loadAnalytics();
  if (target === "calendar") loadCalendar();
  if (target === "admin") {
    loadCompetitors();
    loadIntegrations();
  }
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.tab));
});

document.querySelectorAll("[data-jump]").forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.jump));
});

async function checkHealth() {
  try {
    const [health, config] = await Promise.all([api("/api/health"), api("/api/config")]);
    const status = byId("apiStatus");
    status.textContent = health.status === "ok" ? "Online" : "Issue";
    status.classList.toggle("ok", health.status === "ok");
    byId("postingModeBadge").textContent = config.posting_mode || health.posting_mode || "dry_run";
    byId("postingMode").textContent = config.posting_mode || health.posting_mode || "dry_run";
  } catch (error) {
    byId("apiStatus").textContent = "Offline";
    setText("rawPostOutput", `API is not reachable: ${error.message}`);
  }
}

function setUser(loginResult) {
  if (!loginResult?.success) return;
  currentUser = loginResult.user;
  byId("userPill").textContent = `${currentUser.role}: ${currentUser.username}`;
}

function loginSummary(result) {
  if (!result?.success) return result;
  return {
    success: true,
    role: result.user?.role,
    username: result.user?.username,
    brand: result.user?.brand_name,
  };
}

function openLogin() {
  byId("loginModal").classList.add("open");
  byId("loginModal").setAttribute("aria-hidden", "false");
}

function closeLogin() {
  byId("loginModal").classList.remove("open");
  byId("loginModal").setAttribute("aria-hidden", "true");
}

byId("loginOpen").addEventListener("click", openLogin);
byId("loginClose").addEventListener("click", closeLogin);
byId("loginModal").addEventListener("click", (event) => {
  if (event.target.id === "loginModal") closeLogin();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeLogin();
});

async function handleLogin(event, outputId) {
  event.preventDefault();
  try {
    const result = await api("/api/login", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    setText(outputId, loginSummary(result));
    setUser(result);
    if (result.success) closeLogin();
  } catch (error) {
    setText(outputId, error.message);
  }
}

byId("topLoginForm").addEventListener("submit", (event) => handleLogin(event, "topLoginOutput"));
byId("loginForm").addEventListener("submit", (event) => handleLogin(event, "loginOutput"));

async function loadDashboard() {
  try {
    const [overview, integrations] = await Promise.all([api("/api/dataset-overview"), api("/api/integrations")]);
    const datasets = overview.datasets || overview || [];
    byId("datasetCount").textContent = Array.isArray(datasets) ? datasets.length : overview.total_datasets || "--";
    byId("postingMode").textContent = integrations.posting_mode || byId("postingModeBadge").textContent || "dry_run";
    byId("postingModeBadge").textContent = integrations.posting_mode || "dry_run";
    renderPlatformReadiness(integrations);
  } catch (error) {
    byId("datasetCount").textContent = "--";
    byId("postingMode").textContent = "offline";
    byId("platformReadiness").innerHTML = `<article class="platform-card warn"><strong>API</strong><span>${error.message}</span></article>`;
  }
}

function renderPlatformReadiness(data = {}) {
  const linkedinReady = data.linkedin?.live_ready || data.linkedin?.access_token === "configured";
  const xReady = data.x?.live_ready || data.x?.bearer_token === "configured";
  const platforms = [
    ["Instagram", true, "Dry-run ready. Live posting requires Meta permissions."],
    ["Facebook", true, "Dry-run ready. Live posting requires page token."],
    ["X", xReady, data.x?.live_ready ? "Live ready" : "Dry-run ready; write OAuth required for live posts."],
    ["LinkedIn", linkedinReady, data.linkedin?.live_ready ? "Live ready" : "Token/author setup needed for live publishing."],
  ];
  byId("platformReadiness").innerHTML = platforms
    .map(([name, ok, note]) => `<article class="platform-card ${ok ? "ok" : "warn"}"><strong>${name}</strong><span>${note}</span></article>`)
    .join("");
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
    setText("briefOutput", error.message);
  }
}

byId("loadBriefButton").addEventListener("click", loadBrief);
byId("briefPlatform").addEventListener("change", loadBrief);

byId("useBriefButton").addEventListener("click", async () => {
  if (!currentBrief) await loadBrief();
  if (!currentBrief) return;
  const form = byId("generateForm");
  form.elements.topic.value = currentBrief.recommended_topic || currentBrief.topic_seed || form.elements.topic.value;
  form.elements.platform.value = currentBrief.platform === "Twitter" ? "X" : currentBrief.platform;
});

byId("copyToPublisherButton").addEventListener("click", () => {
  const caption = generatedCaption || byId("captionOutput").textContent;
  if (caption && !caption.includes("Ready")) {
    byId("publishCaption").value = caption;
    byId("publishPlatform").value = byId("generateForm").elements.platform.value;
    activateTab("admin");
  }
});

function extractHashtags(data) {
  if (!data) return "Ready.";
  return data.hashtag_string || data.hashtags?.join(" ") || data.recommended_hashtags?.join(" ") || pretty(data);
}

function extractPredictionScore(prediction) {
  return (
    prediction?.predicted_engagement_score ??
    prediction?.engagement_score ??
    prediction?.score ??
    prediction?.prediction ??
    0
  );
}

function applyPostPackage(data) {
  currentPackage = data;
  generatedCaption = data.caption || "";
  const bestTime = data.best_time
    ? `${data.best_time.day_of_week || data.best_time.day || ""} ${data.best_time.hour_posted ?? data.best_time.hour ?? ""}:00`.trim()
    : "Not available";
  setText("rawPostOutput", {
    platform: data.platform,
    campaign_goal: data.campaign_goal,
    caption: data.caption,
    hashtags: extractHashtags(data.hashtags),
    best_time: bestTime,
    predicted_score: extractPredictionScore(data.engagement_prediction),
    publish_status: data.publish_preview?.status || data.publish_preview?.message || "dry_run preview",
  });
  setText("captionOutput", data.caption || "Ready.");
  setText("hashtagOutput", extractHashtags(data.hashtags));
  setText("safetyOutput", { moderation: data.moderation, plagiarism: data.plagiarism });
  setText("imagePromptOutput", data.image_prompt || "Ready.");
  updateGauge(extractPredictionScore(data.engagement_prediction));
  setText("predictionOutput", data.engagement_prediction || "Ready.");
  byId("publishCaption").value = data.caption || "";
  byId("publishPlatform").value = data.platform === "Twitter" ? "X" : data.platform || "Instagram";
}

byId("rawPostForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setText("rawPostOutput", "Building post package from raw data...");
  try {
    const payload = formJson(event.currentTarget);
    payload.platform = platformForApi(payload.platform);
    const data = await api("/api/full-pipeline", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    applyPostPackage(data);
  } catch (error) {
    setText("rawPostOutput", error.message);
  }
});

byId("reviewPackageButton").addEventListener("click", () => {
  if (currentPackage) applyPostPackage(currentPackage);
  activateTab("generate");
});

byId("publishPackageButton").addEventListener("click", () => {
  if (currentPackage) applyPostPackage(currentPackage);
  activateTab("admin");
});

function updateGauge(score) {
  const gauge = byId("predictionGauge");
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
  const degrees = Math.round((safeScore / 100) * 360);
  gauge.style.background = `radial-gradient(circle at center, #ffffff 0 58%, transparent 59%), conic-gradient(var(--primary) ${degrees}deg, #edf2f7 ${degrees}deg)`;
  gauge.querySelector("span").textContent = safeScore ? Math.round(safeScore) : "--";
}

byId("generateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formJson(event.currentTarget);
  payload.platform = platformForApi(payload.platform);
  setText("captionOutput", "Generating content package...");
  try {
    const caption = await api("/api/generate-caption", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    generatedCaption = caption.caption || caption.captions?.[0]?.caption || "";
    setText("captionOutput", generatedCaption || caption);
    const [hashtags, moderation, plagiarism, imagePrompt] = await Promise.all([
      api("/api/hashtags", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: payload.platform }) }),
      api("/api/moderate", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: payload.platform }) }),
      api("/api/plagiarism", { method: "POST", body: JSON.stringify({ text: generatedCaption, platform: payload.platform }) }),
      api("/api/image-prompt", { method: "POST", body: JSON.stringify(payload) }),
    ]);
    setText("hashtagOutput", extractHashtags(hashtags));
    setText("safetyOutput", { moderation, plagiarism });
    setText("imagePromptOutput", imagePrompt);
  } catch (error) {
    setText("captionOutput", error.message);
  }
});

byId("predictForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formJson(event.currentTarget);
  payload.platform = platformForApi(payload.platform);
  payload.hour_posted = Number(payload.hour_posted);
  payload.hashtags = (payload.caption.match(/#\w+/g) || []).join(" ") || "#AI #SocialMedia";
  payload.sentiment_score = 0.7;
  payload.has_image = 1;
  setText("predictionOutput", "Scoring content performance...");
  updateGauge(0);
  try {
    const prediction = await api("/api/predict-engagement", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    updateGauge(extractPredictionScore(prediction));
    setText("predictionOutput", prediction);
  } catch (error) {
    setText("predictionOutput", error.message);
  }
});

function renderTable(id, rows, columns) {
  const table = byId(id);
  if (!rows || rows.length === 0) {
    table.innerHTML = "<tbody><tr><td>No data available</td></tr></tbody>";
    return;
  }
  const header = columns.map((column) => `<th>${column.label}</th>`).join("");
  const body = rows
    .map((row) => `<tr>${columns.map((column) => `<td>${String(row[column.key] ?? "")}</td>`).join("")}</tr>`)
    .join("");
  table.innerHTML = `<thead><tr>${header}</tr></thead><tbody>${body}</tbody>`;
}

function renderMetrics(analytics) {
  byId("metricStrip").innerHTML = [
    ["Posts", analytics.records],
    ["Reach", analytics.total_reach],
    ["Likes", analytics.total_likes],
    ["Avg ER", analytics.avg_engagement_rate],
  ]
    .map(([label, value]) => `<article class="metric"><span>${label}</span><strong>${value ?? "--"}</strong><em>From analytics dataset</em></article>`)
    .join("");
}

function renderBars(posts = []) {
  const max = Math.max(...posts.map((post) => Number(post.engagement_rate) || 0), 1);
  byId("engagementBars").innerHTML = posts
    .slice(0, 14)
    .map((post) => {
      const height = Math.max(18, Math.round(((Number(post.engagement_rate) || 0) / max) * 100));
      return `<span class="bar" title="${post.platform || "post"}: ${post.engagement_rate}" style="height:${height}%"></span>`;
    })
    .join("");
}

function renderTrendCloud(trends = []) {
  byId("trendCloud").innerHTML = trends
    .slice(0, 18)
    .map((item) => `<span class="trend-chip" style="font-size:${12 + Math.min(12, Number(item.trend_score || 0) / 10)}px">${item.keyword}</span>`)
    .join("");
}

async function loadAnalytics() {
  try {
    const [analytics, trends] = await Promise.all([api("/api/analytics"), api("/api/trends")]);
    renderMetrics(analytics);
    renderBars(analytics.top_posts || []);
    const trendRows = trends.trending_keywords || [];
    renderTrendCloud(trendRows);
    renderTable("topPostsTable", analytics.top_posts || [], [
      { key: "post_id", label: "Post" },
      { key: "platform", label: "Platform" },
      { key: "likes", label: "Likes" },
      { key: "comments", label: "Comments" },
      { key: "shares", label: "Shares" },
      { key: "engagement_rate", label: "Engagement" },
    ]);
    renderTable("trendsTable", trendRows, [
      { key: "keyword", label: "Keyword" },
      { key: "platform", label: "Platform" },
      { key: "trend_score", label: "Score" },
      { key: "trend_category", label: "Category" },
    ]);
  } catch (error) {
    setText("metricStrip", error.message);
  }
}

function renderCalendarLane(rows = []) {
  byId("calendarLane").innerHTML = rows
    .slice(0, 6)
    .map(
      (row) => `<article class="schedule-card">
        <strong>${row.platform || "Platform"}</strong>
        <span>${[row.scheduled_date, row.scheduled_time].filter(Boolean).join(" ") || "Scheduled"}</span>
        <p>${String(row.caption_preview || row.caption || "").slice(0, 115)}</p>
      </article>`
    )
    .join("");
}

async function loadCalendar() {
  try {
    const data = await api("/api/scheduler");
    const rows = data.pending || [];
    renderCalendarLane(rows);
    renderTable("calendarTable", rows, [
      { key: "post_id", label: "Post" },
      { key: "platform", label: "Platform" },
      { key: "scheduled_date", label: "Date" },
      { key: "scheduled_time", label: "Time" },
      { key: "status", label: "Status" },
      { key: "caption_preview", label: "Caption" },
    ]);
  } catch (error) {
    byId("calendarLane").innerHTML = `<article class="schedule-card"><strong>Error</strong><p>${error.message}</p></article>`;
  }
}

byId("refreshCalendar").addEventListener("click", loadCalendar);

async function loadCompetitors() {
  try {
    const competitors = await api("/api/competitors");
    setText("competitorOutput", competitors);
  } catch (error) {
    setText("competitorOutput", error.message);
  }
}

function renderIntegrationStatus(data = {}) {
  const rows = [
    ["Telegram", data.telegram?.configured && data.telegram?.status === "ok", data.telegram?.can_send_messages ? "ready" : "needs chat id"],
    ["LinkedIn", data.linkedin?.access_token === "configured" || data.linkedin?.live_ready, data.linkedin?.live_ready ? "ready" : "needs author urn"],
    ["X", data.x?.bearer_token === "configured" || data.x?.live_ready, data.x?.live_ready ? "ready" : "read/status only"],
  ];
  byId("integrationStatus").innerHTML = rows
    .map(([name, ok, note]) => `<span class="integration-pill ${ok ? "ok" : "warn"}"><strong>${name}</strong><span>${note}</span></span>`)
    .join("");
}

async function loadIntegrations() {
  try {
    const data = await api("/api/integrations");
    renderIntegrationStatus(data);
  } catch (error) {
    byId("integrationStatus").innerHTML = `<span class="integration-pill warn">${error.message}</span>`;
  }
}

byId("publishButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/publish", {
      method: "POST",
      body: JSON.stringify({
        platform: platformForApi(byId("publishPlatform").value),
        caption: byId("publishCaption").value,
        media_url: byId("publishMediaUrl").value || null,
      }),
    });
    setText("publishOutput", result);
  } catch (error) {
    setText("publishOutput", error.message);
  }
});

byId("telegramButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/telegram", {
      method: "POST",
      body: JSON.stringify({ message: byId("publishCaption").value }),
    });
    setText("publishOutput", result);
  } catch (error) {
    setText("publishOutput", error.message);
  }
});

checkHealth();
loadDashboard();
