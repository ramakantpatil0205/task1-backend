import pytest
from app import app, db, Task, Comment
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # use in-memory sqlite for tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_task_comment_flow(client):
    # create a task
    rv = client.post("/tasks", json={"title":"Test Task", "description":"desc"})
    assert rv.status_code == 201
    task = rv.get_json()
    task_id = task["id"]

    # add a comment
    rv = client.post("/comments", json={"task_id": task_id, "body":"First comment", "author":"tester"})
    assert rv.status_code == 201
    comment = rv.get_json()
    assert comment["body"] == "First comment"

    # list comments
    rv = client.get(f"/comments/{task_id}")
    assert rv.status_code == 200
    comments = rv.get_json()
    assert len(comments) == 1

    # update comment
    cid = comment["id"]
    rv = client.put(f"/comments/{cid}", json={"body":"Updated"})
    assert rv.status_code == 200
    updated = rv.get_json()
    assert updated["body"] == "Updated"

    # delete comment
    rv = client.delete(f"/comments/{cid}")
    assert rv.status_code == 200

    # ensure deleted
    rv = client.get(f"/comments/{task_id}")
    comments = rv.get_json()
    assert len(comments) == 0