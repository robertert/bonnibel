# Moduł: analitycs-chat (Analityka + Czat)

**Co pokazuje** (dok.: *Zarządzanie zadaniami i analityka* + *Komunikacja*):
- Analityka projektu: liczba zadań, rozkład per status, per użytkownik (wykonawca/recenzent), completion rate, WIP, cycle time.
- Czat przy zadaniu: wysyłanie/odczyt wiadomości, **broadcast przez WebSocket** (na żywo).

**Wymagania wstępne:** zalogowany user. Analitykę najlepiej pokazać na projekcie **„Bonnibel Core"** (z seeda — ma dane). Czat działa na dowolnym zadaniu.

## Kroki w UI
1. **Analityka** (`/projects/1/analytics` lub `/analytics`): pokaż kafelki/wykresy — liczba zadań, podział po statusach, po użytkownikach, completion rate. (Na „Bonnibel Core" są dane z seeda.)
2. **Czat**: wejdź w zadanie → panel czatu na dole → wyślij wiadomość.
3. **Na żywo (WS)**: otwórz to samo zadanie w drugim oknie → wiadomość pojawia się **natychmiast** u obu (broadcast).

## Backup: curl
```bash
# analityka
curl -s localhost:8000/api/projects/1/analytics/overview

# czat (wysyłka wymaga Bearer; odczyt publiczny)
curl -s localhost:8000/api/projects/1/tasks/101/messages
curl -s -X POST -H "Authorization: Bearer TOKEN" -H 'Content-Type: application/json' \
  localhost:8000/api/projects/1/tasks/101/messages -d '{"text":"Cześć z prezentacji!"}'
```
WebSocket czatu: `ws://localhost:8000/api/ws/tasks/101/chat`.

## Talking points
- Analityka liczona po stronie backendu z tabeli `tasks` (status, assignee, reviewer, daty) — jeden endpoint `overview` zwraca komplet metryk.
- `tasksByUser`/`tasksByReviewer` mapują po użytkownikach; „(brak)" = nieprzypisane.
- Czat zapisuje `ChatMessage` i rozgłasza do połączonych klientów (`ChatConnectionManager`), pokazując realtime bez odświeżania.
