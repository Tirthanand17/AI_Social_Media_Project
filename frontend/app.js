const $ = (id) => document.getElementById(id);
const J = (x) => typeof x === "string" ? x : JSON.stringify(x, null, 2);
const out = (id, x) => { const e = $(id); if (e) e.textContent = J(x); };
const formBody = (form) => JSON.stringify(Object.fromEntries(new FormData(form).entries()));
const platformKey = (x) => x === "X" ? "Twitter" : x;

let currentUser = null;
let latestPackage = null;
let latestCaption = "";

async function api(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { message: text }; }
  if (!response.ok) throw new Error(data.message || response.statusText || response.status);
  return data;
}

function friendlyError(error) {
  const message = String(error?.message || error);
  if (message.includes("404")) return "This feature route is missing. Restart Uvicorn after applying latest patch.";
  if (message.toLowerCase().includes("failed to fetch")) return "Backend is not running. Start Uvicorn and open http://127.0.0.1:8010/";
  if (message.toLowerCase().includes("token") || message.toLowerCase().includes("credential")) return "API key missing or invalid. Keep dry-run mode, or add keys in .env.";
  return message;
}

function showToast(message) {
  let toast = $("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.style.cssText = "position:fixed;left:50%;bottom:70px;transform:translateX(-50%);z-index:9999;background:#1a1200;color:#ffe082;padding:12px 18px;border-radius:999px;font:800 13px Segoe UI,Arial;box-shadow:0 10px 25px rgba(0,0,0,.22)";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.remove(), 3200);
}

function openLogin() { $("loginModal")?.classList.add("open"); }
function closeLogin() { $("loginModal")?.classList.remove("open"); }
function handleLogout() {
  currentUser = null;
  if ($("userPill")) $("userPill").textContent = "Guest workspace";
  if ($("sidebarUserInfo")) $("sidebarUserInfo").textContent = "Not logged in";
  if ($("loginOpen")) $("loginOpen").style.display = "";
  if ($("logoutBtn")) $("logoutBtn").style.display = "none";
  showToast("Logged out");
}
window.openLogin = openLogin;
window.handleLogout = handleLogout;

async function doLogin(event, outputId) {
  event.preventDefault();
  try {
    const result = await api("/api/login", { method: "POST", body: formBody(event.currentTarget) });
    currentUser = result.user || {};
    if ($("userPill")) $("userPill").textContent = `${currentUser.role}: ${currentUser.username}`;
    if ($("sidebarUserInfo")) $("sidebarUserInfo").textContent = `${currentUser.role}: ${currentUser.username}`;
    if ($("loginOpen")) $("loginOpen").style.display = "none";
    if ($("logoutBtn")) $("logoutBtn").style.display = "";
    out(outputId, { success: result.success, user: result.user, message: "Login successful" });
    closeLogin();
    showToast("Login successful");
  } catch (error) { out(outputId, friendlyError(error)); }
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((button) => button.classList.toggle("active", button.dataset.tab === name));
  document.querySelectorAll(".workspace").forEach((section) => section.classList.toggle("active", section.id === name));
  if (name === "analytics") loadAnalytics();
  if (name === "calendar") loadCalendar();
  if (name === "admin") { injectAdminWorkflow(); loadIntegrations(); loadCompetitors(); }
}

function hashtagText(data) {
  return data?.hashtag_string || data?.hashtags?.join(" ") || data?.recommended_hashtags?.join(" ") || "#AI #SocialMedia";
}

function engagementScore(data) { return Number(data?.predicted_engagement_score ?? data?.score ?? 0); }

function updateGauge(value) {
  const gauge = $("predictionGauge");
  if (!gauge) return;
  const score = Math.max(0, Math.min(100, Number(value) || 0));
  const degrees = (score / 100) * 360;
  gauge.style.background = `radial-gradient(circle at center,#fff 0 58%,transparent 59%),conic-gradient(var(--primary) ${degrees}deg,#f0e6b8 ${degrees}deg)`;
  gauge.querySelector("span").textContent = score ? Math.round(score) : "--";
}

function performanceAdvice(result) {
  const score = engagementScore(result);
  const category = result?.engagement_category || (score >= 70 ? "High" : score >= 45 ? "Medium" : "Needs improvement");
  const best = result?.best_time || {};
  return {
    score: score || "--",
    category,
    best_time: best.day_of_week ? `${best.day_of_week} at ${best.hour_posted}:00` : "Use Calendar best-time suggestion",
    suggestions: [
      score < 50 ? "Improve hook in first line" : "Hook looks usable",
      "Keep caption clear and add one CTA",
      "Use 5-10 focused hashtags",
      "Prefer image/reel for Instagram and professional text for LinkedIn"
    ]
  };
}

function applyPackage(data) {
  latestPackage = data;
  latestCaption = data.caption || "";
  out("rawPostOutput", {
    caption: data.caption,
    hashtags: hashtagText(data.hashtags),
    best_time: data.best_time,
    performance: performanceAdvice(data.engagement_prediction || {}),
    publish_preview: data.publish_preview,
  });
  out("captionOutput", latestCaption);
  out("hashtagOutput", hashtagText(data.hashtags));
  out("safetyOutput", { moderation: data.moderation, plagiarism: data.plagiarism });
  out("imagePromptOutput", data.image_prompt || {});
  updateGauge(engagementScore(data.engagement_prediction));
  out("predictionOutput", performanceAdvice(data.engagement_prediction || {}));
  if ($("publishCaption")) $("publishCaption").value = latestCaption;
  if ($("dbCaption")) $("dbCaption").value = latestCaption;
  showToast("Package generated. Check performance score, then save/schedule.");
}

async function boot() {
  try { await api("/api/db/init"); } catch {}
  try {
    const [health, config, datasets] = await Promise.all([api("/api/health"), api("/api/config"), api("/api/dataset-overview")]);
    if ($("apiStatus")) $("apiStatus").textContent = health.status === "ok" ? "Online · simple workflow v5" : "Issue";
    if ($("postingMode")) $("postingMode").textContent = config.posting_mode || "dry_run";
    if ($("postingModeBadge")) $("postingModeBadge").textContent = config.posting_mode || "dry_run";
    if ($("datasetCount")) $("datasetCount").textContent = (datasets.datasets || []).length || "--";
    renderPlatformReadiness(config);
  } catch {
    if ($("apiStatus")) $("apiStatus").textContent = "Offline";
  }
}

function renderPlatformReadiness(config = {}) {
  const element = $("platformReadiness");
  if (!element) return;
  const items = [
    ["Instagram", "Dry-run ready. Live Meta credentials later."],
    ["Facebook", "Dry-run ready. Live Meta credentials later."],
    ["LinkedIn", "Ready if token is configured; dry-run safe otherwise."],
    ["X/Twitter", "Optional. Keep disabled unless paid/API credentials are ready."],
  ];
  element.innerHTML = items.map(([name, note]) => `<article class="platform-card ok"><strong>${name}</strong><span>${note}</span></article>`).join("");
}

async function loadBrief() {
  try {
    const platform = platformKey($("briefPlatform")?.value || "Instagram");
    out("briefOutput", await api("/api/content/brief?platform=" + encodeURIComponent(platform)));
  } catch (error) { out("briefOutput", friendlyError(error)); }
}

function injectCalendarWorkflow() {
  const calendar = $("calendar");
  if (!calendar || $("dbCard")) return;
  const card = document.createElement("article");
  card.className = "tool-card wide";
  card.id = "dbCard";
  card.innerHTML = `
    <div class="card-head"><div><span>Simple storage workflow</span><h3>Save, edit, approve, schedule, reschedule</h3></div><button class="ghost small" id="loadPosts">Load saved posts</button></div>
    <div class="grid-2"><label>Post ID<input id="dbPost" type="number" placeholder="Auto after save"></label><label>Title<input id="dbTitle" value="AI Social Studio post"></label></div>
    <label>Editable caption<textarea id="dbCaption" rows="5">AI automation test caption #AI</textarea></label>
    <div class="grid-2"><label>Platform<select id="dbPlatform"><option>Instagram</option><option>Facebook</option><option>X</option><option>LinkedIn</option></select></label><label>Hashtags<input id="dbTags" value="#AI #Automation"></label></div>
    <div class="grid-2"><label>Date<input id="dbDate" type="date"></label><label>Time<input id="dbTime" type="time" value="19:00"></label></div>
    <label>Reason for reschedule<input id="dbReason" value="Better engagement slot"></label>
    <div class="inline-actions"><button class="cta small" id="savePost">Save post</button><button class="ghost small" id="editPost">Edit post</button><button class="ghost small" id="submitPost">Submit approval</button><button class="cta small" id="schedulePost">Schedule</button><button class="ghost small" id="reschedulePost">Reschedule</button></div>
    <pre id="dbOut">Ready. Generate a caption first, then save and schedule.</pre>`;
  calendar.appendChild(card);
  $("savePost").onclick = savePost;
  $("editPost").onclick = editPost;
  $("submitPost").onclick = submitPost;
  $("schedulePost").onclick = () => schedulePost(false);
  $("reschedulePost").onclick = () => schedulePost(true);
  $("loadPosts").onclick = async () => out("dbOut", await api("/api/db/posts"));
}

async function savePost() {
  try {
    const result = await api("/api/db/posts", { method: "POST", body: JSON.stringify({
      caption: $("dbCaption").value, platform: platformKey($("dbPlatform").value), hashtags: $("dbTags").value,
      title: $("dbTitle").value, image_prompt: $("imagePromptOutput")?.textContent || "", created_by: currentUser?.username || "editor_creator",
    }) });
    $("dbPost").value = result.post?.id || result.post?.post_id || "";
    if ($("apPost")) $("apPost").value = $("dbPost").value;
    out("dbOut", result);
    showToast("Post saved");
    loadCalendar();
  } catch (error) { out("dbOut", friendlyError(error)); }
}

async function editPost() {
  try {
    const id = $("dbPost").value;
    if (!id) return out("dbOut", "Save a post first, then edit.");
    const result = await api(`/api/db/posts/${id}`, { method: "PUT", body: JSON.stringify({ caption: $("dbCaption").value, hashtags: $("dbTags").value, title: $("dbTitle").value, platform: platformKey($("dbPlatform").value) }) });
    out("dbOut", result); showToast("Post updated"); loadCalendar();
  } catch (error) { out("dbOut", friendlyError(error)); }
}

async function submitPost() {
  try {
    if (!$("dbPost").value) return out("dbOut", "Save a post first, then submit for approval.");
    out("dbOut", await api(`/api/db/posts/${$("dbPost").value}/submit`, { method: "POST" }));
    showToast("Sent for approval"); loadCalendar();
  } catch (error) { out("dbOut", friendlyError(error)); }
}

async function schedulePost(isReschedule) {
  try {
    const id = Number($("dbPost").value), date = $("dbDate").value, time = $("dbTime").value;
    if (!id || !date || !time) return out("dbOut", "Post ID, date, and time are required.");
    const payload = isReschedule ? { post_id: id, new_date: date, new_time: time, reason: $("dbReason").value, username: currentUser?.username || "editor_creator" } : { post_id: id, scheduled_date: date, scheduled_time: time, username: currentUser?.username || "editor_creator" };
    const result = await api(isReschedule ? "/api/db/reschedule" : "/api/db/schedule", { method: "POST", body: JSON.stringify(payload) });
    out("dbOut", result); showToast(isReschedule ? "Post rescheduled" : "Post scheduled"); loadCalendar();
  } catch (error) { out("dbOut", friendlyError(error)); }
}

async function loadCalendar() {
  injectCalendarWorkflow();
  try {
    const data = await api("/api/db/schedules");
    const rows = data.schedules || [];
    if ($("calendarLane")) $("calendarLane").innerHTML = rows.slice(0, 6).map((row) => `<article class="schedule-card"><strong>${row.platform || "Post"}</strong><span>${row.scheduled_date || ""} ${row.scheduled_time || ""}</span><p>${String(row.caption || "").slice(0, 110)}</p></article>`).join("");
    renderTable("calendarTable", rows, ["post_id", "platform", "scheduled_date", "scheduled_time", "post_status", "caption"]);
  } catch (error) { out("calendarTable", friendlyError(error)); }
}

function injectAdminWorkflow() {
  const grid = document.querySelector("#admin .card-grid");
  if (!grid || $("reviewCard")) return;
  const card = document.createElement("article");
  card.className = "tool-card wide";
  card.id = "reviewCard";
  card.innerHTML = `
    <div class="card-head"><div><span>Feedback + approval</span><h3>Approve posts and store performance feedback</h3></div><button class="ghost small" id="loadReviews">Load feedback</button></div>
    <div class="grid-2"><label>Post ID<input id="apPost" type="number" value="1"></label><label>Rating<input id="rating" type="number" min="1" max="5" value="5"></label></div>
    <label>Notes<input id="notes" value="Good hook and CTA"></label>
    <div class="inline-actions"><button class="cta small" id="approve">Approve</button><button class="ghost small" id="reject">Reject</button><button class="cta small" id="review">Save feedback</button></div>
    <pre id="reviewOut">Ready. Approve saved posts and save feedback after testing performance.</pre>`;
  grid.appendChild(card);
  $("approve").onclick = () => approvePost(true);
  $("reject").onclick = () => approvePost(false);
  $("review").onclick = saveReview;
  $("loadReviews").onclick = async () => out("reviewOut", await api("/api/db/reviews"));
}

async function approvePost(approved) {
  try {
    out("reviewOut", await api("/api/db/approve", { method: "POST", body: JSON.stringify({ post_id: Number($("apPost").value), approved, approved_by: currentUser?.username || "admin_techcreate", reason: $("notes").value }) }));
    showToast(approved ? "Post approved" : "Post rejected");
  } catch (error) { out("reviewOut", friendlyError(error)); }
}

async function saveReview() {
  try {
    out("reviewOut", await api("/api/db/review", { method: "POST", body: JSON.stringify({ post_id: Number($("apPost").value) || null, platform: platformKey($("publishPlatform")?.value || "Instagram"), caption: $("publishCaption")?.value || latestCaption, rating: Number($("rating").value), notes: $("notes").value, created_by: currentUser?.username || "editor_creator" }) }));
    showToast("Feedback saved");
  } catch (error) { out("reviewOut", friendlyError(error)); }
}

function renderTable(id, rows, columns) {
  const element = $(id); if (!element) return;
  if (!rows.length) { element.innerHTML = "<tbody><tr><td>No records yet.</td></tr></tbody>"; return; }
  element.innerHTML = "<thead><tr>" + columns.map((c) => `<th>${c}</th>`).join("") + "</tr></thead><tbody>" + rows.map((row) => "<tr>" + columns.map((c) => `<td>${String(row[c] ?? "").slice(0, 120)}</td>`).join("") + "</tr>").join("") + "</tbody>";
}

async function loadAnalytics() {
  try {
    const [analytics, trends, charts] = await Promise.all([api("/api/analytics"), api("/api/trends"), api("/api/db/charts").catch(() => ({}))]);
    if ($("metricStrip")) $("metricStrip").innerHTML = [["Posts", analytics.records], ["Reach", analytics.total_reach], ["Likes", analytics.total_likes], ["Avg ER", analytics.avg_engagement_rate]].map((item) => `<article class="metric"><span>${item[0]}</span><strong>${item[1] ?? "--"}</strong><em>Performance analysis</em></article>`).join("");
    if ($("engagementBars")) $("engagementBars").innerHTML = (analytics.top_posts || []).slice(0, 12).map((post) => `<span class="bar" style="height:${Math.max(18, Number(post.engagement_rate) || 20)}%"></span>`).join("");
    if ($("trendCloud")) $("trendCloud").innerHTML = (trends.trending_keywords || []).slice(0, 20).map((keyword) => `<span class="trend-chip">${keyword.keyword}</span>`).join("");
    renderTable("topPostsTable", analytics.top_posts || [], ["post_id", "platform", "likes", "comments", "shares", "engagement_rate"]);
    renderTable("trendsTable", trends.trending_keywords || [], ["keyword", "platform", "trend_score", "trend_category"]);
  } catch (error) { out("metricStrip", friendlyError(error)); }
}

async function loadCompetitors() {
  try { out("competitorOutput", await api("/api/competitors")); }
  catch { out("competitorOutput", "Optional insight only. Main workflow does not depend on competitor alerts."); }
}

async function loadIntegrations() {
  const statuses = [["Gemini/Groq", "Used when API key is in .env; fallback works locally"], ["Telegram", "Optional notification test"], ["LinkedIn", "Dry-run/live-ready if token exists"], ["Meta", "Facebook/Instagram credentials can be added later"]];
  if ($("integrationStatus")) $("integrationStatus").innerHTML = statuses.map(([name, note]) => `<span class="integration-pill ok"><strong>${name}</strong><span>${note}</span></span>`).join("");
}

function wireEvents() {
  document.querySelectorAll(".tab").forEach((button) => button.onclick = () => switchTab(button.dataset.tab));
  document.querySelectorAll("[data-jump]").forEach((button) => button.onclick = () => switchTab(button.dataset.jump));
  if ($("loginOpen")) $("loginOpen").onclick = openLogin;
  if ($("loginClose")) $("loginClose").onclick = closeLogin;
  if ($("logoutBtn")) $("logoutBtn").onclick = handleLogout;
  if ($("sidebarLoginBtn")) $("sidebarLoginBtn").onclick = () => currentUser ? handleLogout() : openLogin();
  if ($("topLoginForm")) $("topLoginForm").onsubmit = (event) => doLogin(event, "topLoginOutput");
  if ($("loginForm")) $("loginForm").onsubmit = (event) => doLogin(event, "loginOutput");
  if ($("loadBriefButton")) $("loadBriefButton").onclick = loadBrief;
  if ($("briefPlatform")) $("briefPlatform").onchange = loadBrief;
  if ($("refreshCalendar")) $("refreshCalendar").onclick = loadCalendar;

  if ($("rawPostForm")) $("rawPostForm").onsubmit = async (event) => {
    event.preventDefault();
    try {
      const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
      payload.platform = platformKey(payload.platform);
      applyPackage(await api("/api/full-pipeline", { method: "POST", body: JSON.stringify(payload) }));
    } catch (error) { out("rawPostOutput", friendlyError(error)); }
  };

  if ($("generateForm")) $("generateForm").onsubmit = async (event) => {
    event.preventDefault();
    try {
      const payload = Object.fromEntries(new FormData(event.currentTarget).entries()); payload.platform = platformKey(payload.platform);
      const captionResult = await api("/api/generate-caption", { method: "POST", body: JSON.stringify(payload) });
      latestCaption = captionResult.caption || captionResult.captions?.[0]?.caption || J(captionResult);
      out("captionOutput", latestCaption);
      const [hashtags, moderation, plagiarism, imagePrompt] = await Promise.all([
        api("/api/hashtags", { method: "POST", body: JSON.stringify({ text: latestCaption, platform: payload.platform }) }),
        api("/api/moderate", { method: "POST", body: JSON.stringify({ text: latestCaption, platform: payload.platform }) }),
        api("/api/plagiarism", { method: "POST", body: JSON.stringify({ text: latestCaption, platform: payload.platform }) }),
        api("/api/image-prompt", { method: "POST", body: JSON.stringify(payload) }),
      ]);
      out("hashtagOutput", hashtagText(hashtags)); out("safetyOutput", { moderation, plagiarism }); out("imagePromptOutput", imagePrompt);
      if ($("dbCaption")) $("dbCaption").value = latestCaption; if ($("publishCaption")) $("publishCaption").value = latestCaption;
      showToast("Caption generated. Now score performance or save it.");
    } catch (error) { out("captionOutput", friendlyError(error)); }
  };

  if ($("predictForm")) $("predictForm").onsubmit = async (event) => {
    event.preventDefault();
    try {
      const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
      payload.platform = platformKey(payload.platform); payload.hour_posted = Number(payload.hour_posted); payload.hashtags = (payload.caption.match(/#\w+/g) || []).join(" "); payload.sentiment_score = 0.7; payload.has_image = 1;
      const result = await api("/api/predict-engagement", { method: "POST", body: JSON.stringify(payload) });
      updateGauge(engagementScore(result)); out("predictionOutput", performanceAdvice(result));
    } catch (error) { out("predictionOutput", friendlyError(error)); }
  };

  if ($("publishButton")) $("publishButton").onclick = async () => {
    try { out("publishOutput", await api("/api/publish", { method: "POST", body: JSON.stringify({ platform: platformKey($("publishPlatform").value), caption: $("publishCaption").value, media_url: $("publishMediaUrl").value || null }) })); showToast("Dry-run publish completed"); }
    catch (error) { out("publishOutput", friendlyError(error)); }
  };

  if ($("telegramButton")) $("telegramButton").onclick = async () => {
    try { out("publishOutput", await api("/api/telegram", { method: "POST", body: JSON.stringify({ message: $("publishCaption").value }) })); }
    catch (error) { out("publishOutput", "Telegram is optional. Add token/chat ID in .env to enable it."); }
  };
}

wireEvents();
boot();
injectCalendarWorkflow();
injectAdminWorkflow();
