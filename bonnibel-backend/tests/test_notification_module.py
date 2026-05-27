import pytest

from conftest import auth
from app.modules.notification.manager import connection_manager


pytestmark = pytest.mark.anyio


async def test_subscribe_and_resolve_task_updated_event(client):
    response = await client.post("/tasks/102/subscribe", headers=auth("user-3"))
    assert response.status_code == 201
    assert response.json()["taskId"] == 102

    response = await client.get("/notifications/unread-count", headers=auth("user-2"))
    assert response.status_code == 200
    initial_unread_count = response.json()["unreadCount"]

    response = await client.post(
        "/notifications/events",
        headers=auth("user-1"),
        json={
            "type": "TASK_UPDATED",
            "taskId": 102,
            "projectId": 1,
            "title": "Zmieniono status zadania",
            "message": "Zadanie BON-102 przeszło do review",
        },
    )

    assert response.status_code == 201
    recipients = {item["userId"] for item in response.json()}
    assert recipients == {"user-2", "user-3"}

    response = await client.get("/notifications/unread-count", headers=auth("user-2"))
    assert response.status_code == 200
    assert response.json() == {"unreadCount": initial_unread_count + 1}


async def test_chat_message_auto_subscribes_author_and_notifies_subscribers(client):
    response = await client.post("/tasks/101/subscribe", headers=auth("user-2"))
    assert response.status_code == 201

    response = await client.post(
        "/tasks/101/messages",
        headers=auth("user-3"),
        json={"text": "Gotowe do sprawdzenia."},
    )
    assert response.status_code == 201
    assert response.json()["authorId"] == "user-3"

    response = await client.get("/tasks/subscriptions", headers=auth("user-3"))
    assert response.status_code == 200
    assert any(item["taskId"] == 101 for item in response.json())

    response = await client.get("/notifications", headers=auth("user-2"))
    assert response.status_code == 200
    notifications = response.json()
    assert any(item["type"] == "CHAT_MESSAGE" for item in notifications)


async def test_seeded_demo_data_is_available_from_get_endpoints(client):
    response = await client.post("/notifications/demo/seed", headers=auth("user-1"))
    assert response.status_code == 200
    assert response.json() == {"status": "demo data ready"}

    response = await client.get("/notifications", headers=auth("user-3"))
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) >= 2
    assert {"TASK_ASSIGNED", "TASK_UPDATED"} <= {item["type"] for item in notifications}

    response = await client.get("/tasks/101/messages", headers=auth("user-1"))
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) >= 2
    assert messages[0]["text"] == "Boilerplate jest gotowy, proszę o review."

    response = await client.get("/tasks/subscriptions", headers=auth("user-2"))
    assert response.status_code == 200
    assert any(item["taskId"] == 101 for item in response.json())


async def test_mark_notification_read(client):
    response = await client.post(
        "/notifications/events",
        headers=auth("user-1"),
        json={
            "type": "PR_REVIEWED",
            "taskId": 102,
            "projectId": 1,
            "assigneeId": "user-2",
            "ownerId": "user-1",
            "title": "Review zakończone",
        },
    )
    assert response.status_code == 201
    notification_id = response.json()[0]["notificationId"]

    response = await client.patch(f"/notifications/{notification_id}/read", headers=auth("user-2"))
    assert response.status_code == 200
    assert response.json()["isRead"] is True


class DummyWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, payload):
        self.sent.append(payload)


async def test_online_user_receives_created_notification(client):
    websocket = DummyWebSocket()
    await connection_manager.connect("user-2", websocket)

    try:
        response = await client.post(
            "/notifications/events",
            headers=auth("user-1"),
            json={
                "type": "TASK_ASSIGNED",
                "taskId": 105,
                "projectId": 1,
                "assigneeId": "user-2",
                "reviewerId": "user-1",
                "title": "Przypisano nowe zadanie",
            },
        )
        assert response.status_code == 201
        assert websocket.accepted is True
        assert websocket.sent[-1]["event"] == "notification_created"
        assert websocket.sent[-1]["data"]["userId"] == "user-2"
        assert websocket.sent[-1]["data"]["type"] == "TASK_ASSIGNED"
    finally:
        connection_manager.disconnect("user-2", websocket)
