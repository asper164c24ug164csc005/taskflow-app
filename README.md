# TaskFlow – Week 3 Back-End API Development

A RESTful back-end API for the TaskFlow web application, built with Python Flask and SQLite.

## Features
- User registration and login
- JWT-based authentication
- Password hashing
- CRUD operations for tasks
- SQLite database
- Input validation
- Error handling
- CORS support for front-end integration
- Pytest API tests
- Clear API documentation

## Project Structure
```text
Week3_TaskFlow_Backend/
├── app.py
├── requirements.txt
├── README.md
└── tests/
    └── test_api.py
```

## Setup
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run:
   `python app.py`
5. API base URL:
   `http://127.0.0.1:5000`

## API Documentation

### Health
`GET /api/health`

Response:
```json
{"status":"success","message":"TaskFlow API is running"}
```

### Register
`POST /api/auth/register`

Body:
```json
{"name":"Dharshini","email":"dharshini@example.com","password":"secret123"}
```

### Login
`POST /api/auth/login`

Body:
```json
{"email":"dharshini@example.com","password":"secret123"}
```

The response contains an `access_token`. Send it for protected endpoints using:
`Authorization: Bearer <token>`

### Create Task
`POST /api/tasks`

Body:
```json
{
  "title":"Complete Week 3",
  "description":"Build REST API",
  "status":"pending",
  "priority":"high"
}
```

### Get All Tasks
`GET /api/tasks`

### Get One Task
`GET /api/tasks/<task_id>`

### Update Task
`PUT /api/tasks/<task_id>`

Body can contain `title`, `description`, `status`, or `priority`.

### Delete Task
`DELETE /api/tasks/<task_id>`

## Validation
- Name, email and password are required during registration.
- Password must contain at least 6 characters.
- Email must have a valid basic format.
- Task title is required.
- Status: `pending`, `in-progress`, `completed`.
- Priority: `low`, `medium`, `high`.

## Testing
Run:
```bash
pytest -q
```

## Security Notes
Passwords are stored as hashes, not plain text. JWT authentication protects task endpoints and each user can access only their own tasks. For deployment, store the JWT secret in an environment variable and disable Flask debug mode.
