/* ============================================
   TaskFlow — app logic
   Simple task store backed by localStorage.
   No framework — vanilla JS, ES modules-free for
   easy local file:// usage.
   ============================================ */

const STORAGE_KEY = "taskflow.tasks.v1";

function uuid() {
  if (window.crypto && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "id-" + Date.now() + "-" + Math.random().toString(16).slice(2);
}

const TaskStore = {
  seedIfEmpty() {
    if (localStorage.getItem(STORAGE_KEY)) return;
    const seed = [
      {
        id: uuid(),
        title: "Draft onboarding checklist",
        notes: "List every step a new teammate needs on day one, from account access to their first task.",
        priority: "high",
        dueDate: nextDate(2),
        done: false,
        createdAt: Date.now()
      },
      {
        id: uuid(),
        title: "Review design QA notes",
        notes: "Go through the feedback from yesterday's review and mark which items need follow-up.",
        priority: "medium",
        dueDate: nextDate(4),
        done: false,
        createdAt: Date.now() - 1000
      },
      {
        id: uuid(),
        title: "Archive last sprint's board",
        notes: "",
        priority: "low",
        dueDate: nextDate(-1),
        done: true,
        createdAt: Date.now() - 2000
      }
    ];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(seed));
  },

  getAll() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  },

  getById(id) {
    return this.getAll().find(t => t.id === id) || null;
  },

  save(tasks) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  },

  add(task) {
    const tasks = this.getAll();
    tasks.unshift({
      id: uuid(),
      createdAt: Date.now(),
      done: false,
      ...task
    });
    this.save(tasks);
  },

  update(id, changes) {
    const tasks = this.getAll().map(t => (t.id === id ? { ...t, ...changes } : t));
    this.save(tasks);
  },

  remove(id) {
    const tasks = this.getAll().filter(t => t.id !== id);
    this.save(tasks);
  },

  toggleDone(id) {
    const t = this.getById(id);
    if (t) this.update(id, { done: !t.done });
  }
};

function nextDate(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

function formatDate(iso) {
  if (!iso) return "No due date";
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

/* ---------- Dashboard page ---------- */
function initDashboard() {
  TaskStore.seedIfEmpty();

  const listEl = document.getElementById("task-list");
  const searchEl = document.getElementById("search-input");
  const chips = document.querySelectorAll(".filter-chip");
  const statTotal = document.getElementById("stat-total");
  const statOpen = document.getElementById("stat-open");
  const statDone = document.getElementById("stat-done");
  const statHigh = document.getElementById("stat-high");
  const addForm = document.getElementById("add-task-form");
  const addToggleBtn = document.getElementById("toggle-add-form");

  let currentFilter = "all";
  let searchTerm = "";

  function render() {
    const all = TaskStore.getAll();

    statTotal.textContent = all.length;
    statOpen.textContent = all.filter(t => !t.done).length;
    statDone.textContent = all.filter(t => t.done).length;
    statHigh.textContent = all.filter(t => t.priority === "high" && !t.done).length;

    let filtered = all;
    if (currentFilter === "open") filtered = filtered.filter(t => !t.done);
    if (currentFilter === "done") filtered = filtered.filter(t => t.done);
    if (currentFilter === "high") filtered = filtered.filter(t => t.priority === "high");
    if (searchTerm) {
      filtered = filtered.filter(t =>
        t.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    listEl.innerHTML = "";

    if (filtered.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state">
          <h3>Nothing here yet</h3>
          <p>Add a task or adjust your filters to see it appear.</p>
        </div>`;
      return;
    }

    filtered
      .sort((a, b) => b.createdAt - a.createdAt)
      .forEach(t => {
        const row = document.createElement("div");
        row.className = "task-row" + (t.done ? " done" : "");
        row.innerHTML = `
          <button class="checkbox ${t.done ? "checked" : ""}" data-id="${t.id}" aria-label="Toggle complete">
            ${t.done ? "✓" : ""}
          </button>
          <div class="task-main">
            <a class="title" href="task-detail.html?id=${t.id}">${escapeHtml(t.title)}</a>
            <div class="meta">Due ${formatDate(t.dueDate)}</div>
          </div>
          <span class="priority-tag priority-${t.priority}">${t.priority}</span>
        `;
        row.querySelector(".checkbox").addEventListener("click", () => {
          TaskStore.toggleDone(t.id);
          render();
        });
        listEl.appendChild(row);
      });
  }

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentFilter = chip.dataset.filter;
      render();
    });
  });

  searchEl.addEventListener("input", e => {
    searchTerm = e.target.value;
    render();
  });

  addToggleBtn.addEventListener("click", () => {
    addForm.classList.toggle("open");
  });

  addForm.addEventListener("submit", e => {
    e.preventDefault();
    const title = document.getElementById("new-title").value.trim();
    if (!title) return;
    TaskStore.add({
      title,
      notes: document.getElementById("new-notes").value.trim(),
      priority: document.getElementById("new-priority").value,
      dueDate: document.getElementById("new-due").value
    });
    addForm.reset();
    addForm.classList.remove("open");
    render();
  });

  render();
}

/* ---------- Task detail page ---------- */
function initTaskDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const task = id ? TaskStore.getById(id) : null;

  const wrap = document.getElementById("detail-wrap");
  if (!task) {
    wrap.innerHTML = `
      <div class="empty-state">
        <h3>Task not found</h3>
        <p>It may have been deleted. <a href="dashboard.html">Back to dashboard</a></p>
      </div>`;
    return;
  }

  document.getElementById("detail-title").textContent = task.title;
  document.getElementById("detail-title-input").value = task.title;
  document.getElementById("detail-priority").value = task.priority;
  document.getElementById("detail-due").value = task.dueDate || "";
  document.getElementById("detail-notes").value = task.notes || "";
  document.getElementById("detail-status-checkbox").checked = task.done;
  updateStatusLabel(task.done);
  document.title = `${task.title} — TaskFlow`;

  function updateStatusLabel(done) {
    document.getElementById("detail-status-label").textContent = done ? "Complete" : "In progress";
  }

  function persist() {
    TaskStore.update(id, {
      title: document.getElementById("detail-title-input").value.trim() || task.title,
      priority: document.getElementById("detail-priority").value,
      dueDate: document.getElementById("detail-due").value,
      notes: document.getElementById("detail-notes").value,
      done: document.getElementById("detail-status-checkbox").checked
    });
    document.getElementById("detail-title").textContent =
      document.getElementById("detail-title-input").value.trim() || task.title;
    const hint = document.getElementById("save-hint");
    hint.classList.add("show");
    setTimeout(() => hint.classList.remove("show"), 1200);
  }

  document.getElementById("detail-status-checkbox").addEventListener("change", e => {
    updateStatusLabel(e.target.checked);
    persist();
  });

  ["detail-title-input", "detail-priority", "detail-due", "detail-notes"].forEach(fieldId => {
    document.getElementById(fieldId).addEventListener("change", persist);
  });

  document.getElementById("delete-task").addEventListener("click", () => {
    if (confirm("Delete this task? This can't be undone.")) {
      TaskStore.remove(id);
      window.location.href = "dashboard.html";
    }
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
