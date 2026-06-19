const $ = (id) => document.getElementById(id);
const show = (id, value) => { const el = $(id); if (el) el.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2); };
const body = (obj) => JSON.stringify(obj);
const platformName = (x) => x || "LinkedIn";

let latestCaption = "";
let latestPostId = null;

async function api(url, options = {}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { message: text }; }
  if (!res.ok) throw new Error(data.message || `${res.status} ${res.statusText}`);
  return data;
}

function message(error) {
  const m = String(error?.message || error);
  if (m.includes("404")) return "This backend route is missing. Run api.live_main:app from the latest GitHub clone.";
  if (m.toLowerCase().includes("failed to fetch")) return "Backend is not running. Start uvicorn and open http://127.0.0.1:8010/app";
  if (m.toLowerCase().includes("token") || m.toLowerCase().includes("credential")) return "Publishing credential missing. Add it in local/deployment environment settings.";
  return m;
}

function toast(text) {
  let t = $("toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "toast";
    t.style.cssText = "position:fixed;left:50%;bottom:70px;transform:translateX(-50%);z-index:9999;background:#1a1200;color:#ffe082;padding:12px 18px;border-radius:999px;font:800 13px Segoe UI,Arial;box-shadow:0 10px 25px rgba(0,0,0,.25)";
    document.body.appendChild(t);
  }
  t.textContent = text;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.remove(), 3000);
}

function switchTab(tab) {
  document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll(".workspace").forEach(s => s.classList.toggle("active", s.id === tab));
  if (tab === "analytics") loadAnalytics();
  if (tab === "calendar") loadSchedules();
  if (tab === "admin") loadPublisherInfo();
}

function scoreAdvice(result) {
  const score = Number(result?.predicted_engagement_score || result?.score || 0);
  const best = result?.best_time || {};
  return {
    score: score || "--",
    category: result?.engagement_category || (score >= 70 ? "High" : score >= 45 ? "Medium" : "Needs improvement"),
    best_time: best.day_of_week ? `${best.day_of_week} ${best.hour_posted}:00` : "Use best-time recommendation",
    suggestions: [
      score < 50 ? "Improve first-line hook" : "Hook is usable",
      "Add one clear CTA",
      "Use 5-10 focused hashtags",
      "Use X for short updates, LinkedIn for professional posts, Telegram for notifications"
    ]
  };
}

function updateGauge(score) {
  const g = $("predictionGauge");
  if (!g) return;
  const s = Math.max(0, Math.min(100, Number(score) || 0));
  g.style.background = `radial-gradient(circle at center,#fff 0 58%,transparent 59%),conic-gradient(var(--primary) ${(s/100)*360}deg,#f0e6b8 0deg)`;
  const span = g.querySelector("span");
  if (span) span.textContent = s ? Math.round(s) : "--";
}

async function boot() {
  document.querySelectorAll(".tab,[data-jump]").forEach(el => el.addEventListener("click", () => switchTab(el.dataset.tab || el.dataset.jump)));
  $("loginForm")?.addEventListener("submit", login);
  $("topLoginForm")?.addEventListener("submit", login);
  $("rawPostForm")?.addEventListener("submit", generatePackage);
  $("generateForm")?.addEventListener("submit", generateCaption);
  $("predictForm")?.addEventListener("submit", predictPost);
  $("savePost")?.addEventListener("click", savePost);
  $("editPost")?.addEventListener("click", editPost);
  $("submitPost")?.addEventListener("click", submitPost);
  $("schedulePost")?.addEventListener("click", schedulePost);
  $("reschedulePost")?.addEventListener("click", reschedulePost);
  $("refreshCalendar")?.addEventListener("click", loadSchedules);
  $("publishButton")?.addEventListener("click", publishPost);
  $("saveFeedback")?.addEventListener("click", saveFeedback);
  $("loadFeedback")?.addEventListener("click", loadFeedback);
  $("loadBriefButton")?.addEventListener("click", loadBrief);
  $("loginOpen")?.addEventListener("click", () => $("loginModal")?.classList.add("open"));
  $("loginClose")?.addEventListener("click", () => $("loginModal")?.classList.remove("open"));

  try { await api("/api/db/init"); } catch {}
  try {
    const [health, config, overview] = await Promise.all([api("/api/health"), api("/api/config"), api("/api/dataset-overview")]);
    show("apiStatus", health.status === "ok" ? "Online · publishing workflow" : "Issue");
    show("postingMode", config.posting_mode || "dry_run");
    show("postingModeBadge", config.posting_mode || "dry_run");
    show("datasetCount", (overview.datasets || []).length || "--");
    showReadiness(config);
  } catch (e) { show("apiStatus", "Offline"); }
}

