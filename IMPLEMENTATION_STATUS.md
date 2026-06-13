# Bonnibel — status implementacji względem dokumentacji

Porównanie z `Full documentation-2.pdf` (System zarządzania postępem prac zespołu Bonnibel).
Stan po scaleniu modułów + domknięciu braków na branchu `feat/analitics-chat`.

Legenda: ✅ działa · ◐ częściowo · ✗ brak

## Zarządzanie kontem
| Funkcja | Status | Endpoint |
|---|---|---|
| Rejestracja / login / refresh | ✅ | `POST /api/auth/{register,login,refresh}` |
| Get / update user / update status | ✅ | `GET/PUT /api/users/{id}[/profile,/status]` |
| Logout | ✅ | po stronie klienta (usunięcie tokenu) — zgodnie z dokumentacją |

## Projekty i członkowie (Owner)
| Funkcja | Status | Endpoint |
|---|---|---|
| create / delete / my projects / update | ✅ | `/api/project*` (moduł logic) |
| connect Git / Jira / Confluence | ✅ | `POST /api/project/{id}/integrations` |
| add / change role / remove / get members | ✅ | `/api/project/{id}/members*` |

## Zadania, review, analityka
| Funkcja | Status | Endpoint |
|---|---|---|
| create / get / list / update status / assign / assign reviewer / request-close | ✅ | `/api/projects/{pid}/tasks*` |
| task count / per status / per user / get user tasks | ✅ | `GET /api/projects/{pid}/analytics/overview` + filtry `?assigneeId` |
| **get task history** | ✅ (dodane) | `GET /api/projects/{pid}/tasks/{tid}/history` |

## Komunikacja i powiadomienia
| Funkcja | Status | Endpoint |
|---|---|---|
| chat: get / send (+WS) | ✅ | `/api/projects/{pid}/tasks/{tid}/messages`, `WS /api/ws/tasks/{tid}/chat` |
| notifications: get / unread / mark read / read-all (+WS) | ✅ | `/api/notifications*`, `WS /api/ws/notifications` |
| **subscribe / unsubscribe / get subscriptions** | ✅ (dodane) | `GET/POST/DELETE /api/tasks[/{tid}]/subscribe[s]` |

## Domknięte braki (ten etap)
| Obszar | Status | Co dodano |
|---|---|---|
| **TaskHistory** | ✅ | `app/modules/task_history/` + zapis zdarzeń (CREATED/STATUS_CHANGED/UPDATED) w `tasks_and_users/service.py` |
| **Docs** | ✅ | `app/modules/docs/` — add/get docs (zapis do tabeli `docs`), best-effort Confluence |
| **PullRequest** | ✅ | `app/modules/pull_requests/` — create/list/approve/decline, zmiana statusu zadania, powiadomienia PR_CREATED/PR_REVIEWED |
| **Integration (klienci)** | ◐ | Klienci Git/Jira/Confluence podpięci przez `integration/gateway.py` (branch przy assign, PR create/merge, Jira transition, Confluence docs) — **best-effort/guarded**: bez aktywnej integracji lub przy błędzie HTTP zapis idzie lokalnie |
| **Hook Auth + webhooki** | ✅ | `app/modules/hook_auth/` — `SignatureVerifier`(Git/Jira HMAC) + `Factory` + `SecretRepository` + `HookAuthService`; `POST /api/hooks/{provider}/{project_id}` weryfikuje podpis i przetwarza zdarzenie |
| **Online presence** | ✅ | `User.is_online` aktualizowane przy connect/disconnect WS powiadomień |

## Znane ograniczenia / poza zakresem
- **Integracje zewnętrzne** wołane są best-effort — realne operacje na GitHub/Jira/Confluence wymagają prawdziwych tokenów; z danymi demo (token testowy) wywołania są pomijane, a rekordy powstają lokalnie.
- **Frontend** dla nowych endpointów (docs, PR, historia, subskrypcje) nie był budowany — testowanie przez Swagger `/api/docs` lub `curl`. Istniejące widoki (projekty, zadania, czat, powiadomienia, analityka) działają jak wcześniej.
- **`request_close`/CLOSED**: kod ustawia status `"CLOSED"`, którego nie ma w enumie DB `taskstatus` (TODO/IN_PROGRESS/IN_REVIEW/DONE) — istniejący, wcześniejszy potencjalny błąd; nie ruszany w tym etapie.
- `app/modules/integration/tests/test_git_client.py::test_create_branch_failure` — wcześniej istniejący defekt testu (źle skonfigurowany `Mock`), nie związany ze scaleniem.

## Dane testowe
`bonnibel-backend/scripts/seed_demo.py` — idempotentny seed wypełniający wszystkie tabele.
Uruchomienie: `cd bonnibel-backend && ./venv/bin/python scripts/seed_demo.py`.
Login (hasło `password123`): `owner@bonnibel.dev` (Owner), `dev@bonnibel.dev` (Developer), `reviewer@bonnibel.dev` (Reviewer), `dev2@bonnibel.dev`.
