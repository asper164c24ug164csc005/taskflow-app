from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskflow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "change-this-secret-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), default="")
    status = db.Column(db.String(30), default="pending")
    priority = db.Column(db.String(20), default="medium")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id
        }

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "success", "message": "TaskFlow API is running"}), 200

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if "@" not in email:
        return jsonify({"error": "Enter a valid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must contain at least 6 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_id": user.id}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }), 200

def current_user_id():
    return int(get_jwt_identity())

@app.route("/api/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user_id()).order_by(Task.id.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user_id()).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict()), 200

@app.route("/api/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    status = str(data.get("status", "pending")).lower()
    priority = str(data.get("priority", "medium")).lower()

    if not title:
        return jsonify({"error": "Task title is required"}), 400
    if status not in {"pending", "in-progress", "completed"}:
        return jsonify({"error": "Invalid status"}), 400
    if priority not in {"low", "medium", "high"}:
        return jsonify({"error": "Invalid priority"}), 400

    task = Task(
        title=title[:150],
        description=description[:500],
        status=status,
        priority=priority,
        user_id=current_user_id()
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user_id()).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return jsonify({"error": "Task title cannot be empty"}), 400
        task.title = title[:150]
    if "description" in data:
        task.description = str(data["description"])[:500]
    if "status" in data:
        status = str(data["status"]).lower()
        if status not in {"pending", "in-progress", "completed"}:
            return jsonify({"error": "Invalid status"}), 400
        task.status = status
    if "priority" in data:
        priority = str(data["priority"]).lower()
        if priority not in {"low", "medium", "high"}:
            return jsonify({"error": "Invalid priority"}), 400
        task.priority = priority

    db.session.commit()
    return jsonify(task.to_dict()), 200

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user_id()).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(_):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
