# TaskFlow – Full Stack Task Management App

TaskFlow lets users create, view, update and delete tasks. The React front-end talks to a Flask REST API, which stores data in SQLite.

## Tech Stack
- Front-end: React (Vite), Axios
- Back-end: Python Flask, Flask-CORS, Flask-SQLAlchemy
- Database: SQLite

## Project Structure
```
taskflow-app/
├── backend/   (app.py, models.py, requirements.txt)
└── frontend/  (src/, package.json, .env)
```

## Setup and Run Locally

### 1. Back-end
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
API runs at http://localhost:5000

### 2. Front-end (new terminal)
```bash
cd frontend
npm install
```
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:5000/api
```
```bash
npm run dev
```
App runs at http://localhost:5173

## API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/tasks | Get all tasks |
| GET | /api/tasks/<id> | Get one task |
| POST | /api/tasks | Create task |
| PUT | /api/tasks/<id> | Update task |
| DELETE | /api/tasks/<id> | Delete task |

## Integration Process
1. Reviewed the front-end components and back-end routes to match integration points.
2. Enabled CORS in Flask so the React app can call the API.
3. Created a service layer (`api.js`) with Axios and a base URL from `.env`.
4. Used `async/await` with `useEffect` to load tasks, and `useState` for tasks, loading and error state.
5. Connected the add, edit and delete actions to the API and updated state from the response.
6. Added try/catch and user-friendly error messages.
7. Tested all endpoints in Postman and then from the UI.

## Validation Rules
- Title: required, 3–100 characters
- Description: max 500 characters
- Status: todo / in_progress / done
- Priority: low / medium / high
- Due date: YYYY-MM-DD

## Challenges and Solutions
| Challenge | Solution |
|---|---|
| CORS error | Enabled Flask-CORS |
| UI not updating after add/delete | Updated state from API response |
| Hard-coded API URL | Moved to `.env` variable |
| Blank screen on API failure | Added error handling and error state |

## Demo
Demo video / deployed link: _add your link here_
