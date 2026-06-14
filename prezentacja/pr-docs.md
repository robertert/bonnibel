# Moduł: pr-docs (Pull Requesty + Dokumentacja + Reviews)

**Co pokazuje** (dok.: *Zarządzanie zadaniami i review* + *Dokumentacja*):
- PR: utworzenie (→ zadanie IN_REVIEW), lista, akceptacja (→ merge + DONE), odrzucenie (→ wraca do IN_PROGRESS).
- Docs: dodanie i lista dokumentacji zadania (best-effort strona w Confluence).
- Strona **Reviews**: zadania w review, w których jesteś recenzentem.

**Wymagania wstępne:** zadanie z przypisanym wykonawcą (z `profile-tasks`) i recenzentem; do realnego PR — podłączony GitHub i istniejąca **gałąź z commitem** (tworzona automatycznie przy przypisaniu — patrz `integrations.md`).

## Kroki w UI
1. Wejdź w zadanie → panel **Pull Requesty** → wpisz tytuł → **Utwórz PR**.
   - ⇒ realny **Pull Request** na GitHubie (dzięki auto-commitowi gałąź ma diff); zadanie → **IN_REVIEW**; powiadomienie do recenzenta.
2. Panel **Dokumentacja** → dodaj dokument (tytuł + URL). Jeśli Confluence podłączony → powstaje realna strona.
3. **Reviews** (`/reviews`): zaloguj jako **reviewer@bonnibel.dev** → lista zadań do recenzji → wejdź w zadanie.
4. W panelu PR: **Akceptuj** → na GitHubie **merge** + usunięcie gałęzi; zadanie → **DONE** (Jira → Done jeśli podłączona). Albo **Odrzuć** → zadanie wraca do IN_PROGRESS.

## Backup: curl
```bash
# utwórz PR (wymaga Bearer -> najpierw login)
curl -s -X POST localhost:8000/api/projects/1/tasks/104/pull-requests \
  -H "Authorization: Bearer TOKEN" -H 'Content-Type: application/json' -d '{"title":"Auth integration"}'
curl -s localhost:8000/api/projects/1/tasks/104/pull-requests

# akceptacja / odrzucenie (Bearer reviewera)
curl -s -X POST localhost:8000/api/pull-requests/PR_ID/approve -H "Authorization: Bearer TOKEN"
curl -s -X POST localhost:8000/api/pull-requests/PR_ID/decline -H "Authorization: Bearer TOKEN"

# docs
curl -s -X POST localhost:8000/api/projects/1/tasks/104/docs \
  -H "Authorization: Bearer TOKEN" -H 'Content-Type: application/json' -d '{"title":"Kontrakt API","url":"https://..."}'
curl -s localhost:8000/api/projects/1/tasks/104/docs
```

## Talking points
- Aplikacja jest **źródłem prawdy** dla PR-ów (zapis w bazie); GitHub to **lustro** (best-effort: realny PR/merge gdy integracja aktywna).
- Akceptacja PR domyka cały cykl: PR MERGED + zadanie DONE + powiadomienie `PR_REVIEWED` + wpis w historii.
- Lista PR-ów/docs czytana z naszej bazy (nie pobierana z GitHuba).
- Status PR w bazie: OPEN/MERGED/CLOSED (approve→MERGED, decline→CLOSED).
