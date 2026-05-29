# Notification Module

Real-time notification and task chat system. Handles WebSocket connections, event-driven notification fanout, per-task chat, and task subscriptions.

---

## What it does

- Delivers **in-app notifications** when tasks are assigned/updated, PRs are created/reviewed, or chat messages are sent.
- Pushes events instantly to connected clients via **WebSocket**; persists them in the DB for users who are offline.
- Provides **per-task chat** — a message thread scoped to a single task.
- Tracks **task subscriptions** — users auto-subscribe on assignment and can subscribe/unsubscribe manually.

---

## File overview

| File | Responsibility |
|------|---------------|
| `models.py` | SQLAlchemy ORM models (4 tables) |
| `schemas.py` | Pydantic request/response schemas |
| `manager.py` | `ConnectionManager`, `RecipientResolver`, `NotificationService` |
| `router.py` | REST endpoints (notifications, chat, subscriptions, events) |
| `ws.py` | WebSocket endpoint |

---

## Data flow

1. An event occurs elsewhere in the app (task assigned, PR opened, chat message sent).
2. The responsible service calls `notification_service.create_from_event(db, event)` or posts to `POST /notifications/events`.
3. `RecipientResolver.resolve()` combines explicit `recipient_ids` from the event with role-based lookups from `TaskRecipientSnapshot` (see below).
4. A `Notification` row is persisted per recipient.
5. `ConnectionManager.send_to_user()` attempts live delivery over WebSocket. If the user is connected, `is_delivered` is set to `True`; if not, the row waits in the DB to be fetched on next load.

---

## Notification types and recipients

Defined in `models.py` as `NotificationType` (`StrEnum`):

| Type | Auto-recipients |
|------|----------------|
| `TASK_ASSIGNED` | Assignee + reviewer |
| `TASK_UPDATED` | Assignee + reviewer + owner + all subscribers |
| `PR_CREATED` | Reviewer + owner |
| `PR_REVIEWED` | Assignee + owner |
| `CHAT_MESSAGE` | All task subscribers |

The actor (`actor_id`) is always removed from the recipient set.

---

## Key classes (`manager.py`)

### `ConnectionManager`

In-memory `dict[user_id → set[WebSocket]]`. One user can hold multiple sockets (multiple tabs). Sockets are pruned automatically on `RuntimeError` during send. A singleton `connection_manager` is exported and shared with `ws.py`.

### `RecipientResolver`

Stateless helper that takes a `NotificationEventCreate` and returns a `set[str]` of user IDs to notify. Falls back to `TaskRecipientSnapshot` when role IDs are not provided in the event payload.

### `NotificationService`

The main service object. Injected with `ConnectionManager` and `RecipientResolver`. Provides:
- `create_from_event` — full fanout pipeline
- `list_notifications`, `unread_count`, `mark_read`, `mark_all_read`
- `subscribe`, `unsubscribe`, `list_subscriptions`
- `list_messages`, `send_message` (chat)
- `upsert_task_snapshot` — called by the `logic` module whenever task roles change

A singleton `notification_service` is exported from `manager.py` for use in routers.

---

## TaskRecipientSnapshot

The notification module deliberately has no import dependency on the `logic` module. Instead it maintains a lightweight denormalised copy of task context (`task_recipient_snapshots` table: `task_id`, `project_id`, `owner_id`, `assignee_id`, `reviewer_id`, `title`).

The `logic` module **must** call `notification_service.upsert_task_snapshot(...)` whenever a task is created or its roles/project change. Assignee and reviewer are auto-subscribed as a side effect of upsert.

---

## Database tables

| Table | Key columns | Notes |
|-------|-------------|-------|
| `notifications` | `notification_id`, `user_id`, `type`, `is_read`, `is_delivered` | One row per recipient per event |
| `task_subscriptions` | `(task_id, user_id)` composite PK | Auto-populated for assignee/reviewer on snapshot upsert |
| `chat_messages` | `message_id`, `task_id`, `author_id`, `text` | Cursor-based pagination via `before_id` |
| `task_recipient_snapshots` | `task_id` PK, `owner_id`, `assignee_id`, `reviewer_id` | Owned by this module; updated by `logic` |

---

## WebSocket (`ws.py`)

**Endpoint:** `ws://<host>/ws/notifications`

Authenticate via query param: `?token=<access_token>` (JWT decoded by `decode_access_token`). A plain `?userId=` fallback exists for development.

On connect the server sends:
```json
{ "event": "connected", "data": { "userId": "..." } }
```

Server-pushed events during the session:
```json
{ "event": "notification_created", "data": { ...NotificationRead } }
{ "event": "chat_message_created", "data": { ...ChatMessageRead } }
```

The client does not need to send messages; the loop only calls `receive_text()` to detect disconnection.

---

## REST endpoints (`router.py`)

All require `Authorization: Bearer <token>`.

### Notifications
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/notifications` | List (`?unread=true`, `?limit`, `?offset`) |
| `GET` | `/notifications/unread-count` | `{ unreadCount }` |
| `PATCH` | `/notifications/{id}/read` | Mark single read |
| `PATCH` | `/notifications/read-all` | Mark all read |
| `POST` | `/notifications/events` | Fire an event (internal use by other modules) |

### Task chat
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks/{task_id}/messages` | History (`?limit`, `?beforeId` for cursor pagination) |
| `POST` | `/tasks/{task_id}/messages` | Send message; auto-subscribes sender |

### Subscriptions
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks/subscriptions` | All tasks the current user watches |
| `POST` | `/tasks/{task_id}/subscribe` | Subscribe |
| `DELETE` | `/tasks/{task_id}/subscribe` | Unsubscribe |

### Demo / dev helpers
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notifications/demo/task-snapshots` | Upsert a task snapshot manually |
| `POST` | `/notifications/demo/seed` | Seed demo notifications, messages, and snapshots |
