# Notifications Module

Real-time notification and task chat system. The backend (`bonnibel-backend/app/modules/notification/`) is fully implemented; the frontend (`NotificationsPage.tsx`) is a TODO stub.

---

## What it does

- Delivers **in-app notifications** when tasks are assigned/updated, PRs are created/reviewed, or chat messages are sent.
- Pushes events to connected clients instantly via **WebSocket**; falls back to persisting in the DB for users who are offline (retrieved on next load).
- Provides **per-task chat** — a message thread scoped to a single task.
- Tracks **task subscriptions** — users can subscribe to any task to receive its events.

---

## Notification types

| Type | Who receives it |
|------|----------------|
| `TASK_ASSIGNED` | Assignee + reviewer |
| `TASK_UPDATED` | Assignee + reviewer + owner + all subscribers |
| `PR_CREATED` | Reviewer + owner |
| `PR_REVIEWED` | Assignee + owner |
| `CHAT_MESSAGE` | All task subscribers |

The actor who triggered the event is always excluded from recipients.

---

## Architecture

### Backend layers

```
ws.py          — WebSocket endpoint (/ws/notifications?token=<jwt>)
router.py      — REST endpoints (notifications, subscriptions, chat, events)
manager.py     — ConnectionManager + RecipientResolver + NotificationService
models.py      — SQLAlchemy models (4 tables)
schemas.py     — Pydantic request/response schemas
```

### Data flow

1. Something happens in the app (task status change, PR opened, chat message sent).
2. The responsible service posts to `POST /notifications/events` with a `NotificationEventCreate` payload.
3. `RecipientResolver` figures out who to notify by combining explicit `recipient_ids` from the payload with role-based lookups against `TaskRecipientSnapshot`.
4. `NotificationService.create_from_event` persists a `Notification` row per recipient, then attempts live delivery via `ConnectionManager.send_to_user`.
5. If the user has an open WebSocket connection, the event is pushed immediately and `is_delivered` is set to `true`. If not, the notification waits in the DB.

### TaskRecipientSnapshot

Because the notification module has no direct dependency on the `logic` module, it maintains its own lightweight copy of task context (`task_recipient_snapshots` table: `task_id`, `project_id`, `owner_id`, `assignee_id`, `reviewer_id`, `title`). The `logic` module must call `upsert_task_snapshot` whenever a task's roles change.

### ConnectionManager

Holds a `dict[user_id → set[WebSocket]]` in memory — one user can have multiple open tabs. On disconnect the socket is pruned automatically.

---

## WebSocket

**Endpoint:** `ws://localhost:3001/ws/notifications?token=<access_token>`

Authenticate by passing the JWT as a query param (`token`). A fallback `userId` query param exists for development only.

On connect the server sends:
```json
{ "event": "connected", "data": { "userId": "..." } }
```

Subsequent server-pushed events:
```json
{ "event": "notification_created", "data": { ...NotificationRead } }
{ "event": "chat_message_created", "data": { ...ChatMessageRead } }
```

The client does not need to send any messages; the connection is receive-only.

---

## REST API

All endpoints require a Bearer token (`Authorization: Bearer <access_token>`).

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/notifications` | List notifications (`?unread=true`, `?limit=`, `?offset=`) |
| `GET` | `/notifications/unread-count` | `{ unreadCount: number }` |
| `PATCH` | `/notifications/{id}/read` | Mark single notification read |
| `PATCH` | `/notifications/read-all` | Mark all read |
| `POST` | `/notifications/events` | Fire a notification event (used internally by other modules) |

### Task chat

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks/{task_id}/messages` | Paginated chat history (`?limit=`, `?beforeId=`) |
| `POST` | `/tasks/{task_id}/messages` | Send a message; auto-subscribes sender |

### Subscriptions

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks/subscriptions` | All tasks the current user subscribes to |
| `POST` | `/tasks/{task_id}/subscribe` | Subscribe |
| `DELETE` | `/tasks/{task_id}/subscribe` | Unsubscribe |

---

## Database tables

| Table | Purpose |
|-------|---------|
| `notifications` | One row per recipient per event. Tracks `is_read` and `is_delivered`. |
| `task_subscriptions` | Composite PK `(task_id, user_id)`. Assignee/reviewer are auto-subscribed on snapshot upsert. |
| `chat_messages` | Per-task message thread. Keyed by `message_id` for cursor-based pagination (`beforeId`). |
| `task_recipient_snapshots` | Denormalised task context owned by the notification module. |

---

## What the frontend needs to implement

`NotificationsPage.tsx` is a placeholder. It should:

1. Open a WebSocket connection on mount (authenticated via `?token=<accessToken>`).
2. Maintain a local notifications list, seeded by `GET /notifications` and updated in real-time via `notification_created` events.
3. Show unread count in the header/sidebar badge (`GET /notifications/unread-count`).
4. Allow marking individual or all notifications read.
5. Navigate to `notification.linkUrl` on click.

Task chat belongs in the individual task view (not this page), and should use the `chat_message_created` WebSocket event together with the `GET /tasks/{task_id}/messages` REST endpoint.
