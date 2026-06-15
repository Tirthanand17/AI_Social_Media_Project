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

if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}
window.scrollTo({ top: 0, behavior: "auto" });

const setText = (id, value) => {
  document.getElementById(id).textContent =
    typeof value === "string" ? value : pretty(value);
};

const formJson = (form) => Object.fromEntries(new FormData(form).entries());
let currentBrief = null;
let generatedCaption = "";
let currentUser = null;
let currentPackage = null;

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".workspace").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(button.dataset.tab).classList.add("active");
    window.scrollTo({ top: 0, behavior: "auto" });
    if (button.dataset.tab === "dashboard") loadDashboard();
    if (button.dataset.tab === "analytics") loadAnalytics();
    if (button.dataset.tab === "calendar") loadCalendar();
    if (button.dataset.tab === "admin") {
      loadCompetitors();
      loadIntegrations();
    }
  });
});

document.querySelectorAll("[data-jump]").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.jump;
    const tab = document.querySelector(`.tab[data-tab="${target}"]`);
    if (tab) tab.click();
    document.getElementById(target)?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

async function checkHealth() {
  try {
    const data = await api("/api/health");
    const status = document.getElementById("apiStatus");
    status.textContent = data.status === "running" ? "Online" : "Issue";
    status.classList.add("ok");
  } catch (error) {
    document.getElementById("apiStatus").textContent = "Offline";
  }
}

function setUser(loginResult) {
  if (!loginResult?.success) return;
  currentUser = loginResult.user;
  document.getElementById("userPill").textContent = `${currentUser.role}: ${currentUser.username}`;
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
  document.getElementById("loginModal").classList.add("open");
  document.getElementById("loginModal").setAttribute("aria-hidden", "false");
}

function closeLogin() {
  document.getElementById("loginModal").classList.remove("open");
  document.getElementById("loginModal").setAttribute("aria-hidden", "true");
}

document.getElementById("loginOpen").addEventListener("click", openLogin);
document.getElementById("loginClose").addEventListener("click", closeLogin);

document.getElementById("topLoginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const result = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    setText("topLoginOutput", loginSummary(result));
    setUser(result);
    if (result.success) closeLogin();
  } catch (error) {
    setText("topLoginOutput", error.message);
  }
});

async function loadDashboard() {
  try {
    const [overview, integrations] = await Promise.all([
      api("/api/data/overview"),
      api("/api/integrations/status"),
    ]);
    document.getElementById("datasetCount").textContent = overview.datasets?.length ?? "--";
    document.getElementById("postingMode").textContent = integrations.posting_mode || "dry_run";
    renderPlatformReadiness(integrations);
  } catch (error) {
    document.getElementById("datasetCount").textContent = "--";
    document.getElementById("postingMode").textContent = "offline";
    document.getElementById("platformReadiness").innerHTML =
      `<article class="platform-card warn"><strong>API</strong><span>${error.message}</span></article>`;
  }
}

function renderPlatformReadiness(data) {
  const platforms = [
    ["Instagram", true, "Dry-run ready. Live requires Meta page/account permissions."],
    ["Facebook", true, "Dry-run ready. Live requires Meta page token and page permissions."],
    ["X", data.x?.bearer_token === "configured", data.x?.live_ready ? "Live ready" : "Read/status configured; write OAuth still needed."],
    ["LinkedIn", data.linkedin?.access_token === "configured", data.linkedin?.live_ready ? "Live ready" : "Token stored; author URN still needed."],
  ];
  document.getElementById("platformReadiness").innerHTML = platforms
    .map(([name, ok, note]) => `<article class="platform-card ${ok ? "ok" : "warn"}"><strong>${name}</strong><span>${note}</span></article>`)
    .join("");
}

