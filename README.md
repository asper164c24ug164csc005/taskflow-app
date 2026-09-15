# TaskFlow — Front-End Application (Week 2)

TaskFlow is a small, fully client-side task management app built as the Week 2
front-end deliverable. It has three connected views — a landing page, a task
dashboard, and a task detail page — and stores data in the browser using
`localStorage`, so it works fully offline with no back end.

## Tech stack

- **HTML5 / CSS3** — semantic markup, custom properties for the design system, flexbox and CSS grid for layout, responsive down to mobile.
- **Vanilla JavaScript (ES6+)** — no framework. Chosen deliberately to keep the app dependency-free and easy to run locally, and to demonstrate DOM manipulation, event handling, and state persistence without relying on a library.
- **Google Fonts** (Fraunces for display headings, Inter for UI/body text) loaded via CDN.

## Views

1. **Landing page** (`index.html`) — introduces the product and links into the dashboard.
2. **Dashboard** (`dashboard.html`) — lists all tasks with live search, filter chips (All / Open / Done / High priority), summary stat cards, and an inline "Add task" form. Clicking a task title opens its detail view.
3. **Task detail** (`task-detail.html`) — full view of a single task (read from the `?id=` query parameter) with editable title, priority, due date, notes, and a complete/incomplete toggle. Changes autosave on field blur/change. Includes a delete action.

## Design decisions

- **State management**: a single `TaskStore` object in `js/app.js` wraps all reads/writes to `localStorage` under one key (`taskflow.tasks.v1`), so every page reads from and writes to the same source of truth without a server.
- **Navigation**: plain `<a href>` links and query parameters (`task-detail.html?id=...`) keep routing simple and framework-free, while still giving each task its own shareable/bookmarkable URL.
- **Seed data**: on first load, if no tasks exist yet, three example tasks are seeded so the dashboard and detail view aren't empty on a fresh run.
- **Accessibility/responsiveness**: visible focus states, sufficient color contrast, and a mobile breakpoint that collapses the multi-column layouts to a single column.

## Design patterns used

- **Module-style separation**: `TaskStore` (data layer) is kept separate from the page-init functions (`initDashboard`, `initTaskDetail`) that own DOM rendering and event wiring — a lightweight model/view split without needing a framework.
- **Progressive enhancement**: each HTML page is a valid, readable document on its own; JavaScript only adds interactivity on top.

## How to run locally

No build step or server is required.

1. Download/unzip the project folder.
2. Open `index.html` directly in any modern browser (Chrome, Edge, Firefox, Safari) — double-click it, or right-click → Open with → your browser.
3. Click **Open your dashboard** to go to `dashboard.html`, or open it directly.
4. Add a task, click its title to open `task-detail.html`, edit it, and use the checkbox to mark it complete.

Optional (recommended for consistent relative-path behavior): serve the folder
with a simple local server instead of the `file://` protocol, e.g.:

```bash
# from inside the taskflow-app folder
python3 -m http.server 8000
# then visit http://localhost:8000 in your browser
```

## Folder structure

```
taskflow-app/
├── index.html          # Landing page
├── dashboard.html       # Task list / dashboard view
├── task-detail.html     # Single task detail/edit view
├── css/
│   └── style.css        # Shared design system + layout
├── js/
│   └── app.js            # TaskStore + page logic
└── README.md
```
