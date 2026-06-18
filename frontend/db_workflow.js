const dbApi = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || `Request failed: ${response.status}`);
  return data;
};

const dbPretty = (value) => JSON.stringify(value, null, 2);
const dbEl = (id) => document.getElementById(id);

function showFriendlyMessage(targetId, result, fallback = "Done") {
  const target = dbEl(targetId);
  if (!target) return;
  if (result?.message) {
    target.textContent = `${result.message}\n\n${dbPretty(result)}`;
  } else {
    target.textContent = `${fallback}\n\n${dbPretty(result)}`;
  }
}

function injectWorkflowTools() {
  const calendar = dbEl("calendar");
  const adminGrid = document.querySelector("#admin .card-grid");

  if (calendar && !dbEl("dbWorkflowCard")) {
    const card = document.createElement("article");
    card.className = "tool-card";
    card.id = "dbWorkflowCard";
    card.innerHTML = `
      <div class="card-head">
        <div><span>SQLite workflow</span><h3>Save, schedule, reschedule</h3></div>
        <a class="cta small" href="/static/workflow_runner.html">Open runner</a>
      </div>
      <div class="grid-2">
        <label>Post ID<input id="dbPostId" type="number" value="1"></label>
        <label>Date<input id="dbDate" type="date"></label>
      </div>
      <div class="grid-2">
        <label>Time<input id="dbTime" type="time" value="19:00"></label>
        <label>Reason<input id="dbReason" value="Better engagement slot"></label>
      </div>
      <div class="inline-actions">
        <button class="cta small" id="dbScheduleBtn" type="button">Schedule</button>
        <button class="ghost small" id="dbRescheduleBtn" type="button">Reschedule</button>
      </div>
      <pre id="dbWorkflowOutput">Ready. Save a post first from the runner or API docs, then schedule/reschedule it here.</pre>
    `;
    calendar.appendChild(card);

    dbEl("dbScheduleBtn")?.addEventListener("click", async () => {
      try {
        const result = await dbApi("/api/db/schedule", {
          method: "POST",
          body: JSON.stringify({
            post_id: Number(dbEl("dbPostId").value || 1),
            scheduled_date: dbEl("dbDate").value,
            scheduled_time: dbEl("dbTime").value,
            username: "editor_creator",
          }),
        });
        showFriendlyMessage("dbWorkflowOutput", result, "Post scheduled");
        if (typeof window.loadCalendar === "function") window.loadCalendar();
      } catch (error) {
        dbEl("dbWorkflowOutput").textContent = `Could not schedule post: ${error.message}`;
      }
    });

    dbEl("dbRescheduleBtn")?.addEventListener("click", async () => {
      try {
        const result = await dbApi("/api/db/reschedule", {
          method: "POST",
          body: JSON.stringify({
            post_id: Number(dbEl("dbPostId").value || 1),
            new_date: dbEl("dbDate").value,
            new_time: dbEl("dbTime").value,
            username: "editor_creator",
            reason: dbEl("dbReason").value,
          }),
        });
        showFriendlyMessage("dbWorkflowOutput", result, "Post rescheduled");
        if (typeof window.loadCalendar === "function") window.loadCalendar();
      } catch (error) {
        dbEl("dbWorkflowOutput").textContent = `Could not reschedule post: ${error.message}`;
      }
    });
  }

  if (adminGrid && !dbEl("dbReviewCard")) {
    const review = document.createElement("article");
    review.className = "tool-card wide";
    review.id = "dbReviewCard";
    review.innerHTML = `
      <div class="card-head">
        <div><span>Feedback loop</span><h3>Store review for post improvement</h3></div>
        <button class="ghost small" id="dbLoadReviewsBtn" type="button">Load reviews</button>
      </div>
      <div class="grid-2">
        <label>Post ID, optional<input id="reviewPostId" type="number" value="1"></label>
        <label>Rating 1-5<input id="reviewRating" type="number" min="1" max="5" value="5"></label>
      </div>
      <label>Review notes<input id="reviewNotes" value="Good hook and CTA"></label>
      <div class="inline-actions">
        <button class="cta small" id="dbReviewBtn" type="button">Save feedback</button>
        <a class="ghost small" href="/static/workflow_runner.html">Open workflow runner</a>
      </div>
      <pre id="dbReviewOutput">Ready. Feedback will be stored in SQLite.</pre>
    `;
    adminGrid.appendChild(review);

    dbEl("dbReviewBtn")?.addEventListener("click", async () => {
      try {
        const caption = dbEl("publishCaption")?.value || "AI automation test caption #AI";
        const platform = dbEl("publishPlatform")?.value === "X" ? "Twitter" : (dbEl("publishPlatform")?.value || "Instagram");
        const result = await dbApi("/api/db/review", {
          method: "POST",
          body: JSON.stringify({
            post_id: Number(dbEl("reviewPostId").value || 0) || null,
            platform,
            caption,
            rating: Number(dbEl("reviewRating").value || 5),
            notes: dbEl("reviewNotes").value,
            created_by: "editor_creator",
          }),
        });
        showFriendlyMessage("dbReviewOutput", result, "Feedback saved");
      } catch (error) {
        dbEl("dbReviewOutput").textContent = `Could not save feedback: ${error.message}`;
      }
    });

    dbEl("dbLoadReviewsBtn")?.addEventListener("click", async () => {
      try {
        const result = await dbApi("/api/db/reviews");
        showFriendlyMessage("dbReviewOutput", result, "Reviews loaded");
      } catch (error) {
        dbEl("dbReviewOutput").textContent = `Could not load reviews: ${error.message}`;
      }
    });
  }
}

async function loadDbCalendar() {
  try {
    const result = await dbApi("/api/db/schedules");
    const rows = result.schedules || [];
    if (typeof renderCalendarLane === "function") renderCalendarLane(rows);
    if (typeof renderTable === "function") {
      renderTable("calendarTable", rows, [
        { key: "post_id", label: "Post" },
        { key: "platform", label: "Platform" },
        { key: "scheduled_date", label: "Date" },
        { key: "scheduled_time", label: "Time" },
        { key: "post_status", label: "Post status" },
        { key: "caption", label: "Caption" },
      ]);
    }
  } catch (error) {
    const lane = dbEl("calendarLane");
    if (lane) lane.innerHTML = `<article class="schedule-card"><strong>Database calendar issue</strong><p>${error.message}</p></article>`;
  }
}

window.addEventListener("load", () => {
  injectWorkflowTools();
  window.loadCalendar = loadDbCalendar;
  dbEl("refreshCalendar")?.addEventListener("click", loadDbCalendar);
});
