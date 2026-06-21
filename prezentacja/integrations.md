# Moduł: integrations (Integration + Hook Auth)

**Co pokazuje** (dok.: *Integration Module* + *Hook Auth Module* + diagram sekwencji hooka):
- Podłączanie/odłączanie integracji projektu: **GitHub, Jira, Confluence**.
- Realne efekty na GitHubie: **gałąź + commit** (przy przypisaniu zadania), **merge** (przy akceptacji PR).
- Jira: przejście statusu ticketu; Confluence: podłączany jako integracja projektu, ale `pr-docs` zapisuje link podany przez użytkownika i nie tworzy strony automatycznie.
- **Webhooki + Hook Auth**: weryfikacja podpisu HMAC (zaufane źródło).

**Wymagania wstępne:** projekt (z `projects-members`), realny token GitHub (PAT) i repo `owner/repo` z commitem na `main`. Opcjonalnie token Atlassian.

## Kroki w UI — podłączanie tokenów
1. Projekt → **Integracje** (`/projects/{id}/integrations`).
2. **GitHub**: `Identyfikator zewnętrzny` = `owner/repo`, `Token` = PAT → **Podłącz**. Pojawia się na liście „Podłączone".
   - (Jeśli projekt to seedowy „Bonnibel Core" z atrapą GitHub — najpierw **Odłącz** atrapę.)
3. **Jira**: external_id = `https://twojadomena.atlassian.net`, Token = `email:api_token`.
4. **Confluence**: external_id = `https://twojadomena.atlassian.net/wiki`, Token = `email:api_token`.

## Przepływ GitHub / PR
> `pr-docs` korzysta z modułu `integration` w trybie best-effort: przy podłączonym GitHubie tworzy realny PR i próbuje merge przy approve, a bez tokenów zostawia lokalny rekord w bazie.

1. W `profile-tasks`: utwórz zadanie i **przypisz wykonawcę** → na GitHubie pojawia się **gałąź** `bon-{taskId}-{user}` **z plikiem** `.bonnibel/...md` (auto-commit, żeby PR miał diff).
2. W `pr-docs`: **Dodaj docs** → użytkownik podaje tytuł i URL dokumentacji utworzonej poza Bonnibel.
3. W `pr-docs`: **Utwórz PR** → przy aktywnym GitHubie powstaje realny Pull Request; bez GitHuba PR zapisuje się lokalnie jako `OPEN`.
4. W `pr-docs`: **Approve/Reject** → approve próbuje merge na GitHubie i ustawia `MERGED`; reject ustawia `CLOSED`.

## Webhooki / Hook Auth (przychodzące zdarzenia)
Sekret dla projektu 1 z seeda: **`demo-webhook-secret`** (GitHub). Pokaż weryfikację podpisu:
```bash
# poprawny podpis -> 202 + wpis w historii zadania 104 + powiadomienie
BODY='{"taskId":104,"title":"Push to branch","message":"3 new commits"}'
SIG=$(BODY="$BODY" ./bonnibel-backend/venv/bin/python -c "import os,hmac,hashlib;print('sha256='+hmac.new(b'demo-webhook-secret', os.environ['BODY'].encode(), hashlib.sha256).hexdigest())")
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/api/hooks/git/1 \
  -H "X-Hub-Signature-256: $SIG" -H 'Content-Type: application/json' -d "$BODY"   # -> 202

# zły podpis -> 401 (odrzucone)
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/api/hooks/git/1 \
  -H "X-Hub-Signature-256: sha256=deadbeef" -H 'Content-Type: application/json' -d "$BODY"  # -> 401
```

## Backup: curl (integracje)
```bash
curl -s localhost:8000/api/project/1/integrations
curl -s -X POST localhost:8000/api/project/1/integrations -H 'Content-Type: application/json' \
  -d '{"provider":"GITHUB","external_id":"OWNER/REPO","access_token":"github_pat_..."}'
curl -s -X DELETE localhost:8000/api/project/1/integrations/GITHUB
```

## Talking points
- Architektura: wspólny `HttpClient` + osobni klienci (Git/Jira/Confluence), token z bazy (`project_integrations`).
- **GitHub = Bearer**, **Jira/Confluence = Basic** (`email:api_token`) — automatycznie dobierane.
- Wywołania zewnętrzne są **best-effort**: brak/zły token → akcja w aplikacji i tak przechodzi, a powód błędu ląduje w logach (`WARNING ...: HTTP 401 ...`).
- Hook Auth: `SignatureVerifierFactory` dobiera weryfikator (Git/Jira) → HMAC-SHA256 względem sekretu z `webhook_secrets`.

## Ryzyka
- **401 Bad credentials** = zły/wygasły PAT (sprawdź `GET /repos/OWNER/REPO/git/refs/heads/main` = 200 przed demo).
- **Jira transition ID** zahardkodowane (`"21"`/`"31"` w `jira_client.py`) — w realnej instancji bywają inne; jeśli przejście nie zadziała, to tylko ten krok (nie blokuje reszty).
