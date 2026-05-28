# Bonnibel — Backend

Folder zawierający kod źródłowy backendu systemu Bonnibel.

## Wybrany stos technologiczny (Stack)

- **Język i framework:** Python 3 + FastAPI
- **Baza danych:** PostgreSQL
- **ORM / query builder:** SQLAlchemy
- **Mechanizm migracji:** Alembic
- **WebSocket:** Natywny mechanizm `fastapi.WebSocket`
- **Sposób uruchamiania:** Docker Compose (zintegrowany ze środowiskiem bazy danych i frontendem)

Powyzsza propozycja wykorzystania natywnego mechanizmu `fastapi.WebSocket` oraz Docker Compose to wstępny pomysł.

## Architektura i moduły systemu

Zastosowano architekturę warstwową (layered) z podziałem na moduły biznesowe.

- **REST Controllers (Routers)** — przyjmowanie żądań od klienta frontendowego (`router.py` w modułach)
- **Hook Handlers** — odbiór webhooków z Git / Jira
- **Auth Module** — `AuthService`, `AuthGuard` (wstrzykiwany jako zależność FastAPI), JWT, `PermissionService`
- **Hook Auth Module** — weryfikacja podpisów webhooków (HMAC per provider)
- **Business Modules** — logika biznesowa (pliki `service.py`):
  - `ProjectService`
  - `MembershipService`
  - `UserService`
  - `TaskService`
  - `DocsService`
  - `PRService`
  - `ChatService`
  - `AnalyticsService`
- **Integration Module** — `GitIntegrationClient`, `JiraIntegrationClient`,
  `ConfluenceIntegrationClient`, wspólny `HttpClient`, `ConfigRepository`
- **Notification Module** — `NotificationService`, `WSModule` (obsługa WebSocket),
  `RecipientResolver`, `OnlineRepository`, `NotificationRepository`
- **Database** — encje definiowane przez SQLAlchemy: `Project`, `ProjectMember`, `User`, `Auth`, `Task`,
  `TaskHistory`, `PullRequest`, `ChatMessage`, `Notification`,
  `TaskSubscription`, `ProjectIntegration`, `WebhookSecret`, `Docs`

## Procedura uruchomienia backendu

### 1. Tworzenie i aktywacja środowiska wirtualnego
```bash
python -m venv venv
```
Windows: .\venv\Scripts\activate
Linux/Mac: source venv/bin/activate

### 2. Instalacja zależności
```bash
pip install -r requirements.txt
```
### 3. Uruchomienie bazy danych PostgreSQL
```bash
docker compose up -d
```
### 4. Generowanie i aplikacja migracji bazy danych
```bash
alembic upgrade head
```

### 5. Uruchomienie serwera
```bash
uvicorn app.main:app --reload
```
## Struktura katalogów backendu

Struktura opiera się na izolacji modułów:

- `app/core/` — konfiguracja globalna (zmienne środowiskowe, połączenie DB, schemat bazy danych).
- `app/dependencies/` — współdzielone funkcje dla *Dependency Injection*.
- `app/modules/` — poszczególne domeny systemu (auth, logic, integration, notification).
- `alembic/` — wersjonowanie schematu bazy danych.

Poniżej znajduje się szczegółowy podział struktury katalogów dla aplikacji opartej na FastAPI i SQLAlchemy. Zastosowano architekturę z podziałem na moduły biznesowe (Domain-Driven Design), co zapewnia czytelną separację logiki poszczególnych domen.

```text
bonnibel-backend/
├── alembic/                    # Konfiguracja i pliki migracji bazy danych (Alembic)
│   ├── versions/               # Wygenerowane pliki migracji (np. tworzenie nowych tabel)
│   └── env.py                  # Skrypt ładujący modele SQLAlchemy na potrzeby generowania migracji
│
├── app/
│   ├── core/                   # Globalna konfiguracja i fundamenty aplikacji
│   │   ├── config.py           # Wczytywanie i walidacja zmiennych środowiskowych (Pydantic BaseSettings)
│   │   ├── database.py         # Inicjalizacja silnika SQLAlchemy i sesji bazy danych
│   │   ├── models.py           # Tabele SQLAlchemy
│   │   └── security.py         # Konfiguracja algorytmów hashowania haseł i mechanizmów JWT
│   │
│   ├── dependencies/           # Współdzielone funkcje wstrzykiwania zależności (Dependency Injection)
│   │   ├── auth.py             # Implementacja AuthGuard (weryfikacja tokenów i uprawnień)
│   │   └── db.py               # Dostarczanie sesji bazy danych do routerów
│   │
│   ├── modules/                # Logika biznesowa pogrupowana w domeny
│   │   │
│   │   ├── auth/               # Zarządzanie tożsamością i dostępem
│   │   │   ├── router.py       # REST Controllers (np. POST /login, POST /register)
│   │   │   ├── service.py      # AuthService (weryfikacja logowania, generowanie tokenów)
│   │   │   └── schemas.py      # DTO (Pydantic): definicje payloadów wejściowych i wyjściowych
│   │   │
│   │   ├── hook_auth/          # Walidacja zdarzeń zewnętrznych (Webhooki)
│   │   │   ├── router.py       # Hook Handlers: endpointy przyjmujące powiadomienia
│   │   │   ├── verifier.py     # Weryfikacja sygnatur (HMAC per provider)
│   │   │   └── schemas.py      # DTO dla struktur danych przesyłanych przez zewnętrzne API
│   │   │
│   │   ├── integration/        # Połączenia z zewnętrznymi narzędziami
│   │   │   ├── router.py       # Endpointy do zarządzania integracjami projektów
│   │   │   ├── service.py      # Logika biznesowa integracji
│   │   │   ├── clients.py      # Klienci HTTP (GitIntegrationClient, JiraIntegrationClient)
│   │   │   └── schemas.py      # DTO dla modułu integracji
│   │   │
│   │   ├── logic/              # Główna logika systemu (Zadania, Projekty, Pull Requesty)
│   │   │   ├── router.py       # REST Controllers dla projektów i zadań
│   │   │   ├── service.py      # ProjectService, TaskService, MembershipService, DocsService
│   │   │   ├── repository.py   # Warstwa abstrakcji dla złożonych zapytań SQL do bazy
│   │   │   └── schemas.py      # DTO zadań, projektów i historii
│   │   │
│   │   └── notification/       # Obsługa czasu rzeczywistego i komunikacji
│   │       ├── router.py       # Endpointy HTTP (np. pobieranie historii powiadomień)
│   │       ├── ws.py           # WSModule: punkt wejścia dla połączeń WebSocket
│   │       └── manager.py      # NotificationService, ChatService, RecipientResolver (zarządzanie sesjami)
│   │
│   └── main.py                 # Główny plik aplikacji, inicjalizacja FastAPI i rejestracja wszystkich routerów
│
├── tests/                      # Katalog testów automatycznych (Pytest)
│   ├── conftest.py             # Konfiguracja środowiska testowego (np. testowa baza w pamięci) i fixtury
│   ├── modules/                # Testy integracyjne podzielone zgodnie z modułami w aplikacji
│   └── core/                   # Testy jednostkowe konfiguracji bazowej i bezpieczeństwa
│
├── alembic.ini                 # Główny plik konfiguracyjny mechanizmu migracji Alembic
├── requirements.txt            # Lista pakietów i ich wersji
├── .env                        # Lokalne zmienne środowiskowe (nie są objęte kontrolą wersji)
└── .gitignore                  # Definicje plików i katalogów ignorowanych przez repozytorium Git

