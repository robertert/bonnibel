# Bonnibel — prezentacja: przygotowanie i kolejność

Dokument podzielony na moduły (wg branchy). Ten plik = przygotowanie + kolejność.
Pliki modułów: `auth.md`, `projects-members.md`, `integrations.md`, `profile-tasks.md`,
`pr-docs.md`, `notification.md`, `analitycs-chat.md`.

---

## 1. Przygotowanie PRZED prezentacją (checklist)

### Czysta baza + pełne tło (dane do pokazania nasycenia)
```bash
cd bonnibel-backend
docker compose down -v && docker compose up -d --wait      # świeży Postgres
./venv/bin/alembic upgrade head                      # migracje
./venv/bin/python scripts/seed_demo.py               # 4 userów + projekt "Bonnibel Core" z danymi
```
> **Ważne:** `--wait` blokuje, aż Postgres zgłosi gotowość (healthcheck w `docker-compose.yml`).
> Bez tego `alembic` odpala się zanim baza wstanie → błąd „connection ... server closed" / „relation users does not exist".
> Starszy compose bez `--wait`? Użyj pętli:
> `until docker exec bonnibel_db pg_isready -U app -d bonnibel_db; do sleep 1; done` przed `alembic`.

Seed daje loginowalnych userów (hasło dla wszystkich: **`password123`**):

| Login | user_id | Rola w "Bonnibel Core" |
|---|---|---|
| owner@bonnibel.dev | user-1 | OWNER |
| dev@bonnibel.dev | user-2 | DEVELOPER |
| reviewer@bonnibel.dev | user-3 | REVIEWER |
| dev2@bonnibel.dev | user-4 | DEVELOPER |

### Uruchomienie
```bash
# terminal 1
cd bonnibel-backend && ./venv/bin/uvicorn app.main:app --reload      # :8000, Swagger /api/docs
# terminal 2
cd bonnibel-frontend && npm run dev                                  # :5173
```

### Konta zewnętrzne (w ręku, przetestowane przed wejściem)
- **GitHub**: testowe repo z commitem na `main` (np. README), fine-grained PAT (uprawnienia **Contents: RW**, **Pull requests: RW**). `external_id` = `owner/repo`.
  - Sprawdź token (musi być **200**): `curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer PAT" https://api.github.com/repos/OWNER/REPO/git/refs/heads/main`
- **Jira/Confluence** (Atlassian Cloud, opcjonalnie): API token z id.atlassian.com. W polu „Token" wpisać **`email:api_token`** (Basic). `external_id` = base URL (Jira) lub `.../wiki` (Confluence).

---

## 2. Co mieć już stworzone vs co na żywo

| Element | Stan | Dlaczego |
|---|---|---|
| Użytkownicy (4) | **pre-seed** | logowanie/przypisania/członkowie bez tracenia czasu |
| Projekt „Bonnibel Core" + dane | **pre-seed (tło)** | szybki tour po analityce/powiadomieniach/czacie/historii |
| Rejestracja 1 usera | **na żywo** | pokaz modułu konta (signup→login) |
| Projekt „demo" | **na żywo** | pokaz tworzenia projektu (Owner) |
| Integracje (GH/Jira/Confluence) | **na żywo** | pokaz podpinania tokenów |
| Zadanie → gałąź → PR → merge | **na żywo, realny GitHub** | sedno: realny efekt na GitHubie |

> Dwa wątki: **projekt „demo"** (tworzony na żywo, realny GitHub) i **projekt „Bonnibel Core"** (z seeda, do pokazania nasyconych ekranów: analityka, powiadomienia, czat, historia).

---

## 3. Rekomendowana kolejność między modułami (jeden spójny przebieg)

```
auth            → rejestracja + login
projects-members→ utwórz projekt "demo"
integrations    → podłącz GitHub (+ Jira/Confluence)
projects-members→ dodaj członków + role
profile-tasks   → profil/status; utwórz zadanie; PRZYPISZ wykonawcę  ──► gałąź+commit na GitHubie
pr-docs         → Utwórz PR (realny PR na GH); docs; Reviews → Akceptuj ──► merge na GH + zadanie DONE
analitycs-chat  → czat w zadaniu; analityka (na "Bonnibel Core")
notification    → powiadomienia na żywo (WS); subskrypcje; presence
integrations    → webhook z podpisem (Hook Auth): poprawny → 202, zły → 401
```

Każdy moduł da się też pokazać samodzielnie — sekcja „Wymagania wstępne" w każdym pliku mówi, co musi istnieć wcześniej.

---

## 4. Adresy

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000` · Swagger: `http://localhost:8000/api/docs` · health: `/api/health`

## 5. Reset w trakcie (gdyby coś poszło nie tak)
```bash
cd bonnibel-backend && docker compose down -v && docker compose up -d --wait && ./venv/bin/alembic upgrade head && ./venv/bin/python scripts/seed_demo.py
```
