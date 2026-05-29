# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Bonnibel** is a team progress management system integrating Jira, Git, and documentation for software engineering teams. Monorepo with a React/TypeScript frontend and a Python/FastAPI backend.

## Commands

### Frontend (`bonnibel-frontend/`)

```bash
npm install          # Install dependencies
npm run dev          # Dev server (Vite, http://localhost:5173)
npm run build        # Production build
npm run lint         # ESLint
```

### Backend (`bonnibel-backend/`)

```bash
docker compose up -d              # Start PostgreSQL
pip install -r requirements.txt   # Install dependencies
alembic upgrade head               # Run DB migrations
uvicorn app.main:app --reload --port 3001  # Run dev server (http://localhost:3001)
pytest                             # Run tests
pytest tests/path/to/test.py      # Run single test file
```

### Environment

Frontend reads from `.env` (copy from `.env.example`). Key variables:
- `VITE_API_BASE_URL` — backend URL (default `http://localhost:3001`)
- `VITE_WS_BASE_URL` — WebSocket base URL (if empty, derived from `VITE_API_BASE_URL`)
- `VITE_BYPASS_AUTH=true` — skips login entirely in dev, uses a mock auth state
- `VITE_BYPASS_USER_ID=user-1` — user ID used when `BYPASS_AUTH` is active

## Architecture

### Monorepo Layout

```
bonnibel/
├── bonnibel-frontend/   # React 19 + TypeScript + Vite + Tailwind CSS v4
└── bonnibel-backend/    # Python FastAPI + PostgreSQL + SQLAlchemy
```

### Frontend

**Entry points:** `src/main.tsx` → `src/App.tsx` (wraps `QueryClientProvider` + `RouterProvider`) → `src/router/routes.tsx` (defines protected routes via `ProtectedRoute` component).

**Feature modules** live under `src/modules/`, each with `pages/`, `components/`, `hooks/`, `api/`. Current modules: `auth`, `projects`, `members`, `tasks`, `reviews`, `notifications`, `chat`, `analytics`.

**Shared code:**
- `src/lib/api.ts` — `apiFetch<T>()` wrapper: attaches Bearer token, silently refreshes on 401, redirects on auth failure. **Always use `apiFetch` instead of raw `fetch`.**
- `src/lib/queryClient.ts` — TanStack Query client (30s staleTime, no refetchOnWindowFocus).
- `src/lib/env.ts` — typed access to `VITE_*` env vars; `isUsingFastApiBackend()` returns true when URL contains `:8000` or `VITE_WS_BASE_URL` is set — services use this to switch between FastAPI paths (`/api/...`) and json-server paths.
- `src/store/` — Zustand stores (currently auth). Auth state persisted to `localStorage`.
- `src/services/` — `authService`, `userService`, `taskService`, `chatService`, `analyticsService`.
- `src/types/domain.ts` — all shared domain types and enums.

**Path alias:** `@/` resolves to `src/`.

**API base URL:** `http://localhost:3001` (default, overridden by `VITE_API_BASE_URL`).

### Backend

Layered, domain-driven structure under `app/`:
- `core/` — `config.py` (pydantic-settings), `database.py` (SQLAlchemy session), `security.py` (JWT + bcrypt), `models.py` (all SQLAlchemy ORM models).
- `modules/` — business logic by domain (see below).
- `dependencies/auth.py` — `get_current_user_id()`: extracts user from Bearer token; falls back to `X-User-Id` header for demo/dev use.
- `alembic/` — database migrations.

**Module structure pattern** (follow this when adding new modules):
```
modules/<name>/
├── router.py    # FastAPI router, registered in main.py
├── schemas.py   # Pydantic request/response models
├── service.py   # Business logic, takes db: Session as argument
├── models.py    # SQLAlchemy ORM models (if module owns tables)
└── manager.py   # Stateful singleton services (e.g., ConnectionManager)
```

**Registering a new router:** add `app.include_router(...)` in `app/main.py`. Currently only the `notification` router is registered — auth router is not yet wired up.

**Module status:**
- `notification/` — **fully implemented**: REST endpoints (GET/PATCH notifications, subscriptions, chat), WebSocket endpoint, `ConnectionManager`, `RecipientResolver`, `NotificationService`, demo data seeding on startup.
- `auth/` — **stub**: files exist but are empty; JWT logic lives in `core/security.py` only.
- `logic/`, `integration/`, `hook_auth/` — empty stubs.

### Notification / WebSocket Architecture

- **WS endpoint:** `ws://localhost:3001/ws/notifications?token=<jwt>`
- **ConnectionManager** (`manager.py`): in-memory `dict[user_id → set[WebSocket]]`; pushes to all open connections for a user, persists to DB if offline.
- **Event flow:** domain event → `RecipientResolver` (resolves who to notify) → `NotificationService` (creates DB rows + pushes WS) → client.
- **Notification types:** `TASK_ASSIGNED`, `TASK_UPDATED`, `PR_CREATED`, `PR_REVIEWED`, `CHAT_MESSAGE`.
- **Chat:** per-task messages, cursor pagination with `beforeId`.
- **Fanout table:** `task_recipient_snapshots` stores a denormalized copy of who should receive notifications to avoid circular imports between `notification` and `logic` modules. Call `POST /api/notifications/snapshots` to upsert a snapshot before emitting events.

### Database

All SQLAlchemy ORM models live in `app/core/models.py` (20+ tables). Key tables: `users`, `auth`, `refresh_tokens`, `projects`, `project_members`, `tasks`, `task_subscriptions`, `notifications`, `chat_messages`, `pull_requests`. PostgreSQL runs via Docker Compose.

### Key Domain Types

Defined in `src/types/domain.ts`:
- Enums: `ProjectRole`, `UserStatus`, `TaskStatus`, `PullRequestStatus`, `IntegrationProvider`, `NotificationType`, `TaskEventType`
- Interfaces: `User`, `Task`, `TaskDoc`, `TaskHistory`, `AuthResponse`, `AuthTokens`, `ChatMessage`

## Implementation Status

**Frontend — implemented:** auth flow (login, signup, token refresh), `AppLayout`/`AuthLayout`, routing guards, `TaskDetailsPage`, `TaskChat` (WebSocket + cursor pagination), `ProfilePage`, `AnalyticsPage` (task counts, by status, by assignee, commits).

**Frontend — TODO stubs (8-line placeholder pages):** `NotificationsPage`, `ProjectsListPage`, `ProjectDetailsPage`, `ProjectIntegrationsPage`, `MembersPage`, `ReviewsPage`. `TasksListPage` and `MyTasksPage` also need full implementation.

**Backend — implemented:** `notification` module (REST + WebSocket + fanout), JWT security (`core/security.py`), all DB models, Docker Compose for PostgreSQL.

**Backend — TODO:** `auth` module router (register/login endpoints), `logic` module (ProjectService, TaskService, etc.), `integration` module (Jira/Git clients), `hook_auth` (HMAC webhook verification).
