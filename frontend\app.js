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

const setText = (id, value) => {
  document.getElementById(id).textContent =
    typeof value === "string" ? value : pretty(value);
};

const formJson = (form) => Object.fromEntries(new FormData(form).entries());

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".workspace").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(button.dataset.tab).classList.add("active");
    if (button.dataset.tab === "analytics") loadAnalytics();
    if (button.dataset.tab === "calendar") loadCalendar();
    if (button.dataset.tab === "admin") loadCompetitors();
  });
});

async function checkHealth() {
  try {
    const data = await api("/api/health");
    const status = document.getElementById("apiStatus");
    status.textContent = data.status === "running" ? "API online" : "API issue";
    status.classList.add("ok");
  } catch (error) {
    document.getElementById("apiStatus").textContent = "API offline";
  }
}

document.getElementById("generateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formJson(event.currentTarget);
  setText("captionOutput", "Generating...");
  try {
    const caption = await api("/api/content/generate-caption", {
      method: "POST",
      body: JSON.stringify(payload),
    });
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
  setText("predictionOutput", "Scoring...");
  try {
    const prediction = await api("/api/ml/predict-engagement", {
      method: "POST",
      body: JSON.stringify(payload),
    });
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

async function loadAnalytics() {
  const [analytics, trends] = await Promise.all([
    api("/api/analytics/summary"),
    api("/api/trends/analyze"),
  ]);
  document.getElementById("metricStrip").innerHTML = [
    ["Posts", analytics.records],
    ["Reach", analytics.total_reach],
    ["Likes", analytics.total_likes],
    ["Avg ER", analytics.avg_engagement_rate],
  ]
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`)
    .join("");
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

async function loadCalendar() {
  const data = await api("/api/scheduler/summary");
  renderTable("calendarTable", data.pending, [
    { key: "post_id", label: "Post" },
    { key: "platform", label: "Platform" },
    { key: "scheduled_time", label: "Time" },
    { key: "status", label: "Status" },
    { key: "caption", label: "Caption" },
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
    setText("loginOutput", login);
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

document.getElementById("publishButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/publisher/dry-run", {
      method: "POST",
      body: JSON.stringify({
        platform: "Instagram",
        caption: document.getElementById("publishCaption").value,
      }),
    });
    setText("publishOutput", result);
  } catch (error) {
    setText("publishOutput", error.message);
  }
});

checkHealth();