function showReadiness() {
  const el = $("platformReadiness");
  if (!el) return;
  const rows = [
    ["X", "Live-ready with user-context write credentials."],
    ["LinkedIn", "Live-ready with approved member or organization publishing token."],
    ["Telegram", "Live-ready with bot token and chat ID."],
    ["Instagram/Facebook", "Paused for now until Meta credentials are added."]
  ];
  el.innerHTML = rows.map(([a,b]) => `<article class="platform-card ok"><strong>${a}</strong><span>${b}</span></article>`).join("");
}

async function login(ev) {
  ev.preventDefault();
  try {
    const f = new FormData(ev.currentTarget);
    const data = await api("/api/login", { method: "POST", body: body({ username: f.get("username"), password: f.get("password") }) });
    const user = data.user || { username: data.username || "admin_techcreate", role: data.role || "admin" };
    show("userPill", `${user.role}: ${user.username}`);
    show("sidebarUserInfo", `${user.role}: ${user.username}`);
    show("loginOutput", { success: data.success, user });
    show("topLoginOutput", { success: data.success, user });
    $("loginModal")?.classList.remove("open");
    toast("Login successful");
  } catch (e) { show("loginOutput", message(e)); show("topLoginOutput", message(e)); }
}

async function generatePackage(ev) {
  ev.preventDefault();
  try {
    const f = new FormData(ev.currentTarget);
    const data = await api("/api/full-pipeline", { method: "POST", body: body({ raw_text: f.get("raw_text"), platform: platformName(f.get("platform")), tone: f.get("tone"), campaign_goal: f.get("campaign_goal") }) });
    latestCaption = data.caption || "";
    show("rawPostOutput", { caption: data.caption, hashtags: data.hashtags, performance: scoreAdvice(data.engagement_prediction), best_time: data.best_time, next_steps: data.simple_next_steps, publish_preview: data.publish_preview });
    show("captionOutput", latestCaption);
    show("hashtagOutput", data.hashtags?.hashtag_string || JSON.stringify(data.hashtags));
    show("safetyOutput", { moderation: data.moderation, plagiarism: data.plagiarism });
    show("imagePromptOutput", data.image_prompt);
    show("predictionOutput", scoreAdvice(data.engagement_prediction));
    updateGauge(data.engagement_prediction?.predicted_engagement_score);
    if ($("publishCaption")) $("publishCaption").value = latestCaption;
    if ($("dbCaption")) $("dbCaption").value = latestCaption;
    toast("Package generated");
  } catch (e) { show("rawPostOutput", message(e)); }
}

async function generateCaption(ev) {
  ev.preventDefault();
  try {
    const f = new FormData(ev.currentTarget);
    const data = await api("/api/generate-caption", { method: "POST", body: body({ topic: f.get("topic"), platform: platformName(f.get("platform")), tone: f.get("tone") }) });
    latestCaption = data.caption || "";
    show("captionOutput", latestCaption);
    show("hashtagOutput", data.hashtags?.hashtag_string || JSON.stringify(data.hashtags));
    show("safetyOutput", await api("/api/moderate", { method: "POST", body: body({ text: latestCaption, platform: platformName(f.get("platform")) }) }));
    show("imagePromptOutput", await api("/api/image-prompt", { method: "POST", body: body({ topic: f.get("topic"), platform: platformName(f.get("platform")), tone: f.get("tone") }) }));
    if ($("publishCaption")) $("publishCaption").value = latestCaption;
    if ($("dbCaption")) $("dbCaption").value = latestCaption;
    toast("Caption generated");
  } catch (e) { show("captionOutput", message(e)); }
}

async function predictPost(ev) {
  ev.preventDefault();
  try {
    const f = new FormData(ev.currentTarget);
    const data = await api("/api/predict-engagement", { method: "POST", body: body({ caption: f.get("caption"), platform: platformName(f.get("platform")), content_type: f.get("content_type"), day_of_week: f.get("day_of_week"), hour_posted: Number(f.get("hour_posted")) }) });
    show("predictionOutput", scoreAdvice(data));
    updateGauge(data.predicted_engagement_score);
  } catch (e) { show("predictionOutput", message(e)); }
}

async function savePost() {
  try {
    const data = await api("/api/db/posts", { method: "POST", body: body({ title: $("dbTitle").value, caption: $("dbCaption").value, platform: platformName($("dbPlatform").value), hashtags: $("dbTags").value, image_prompt: $("imagePromptOutput")?.textContent || "" }) });
    latestPostId = data.post?.id || data.post?.post_id;
    if ($("dbPost")) $("dbPost").value = latestPostId || "";
    if ($("apPost")) $("apPost").value = latestPostId || "";
    show("dbOut", data); toast("Post saved"); loadSchedules();
  } catch (e) { show("dbOut", message(e)); }
}

async function editPost() {
  try {
    const id = $("dbPost").value;
    if (!id) return show("dbOut", "Save post first.");
    const data = await api(`/api/db/posts/${id}`, { method: "PUT", body: body({ title: $("dbTitle").value, caption: $("dbCaption").value, platform: platformName($("dbPlatform").value), hashtags: $("dbTags").value }) });
    show("dbOut", data); toast("Post updated"); loadSchedules();
  } catch (e) { show("dbOut", message(e)); }
}

