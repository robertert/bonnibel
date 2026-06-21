# Moduł: pr-docs (Pull Requesty + Dokumentacja + Reviews)

**Co pokazuje** (dok.: *Zarządzanie zadaniami i review* + *Dokumentacja*):
- Docs: dodanie, edycja i podgląd dokumentacji przypiętej do zadania.
- PR: utworzenie pull requesta dopiero po dodaniu dokumentacji.
- Reviews: lista otwartych PR-ów widocznych dla użytkownika zgodnie z jego rolą w projekcie.
- Decyzja review: akceptacja (`MERGED`) albo odrzucenie (`CLOSED`) z powodem.

**Integracje:** część PR korzysta z realnego modułu `integration` w trybie best-effort. Jeśli projekt ma aktywny GitHub, utworzenie PR próbuje stworzyć prawdziwy Pull Request w repozytorium, a approve próbuje wykonać merge i usunąć gałąź. Część docs nie tworzy strony w Confluence: użytkownik sam przygotowuje dokumentację po swojej stronie i w Bonnibel zapisuje obowiązkowe `title + url`.

**Wymagania wstępne:** istniejący projekt, zadanie z przypisanym wykonawcą i recenzentem. Dokumentacja musi być dodana przed utworzeniem PR.

## Kroki w UI
1. Wejdź w zadanie -> panel **Dokumentacja i Pull Request**.
2. Dodaj dokumentację: tytuł + poprawny URL zaczynający się od `http://` albo `https://`.
   - Użytkownik sam tworzy dokumentację poza Bonnibel, np. w Confluence, Google Docs albo repo.
   - Bonnibel zapisuje tylko nazwę i link do tej dokumentacji.
   - Formularz blokuje zapis dla pustego albo niepoprawnego URL.
   - Po dodaniu dokumentacji można ją edytować.
3. Kliknij **Utwórz Pull Request**.
   - Backend wymaga istniejącej dokumentacji (`TASK_DOCS_REQUIRED` bez docs).
   - Backend próbuje utworzyć realny PR przez GitHub integration; przy braku integracji zapisuje lokalny PR ze statusem `OPEN`.
   - Dla zadania może istnieć tylko jeden PR (`PULL_REQUEST_ALREADY_EXISTS` przy duplikacie).
4. Wejdź w **Reviews** (`/reviews`).
   - Widok pobiera otwarte PR-y przez endpoint użytkownika z trybem `reviews`.
   - Owner widzi PR-y projektów, reviewer widzi swoje review, developer widzi PR-y swoich zadań.
5. W **Reviews**:
   - **Approve** próbuje zrobić merge na GitHubie, ustawia PR jako `MERGED`, a zadanie jako `DONE`.
   - **Reject** wymaga powodu, ustawia PR jako `CLOSED`, a zadanie wraca do `IN_PROGRESS`.

## Backup: curl
```bash
# docs: dodanie / pobranie / edycja
curl -s -X POST localhost:8000/api/projects/1/tasks/104/docs \
  -H 'Content-Type: application/json' \
  -d '{"title":"Kontrakt API","url":"https://example.com/docs/api"}'

curl -s localhost:8000/api/projects/1/tasks/104/docs

curl -s -X PUT localhost:8000/api/projects/1/tasks/104/docs \
  -H 'Content-Type: application/json' \
  -d '{"title":"Kontrakt API v2","url":"https://example.com/docs/api-v2"}'

# PR: utworzenie / lista w projekcie / lista do review
curl -s -X POST localhost:8000/api/projects/1/tasks/104/pull-requests

curl -s localhost:8000/api/projects/1/pull-requests

curl -s "localhost:8000/api/users/user-3/pull-requests?mode=reviews&status=OPEN"

# decyzja review
curl -s -X POST localhost:8000/api/projects/1/pull-requests/PR_ID/accept

curl -s -X POST localhost:8000/api/projects/1/pull-requests/PR_ID/reject \
  -H 'Content-Type: application/json' \
  -d '{"reason":"Needs changes"}'
```

## Endpointy używane przez frontend
- `GET /api/projects/{projectId}/tasks/{taskId}/docs`
- `POST /api/projects/{projectId}/tasks/{taskId}/docs`
- `PUT /api/projects/{projectId}/tasks/{taskId}/docs`
- `GET /api/projects/{projectId}/docs`
- `POST /api/projects/{projectId}/tasks/{taskId}/pull-requests`
- `GET /api/projects/{projectId}/pull-requests`
- `GET /api/users/{userId}/pull-requests?mode=reviews&status=OPEN`
- `POST /api/projects/{projectId}/pull-requests/{pullRequestId}/accept`
- `POST /api/projects/{projectId}/pull-requests/{pullRequestId}/reject`

## Talking points
- Dokumentacja jest bramką przed PR: bez docs backend blokuje utworzenie pull requesta.
- PR-y i docs są czytane z naszej bazy. GitHub jest zewnętrznym lustrem dla PR; docs są linkiem podanym przez użytkownika.
- Statusy PR w tej wersji: `OPEN`, `MERGED`, `CLOSED`.
- Moduł pokazuje cykl review w aplikacji: docs link -> PR -> Reviews -> approve/reject, z realnym GitHubem gdy integracja jest podłączona.
- Fallback bez tokenów: PR dostaje `local-pr-*` i `local://...`, więc demo działa także offline.
