# Bonnibel — Frontend

System zarządzania postępem prac zespołu (Jira + Git + dokumentacja).
Szkielet aplikacji frontendowej. Backend nie został jeszcze zdecydowany.

## Stack

- **Vite + React 19 + TypeScript**
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **React Router** — routing
- **Zustand** — globalny state (np. auth)
- **TanStack Query** — cache zapytań HTTP

## Uruchomienie

```bash
npm install
npm run dev      # dev server
npm run build    # produkcyjny build
npm run lint     # ESLint
```

## Struktura

```
src/
├── App.tsx                     # Providery (QueryClient, Router)
├── main.tsx                    # bootstrap
├── index.css                   # Tailwind import
├── components/
│   ├── layout/                 # AppLayout, AuthLayout, Sidebar, Header
│   └── ui/                     # współdzielone komponenty UI (shadcn target)
├── modules/                    # moduły per obszar funkcjonalny
│   ├── auth/                   # logowanie, rejestracja, profil, status
│   ├── projects/               # CRUD projektów + integracje
│   ├── members/                # zarządzanie członkami i rolami
│   ├── tasks/                  # zadania, historia, dokumentacja
│   ├── reviews/                # pull requesty, approve/decline
│   ├── notifications/          # powiadomienia + WebSocket
│   ├── chat/                   # czat w zadaniach
│   └── analytics/              # statystyki projektu
├── router/routes.tsx           # konfiguracja React Router
├── lib/                        # api client, queryClient
├── store/                      # globalne stany Zustand
└── types/                      # współdzielone typy domenowe
```

Każdy moduł ma podfoldery `pages/`, `components/`, `hooks/`, `api/`
do uzupełnienia w trakcie implementacji.

## Mapowanie modułów na dokumentację

| Moduł frontendu  | Funkcjonalność z dokumentacji                          |
|------------------|--------------------------------------------------------|
| `auth`           | Zarządzanie kontem (signup, login, profil, status)     |
| `projects`       | Zarządzanie projektami + integracje Git/Jira/Docs      |
| `members`        | Zarządzanie uczestnikami projektu i rolami             |
| `tasks`          | Zarządzanie zadaniami, dokumentacja, historia          |
| `reviews`        | Pull requesty (approve / decline)                      |
| `notifications`  | Powiadomienia (get, mark as read) + WebSocket          |
| `chat`           | Wiadomości w czacie zadania                            |
| `analytics`      | Statystyki: task count, per status, per user           |

## Status

Szkielet — wszystkie strony są placeholderami `TODO`. Routing, layout
i stack są skonfigurowane. Logikę dopisujemy moduł po module.