async function loadBrief() {
  try {
    const platform = document.getElementById("briefPlatform").value;
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

document.getElementById("loadBriefButton").addEventListener("click", loadBrief);
document.getElementById("briefPlatform").addEventListener("change", loadBrief);

document.getElementById("useBriefButton").addEventListener("click", async () => {
  if (!currentBrief) await loadBrief();
  const form = document.getElementById("generateForm");
  form.elements.topic.value = currentBrief.recommended_topic || currentBrief.topic_seed || form.elements.topic.value;
  form.elements.platform.value = currentBrief.platform === "Twitter" ? "X" : currentBrief.platform;
});

document.getElementById("copyToPublisherButton").addEventListener("click", () => {
  const caption = generatedCaption || document.getElementById("captionOutput").textContent;
  if (caption && !caption.includes("Ready")) {
    document.getElementById("publishCaption").value = caption;
    document.getElementById("publishPlatform").value = document.getElementById("generateForm").elements.platform.value;
    document.querySelector('.tab[data-tab="admin"]').click();
  }
});

function applyPostPackage(data) {
  currentPackage = data;
  generatedCaption = data.caption || "";
  const bestTime = data.best_time
    ? `${data.best_time.day_of_week || ""} ${data.best_time.hour_posted ?? ""}:00`.trim()
    : "Not available";
  setText("rawPostOutput", {
    platform: data.platform,
    caption: data.caption,
    hashtags: data.hashtags?.hashtag_string,
    best_time: bestTime,
    predicted_score: data.engagement_prediction?.predicted_engagement_score,
    publish_status: data.publish_preview?.status,
  });
  setText("captionOutput", data.caption || "Ready.");
  setText("hashtagOutput", data.hashtags?.hashtag_string || "Ready.");
  setText("safetyOutput", { moderation: data.moderation, plagiarism: data.plagiarism });
  setText("imagePromptOutput", data.image_prompt || "Ready.");
  if (data.engagement_prediction?.predicted_engagement_score !== undefined) {
    updateGauge(data.engagement_prediction.predicted_engagement_score);
    setText("predictionOutput", data.engagement_prediction);
  }
  document.getElementById("publishCaption").value = data.caption || "";
  document.getElementById("publishPlatform").value = data.platform || "Instagram";
}

document.getElementById("rawPostForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setText("rawPostOutput", "Building post package from raw data...");
  try {
    const data = await api("/api/content/raw-to-post", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    applyPostPackage(data);
  } catch (error) {
    setText("rawPostOutput", error.message);
  }
});

document.getElementById("reviewPackageButton").addEventListener("click", () => {
  if (currentPackage) applyPostPackage(currentPackage);
  document.querySelector('.tab[data-tab="generate"]').click();
});

document.getElementById("publishPackageButton").addEventListener("click", () => {
  if (currentPackage) applyPostPackage(currentPackage);
  document.querySelector('.tab[data-tab="admin"]').click();
});

function updateGauge(score) {
  const gauge = document.getElementById("predictionGauge");
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
  const degrees = Math.round((safeScore / 100) * 360);
  gauge.style.background = `radial-gradient(circle at center, #ffffff 0 56%, transparent 57%), conic-gradient(var(--red) ${degrees}deg, #edf2f4 ${degrees}deg)`;
  gauge.querySelector("span").textContent = Math.round(safeScore);
}

document.getElementById("generateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formJson(event.currentTarget);
  setText("captionOutput", "Generating with connected AI provider...");
  try {
    const caption = await api("/api/content/generate-caption", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    generatedCaption = caption.caption;
    setText("captionOutput", caption.caption);
    const [hashtags, moderation, plagiarism, imagePrompt] = await Promise.all([
      api("/api/content/hashtags", { method: "POST", body: JSON.stringify({ text: caption.caption, platform: payload.platform }) }),
      api("/api/content/moderate", { method: "POST", body: JSON.stringify({ text: caption.caption, platform: payload.platform }) }),
      api("/api/content/plagiarism", { method: "POST", body: JSON.stringify({ text: caption.caption, platform: payload.platform }) }),
      api("/api/content/image-prompt", { method: "POST", body: JSON.stringify(payload) }),
    ]);
    setText("hashtagOutput", hashtags.hashtag_string);
    setText("safetyOutput", { moderation, plagiarism });
    setText("imagePromptOutput", imagePrompt);
  } catch (error) {
    setText("captionOutput", error.message);
  }
});

document.getElementById("predictForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formJson(event.currentTarget);
  payload.hour_posted = Number(payload.hour_posted);
  payload.hashtags = (payload.caption.match(/#\w+/g) || []).join(" ");
  payload.sentiment_score = 0.7;
  payload.has_image = 1;
  setText("predictionOutput", "Scoring content performance...");
  updateGauge(0);
  try {
    const prediction = await api("/api/ml/predict-engagement", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    updateGauge(prediction.predicted_engagement_score);
    setText("predictionOutput", prediction);
  } catch (error) {
    setText("predictionOutput", error.message);
  }
});

function renderTable(id, rows, columns) {
  const table = document.getElementById(id);
  if (!rows || rows.length === 0) {
    table.innerHTML = "<tbody><tr><td>No data</td></tr></tbody>";
    return;
  }
  const header = columns.map((column) => `<th>${column.label}</th>`).join("");
  const body = rows
    .map((row) =>
      `<tr>${columns
        .map((column) => `<td>${String(row[column.key] ?? "")}</td>`)
        .join("")}</tr>`
    )
    .join("");
  table.innerHTML = `<thead><tr>${header}</tr></thead><tbody>${body}</tbody>`;
}

function renderMetrics(analytics) {
  document.getElementById("metricStrip").innerHTML = [
    ["Posts", analytics.records],
    ["Reach", analytics.total_reach],
    ["Likes", analytics.total_likes],
    ["Avg ER", analytics.avg_engagement_rate],
  ]
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong><em></em></div>`)
    .join("");
}

function renderBars(posts) {
  const max = Math.max(...posts.map((post) => Number(post.engagement_rate) || 0), 1);
  document.getElementById("engagementBars").innerHTML = posts
    .slice(0, 14)
    .map((post) => {
      const height = Math.max(18, Math.round(((Number(post.engagement_rate) || 0) / max) * 100));
      return `<span class="bar" title="${post.platform} ${post.engagement_rate}" style="height:${height}%"></span>`;
    })
    .join("");
}

function renderTrendCloud(trends) {
  document.getElementById("trendCloud").innerHTML = trends
    .slice(0, 16)
    .map((item) => `<span class="trend-chip" style="font-size:${12 + Math.min(12, item.trend_score / 10)}px">${item.keyword}</span>`)
    .join("");
}

async function loadAnalytics() {
  const [analytics, trends] = await Promise.all([
    api("/api/analytics/summary"),
    api("/api/trends/analyze"),
  ]);
  renderMetrics(analytics);
  renderBars(analytics.top_posts);
  renderTrendCloud(trends.trending_keywords || []);
  renderTable("topPostsTable", analytics.top_posts, [
    { key: "post_id", label: "Post" },
    { key: "platform", label: "Platform" },
    { key: "likes", label: "Likes" },
    { key: "comments", label: "Comments" },
    { key: "shares", label: "Shares" },
    { key: "engagement_rate", label: "Engagement" },
  ]);
  renderTable("trendsTable", trends.trending_keywords, [
    { key: "keyword", label: "Keyword" },
    { key: "platform", label: "Platform" },
    { key: "trend_score", label: "Score" },
    { key: "trend_category", label: "Category" },
  ]);
}

function renderCalendarLane(rows) {
  document.getElementById("calendarLane").innerHTML = (rows || [])
    .slice(0, 6)
    .map(
      (row) => `<article class="schedule-card">
        <strong>${row.platform || "Platform"}</strong>
        <span>${[row.scheduled_date, row.scheduled_time].filter(Boolean).join(" ") || "Scheduled"}</span>
        <p>${String(row.caption_preview || row.caption || "").slice(0, 96)}</p>
      </article>`
    )
    .join("");
}

async function loadCalendar() {
  const data = await api("/api/scheduler/summary");
  renderCalendarLane(data.pending);
  renderTable("calendarTable", data.pending, [
    { key: "post_id", label: "Post" },
    { key: "platform", label: "Platform" },
    { key: "scheduled_date", label: "Date" },
    { key: "scheduled_time", label: "Time" },
    { key: "status", label: "Status" },
    { key: "caption_preview", label: "Caption" },
  ]);
}

document.getElementById("refreshCalendar").addEventListener("click", loadCalendar);

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const login = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    setText("loginOutput", loginSummary(login));
    setUser(login);
  } catch (error) {
    setText("loginOutput", error.message);
  }
});

async function loadCompetitors() {
  try {
    const competitors = await api("/api/competitors/summary");
    setText("competitorOutput", competitors);
  } catch (error) {
    setText("competitorOutput", error.message);
  }
}

function renderIntegrationStatus(data) {
  const rows = [
    ["Telegram", data.telegram?.configured && data.telegram?.status === "ok", data.telegram?.can_send_messages ? "ready" : "needs chat id"],
    ["LinkedIn", data.linkedin?.access_token === "configured", data.linkedin?.live_ready ? "ready" : "needs author urn"],
    ["X", data.x?.bearer_token === "configured", data.x?.live_ready ? "ready" : "read/status only"],
  ];
  document.getElementById("integrationStatus").innerHTML = rows
    .map(([name, ok, note]) => `<span class="integration-pill ${ok ? "ok" : "warn"}">${name}: ${note}</span>`)
    .join("");
}

async function loadIntegrations() {
  try {
    renderIntegrationStatus(await api("/api/integrations/status"));
  } catch (error) {
    document.getElementById("integrationStatus").innerHTML = `<span class="integration-pill warn">${error.message}</span>`;
  }
}

document.getElementById("publishButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/publisher/dry-run", {
      method: "POST",
      body: JSON.stringify({
        platform: document.getElementById("publishPlatform").value,
        caption: document.getElementById("publishCaption").value,
      }),
    });
    setText("publishOutput", result);
  } catch (error) {
    setText("publishOutput", error.message);
  }
});

document.getElementById("telegramButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/integrations/telegram/send", {
      method: "POST",
      body: JSON.stringify({ message: document.getElementById("publishCaption").value }),
    });
    setText("publishOutput", result);
  } catch (error) {
    setText("publishOutput", error.message);
  }
});

checkHealth();
loadDashboard();