async function submitPost() {
  try {
    const id = $("dbPost").value;
    if (!id) return show("dbOut", "Save post first.");
    show("dbOut", await api(`/api/db/posts/${id}/submit`, { method: "POST" })); toast("Sent for approval"); loadSchedules();
  } catch (e) { show("dbOut", message(e)); }
}

async function schedulePost() {
  try {
    const id = $("dbPost").value;
    if (!id) return show("dbOut", "Save post first.");
    const data = await api("/api/db/schedule", { method: "POST", body: body({ post_id: Number(id), scheduled_date: $("dbDate").value, scheduled_time: $("dbTime").value }) });
    show("dbOut", data); toast("Post scheduled"); loadSchedules();
  } catch (e) { show("dbOut", message(e)); }
}

async function reschedulePost() {
  try {
    const id = $("dbPost").value;
    if (!id) return show("dbOut", "Save/schedule post first.");
    const data = await api("/api/db/reschedule", { method: "POST", body: body({ post_id: Number(id), new_date: $("dbDate").value, new_time: $("dbTime").value, reason: $("dbReason").value }) });
    show("dbOut", data); toast("Post rescheduled"); loadSchedules();
  } catch (e) { show("dbOut", message(e)); }
}

async function loadSchedules() {
  try {
    const data = await api("/api/db/schedules");
    const rows = data.schedules || [];
    const lane = $("calendarLane");
    if (lane) lane.innerHTML = rows.slice(0, 6).map(r => `<article class="schedule-card"><strong>${r.platform || "Post"}</strong><span>${r.scheduled_date || ""} ${r.scheduled_time || ""}</span><p>${String(r.caption || "").slice(0, 110)}</p></article>`).join("");
    renderTable("calendarTable", rows, ["post_id", "platform", "scheduled_date", "scheduled_time", "post_status", "caption"]);
  } catch (e) { show("calendarTable", message(e)); }
}

async function publishPost() {
  try {
    const data = await api("/api/publish", { method: "POST", body: body({ platform: platformName($("publishPlatform").value), caption: $("publishCaption").value, media_url: $("publishMediaUrl").value }) });
    show("publishOutput", data);
    toast(data.status === "published" || data.status === "sent" ? "Published" : "Publisher response received");
  } catch (e) { show("publishOutput", message(e)); }
}

async function saveFeedback() {
  try {
    const data = await api("/api/db/review", { method: "POST", body: body({ post_id: Number($("apPost").value || latestPostId || 0) || null, rating: Number($("reviewRating").value || 5), notes: $("reviewNotes").value, caption: $("publishCaption").value, platform: platformName($("publishPlatform").value) }) });
    show("reviewOut", data); toast("Feedback saved");
  } catch (e) { show("reviewOut", message(e)); }
}

async function loadFeedback() {
  try { show("reviewOut", await api("/api/db/reviews")); } catch (e) { show("reviewOut", message(e)); }
}

async function loadPublisherInfo() {
  try { show("integrationStatus", await api("/api/integrations")); } catch (e) { show("integrationStatus", message(e)); }
  try { show("competitorOutput", await api("/api/competitors")); } catch (e) { show("competitorOutput", message(e)); }
}

async function loadBrief() {
  try { show("briefOutput", await api(`/api/content/brief?platform=${encodeURIComponent(platformName($("briefPlatform")?.value))}`)); } catch (e) { show("briefOutput", message(e)); }
}

async function loadAnalytics() {
  try {
    const analytics = await api("/api/analytics");
    const trends = await api("/api/trends");
    const totals = analytics.totals || {};
    const metrics = $("metricStrip");
    if (metrics) metrics.innerHTML = `<article class="metric"><span>Reach</span><strong>${totals.reach || 0}</strong><em>Total reach</em></article><article class="metric"><span>Likes</span><strong>${totals.likes || 0}</strong><em>Total likes</em></article><article class="metric"><span>Comments</span><strong>${totals.comments || 0}</strong><em>Total comments</em></article><article class="metric"><span>ER</span><strong>${analytics.average_engagement_rate || 0}</strong><em>Average rate</em></article>`;
    const cloud = $("trendCloud");
    if (cloud) cloud.innerHTML = (trends.trending_keywords || []).slice(0, 18).map(x => `<span class="trend-chip">${x}</span>`).join("");
    renderTable("topPostsTable", analytics.top_posts || analytics.records || [], ["platform", "caption", "reach", "likes", "engagement_rate"]);
  } catch (e) { show("metricStrip", message(e)); }
}

function renderTable(id, rows, cols) {
  const el = $(id);
  if (!el) return;
  if (!rows || !rows.length) { el.innerHTML = "<tr><td>No data yet</td></tr>"; return; }
  el.innerHTML = `<thead><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${cols.map(c => `<td>${String(r[c] ?? "").slice(0, 140)}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

document.addEventListener("DOMContentLoaded", boot);
