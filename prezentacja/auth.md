# Moduł: auth (Zarządzanie kontem)

**Co pokazuje** (dok.: *Zarządzanie kontem*): rejestracja (signup), tworzenie profilu, logowanie, odświeżanie tokenu (refresh). Wylogowanie = po stronie klienta (usunięcie tokenu).

**Wymagania wstępne:** brak (to początek demo). Backend + frontend uruchomione.

## Kroki w UI
1. Wejdź na `http://localhost:5173/register`.
2. Zarejestruj nowego użytkownika (email, hasło, imię, nazwisko) — pokazuje **signup**.
3. Po rejestracji następuje przekierowanie do profilu/logowania → **zaloguj się** (`/login`).
4. (Opcjonalnie) pokaż, że istnieją już konta z seeda — zaloguj jako `owner@bonnibel.dev` / `password123`.
5. Token JWT trzymany w localStorage; przy 401 frontend sam robi **refresh** (transparentnie).

## Backup: curl
```bash
# rejestracja
curl -s -X POST localhost:8000/api/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"nowy@bonnibel.dev","password":"haslo123","name":"Nowy","surname":"User"}'

# logowanie -> zwraca access_token, refresh_token, user_id
curl -s -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"owner@bonnibel.dev","password":"password123"}'

# refresh (refresh_token jako query param)
curl -s -X POST "localhost:8000/api/auth/refresh?refresh_token=REFRESH_TOKEN"
```

## Talking points
- Hasła hashowane **bcrypt** (`app/core/security.py`), tokeny **JWT** (access 30 min, refresh 7 dni).
- Logout świadomie tylko po stronie klienta (usunięcie refresh tokenu) — zgodnie z dokumentacją.
- Endpointy wymagające zalogowania (czat, powiadomienia, docs, PR, subskrypcje) działają na **Bearer** — dlatego zaczynamy od logowania.
