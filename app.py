from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
db_path = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship("Comment", backref="task", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "created_at": self.created_at.isoformat()}

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(120), default="anonymous")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "task_id": self.task_id, "body": self.body, "author": self.author, "created_at": self.created_at.isoformat(), "updated_at": self.updated_at.isoformat()}

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error":"title is required"}), 400
    task = Task(title=title, description=data.get("description",""))
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.route("/tasks", methods=["GET"])
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json() or {}
    title = data.get("title")
    if title:
        task.title = title
    if "description" in data:
        task.description = data.get("description","")
    db.session.commit()
    return jsonify(task.to_dict()), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message":"deleted"}), 200

# Comments CRUD
@app.route("/comments", methods=["POST"])
def add_comment():
    data = request.get_json() or {}
    task_id = data.get("task_id")
    body = data.get("body")
    author = data.get("author","anonymous")
    if not task_id or not body:
        return jsonify({"error":"task_id and body are required"}), 400
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error":"task not found"}), 404
    comment = Comment(task_id=task_id, body=body, author=author)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201

@app.route("/comments/<int:task_id>", methods=["GET"])
def get_comments_for_task(task_id):
    task = Task.query.get_or_404(task_id)
    comments = Comment.query.filter_by(task_id=task.id).order_by(Comment.created_at.asc()).all()
    return jsonify([c.to_dict() for c in comments]), 200

@app.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json() or {}
    if "body" in data:
        comment.body = data.get("body")
    if "author" in data:
        comment.author = data.get("author")
    db.session.commit()
    return jsonify(comment.to_dict()), 200

@app.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message":"deleted"}), 200

if __name__ == "__main__":
    # create tables if not present (for demo)
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)