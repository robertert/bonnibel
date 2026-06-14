# Moduł: projects-members (Zarządzanie projektami i uczestnikami)

**Co pokazuje** (dok.: *Zarządzanie projektami* + *Zarządzanie uczestnikami projektu*):
- Projekty: utworzenie, lista, szczegóły, edycja, usunięcie (Owner).
- Członkowie: dodanie, zmiana roli, usunięcie, lista; właściciela nie da się usunąć.

**Wymagania wstępne:** zalogowany użytkownik (z modułu `auth`). Do dodawania członków przydają się userzy z seeda (`user-2`, `user-3`, `user-4`).

## Kroki w UI
1. `/projects` → lista projektów (widać „Bonnibel Core" z seeda). Kliknij **„Utwórz projekt"**/utwórz nowy „demo" (na żywo).
2. Wejdź w projekt → **szczegóły** (kafelki: Zadania, Członkowie, Analityka, Integracje).
3. **Członkowie** (`/projects/{id}/members`):
   - Dodaj członka: wpisz `user_id` (np. `user-2`) + rola **DEVELOPER** → Dodaj.
   - Dodaj `user-3` jako **REVIEWER** (potrzebny później do review).
   - Pokaż **zmianę roli** i że **OWNER-a nie można usunąć**.

## Backup: curl
```bash
# utwórz projekt (Owner = dummy/zalogowany)
curl -s -X POST localhost:8000/api/project/ -H 'Content-Type: application/json' \
  -d '{"name":"Projekt demo","description":"Pokaz na żywo"}'

# lista wszystkich projektów (zasila /projects)
curl -s localhost:8000/api/projects

# członkowie
curl -s localhost:8000/api/project/1/members
curl -s -X POST localhost:8000/api/project/1/members -H 'Content-Type: application/json' \
  -d '{"user_id":"user-2","role":"DEVELOPER"}'
curl -s -X PATCH localhost:8000/api/project/1/members/user-4/role -H 'Content-Type: application/json' \
  -d '{"role":"REVIEWER"}'
curl -s -X DELETE localhost:8000/api/project/1/members/user-2
```

## Talking points
- Tworząc projekt, autor automatycznie dostaje rolę **OWNER**.
- Role: **OWNER / DEVELOPER / REVIEWER** definiują uprawnienia (dok.: Role w systemie).
- Endpointy projektów/członków pod prefiksem `/api/project` (moduł logic); lista wszystkich projektów pod `/api/projects`.
- Usunięcie integracji projektu sprząta też powiązany webhook secret (FK).
