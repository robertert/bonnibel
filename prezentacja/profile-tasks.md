# Moduł: profile-tasks (Profil użytkownika + Zadania)

**Co pokazuje** (dok.: *Zarządzanie kontem* — profil; *Zarządzanie zadaniami i analityka* — zadania):
- Profil: pobranie/edycja danych, zmiana **statusu dostępności** (ACTIVE/INACTIVE/BANNED).
- Zadania: utworzenie, lista (z filtrami), szczegóły, zmiana statusu, przypisanie wykonawcy, przypisanie recenzenta, zgłoszenie zamknięcia.
- **Historia zadania** (oś czasu zdarzeń).

**Wymagania wstępne:** zalogowany user; projekt (z `projects-members`). Dla realnej gałęzi na GitHubie — podłączona integracja GitHub (z `integrations`).

## Kroki w UI
1. **Profil** (`/profile`): pokaż dane; zmień status dostępności (np. INACTIVE) i zapisz.
2. **Zadania** projektu (`/projects/{id}/tasks`): utwórz zadanie (tytuł, opis).
3. Wejdź w zadanie → **przypisz wykonawcę** z listy. ⇒ jeśli GitHub podłączony, na repo pojawia się **gałąź `bon-{taskId}-{user}` z commitem** (patrz `integrations.md`); status zmienia ticket Jira (jeśli podłączona).
4. **Przypisz recenzenta** (np. `reviewer@`/user-3) — potrzebny do modułu `pr-docs`.
5. Zmień **status** zadania (TODO → IN_PROGRESS → … → DONE/CLOSED).
6. Na dole zadania: panel **Historia** — pokaż zdarzenia (utworzono, przypisano, zmiana statusu, PR).
7. „Moje zadania" (`/my-tasks`) — lista przypisanych.

## Backup: curl
```bash
# profil / status
curl -s localhost:8000/api/users/user-1
curl -s -X PUT localhost:8000/api/users/user-1/status -H 'Content-Type: application/json' -d '{"status":"INACTIVE"}'

# zadania
curl -s -X POST localhost:8000/api/projects/1/tasks -H 'Content-Type: application/json' \
  -d '{"title":"Nowe zadanie","description":"opis","assigneeId":null,"reviewerId":null}'
curl -s -X PATCH localhost:8000/api/projects/1/tasks/104/assign  -H 'Content-Type: application/json' -d '{"assigneeId":"user-2"}'
curl -s -X PATCH localhost:8000/api/projects/1/tasks/104/reviewer -H 'Content-Type: application/json' -d '{"reviewerId":"user-3"}'
curl -s -X PATCH localhost:8000/api/projects/1/tasks/104/status   -H 'Content-Type: application/json' -d '{"status":"IN_PROGRESS"}'
curl -s        localhost:8000/api/projects/1/tasks/104/history
```

## Talking points
- Przy tworzeniu zadania nadawany jest `jira_issue_key` = `BON-{id}` (powiązanie z Jira).
- **Przypisanie wykonawcy** to wyzwalacz tworzenia gałęzi na GitHubie (best-effort) — łączy moduły tasks ↔ integrations.
- Każda istotna zmiana (utworzenie, status, przypisanie, PR) zapisuje wpis do **TaskHistory** (aktor wynikany z kontekstu zadania, bo endpointy zadań są bez auth).
- Status `CLOSED` dostępny (dodany do enuma) — `request-close` realnie zamyka zadanie.
