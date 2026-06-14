# Moduł: notification (Powiadomienia + subskrypcje + presence)

**Co pokazuje** (dok.: *Powiadomienia i komunikacja* + *Notification Module*):
- Powiadomienia: lista, licznik nieprzeczytanych, oznacz jako przeczytane / wszystkie.
- Subskrypcje zadań: sub / unsub / lista obserwowanych.
- **Powiadomienia na żywo przez WebSocket** (bez odświeżania).
- Presence: status online użytkownika (`is_online`) aktualizowany na połączeniu WS.

**Wymagania wstępne:** zalogowany user. Najlepiej pokazywać PO module `pr-docs`, bo PR-y generują powiadomienia. Tło: seed ma gotowe powiadomienia dla user-1..4.

## Kroki w UI
1. **Powiadomienia** (`/notifications`): lista (seed ma kilka), filtr „nieprzeczytane", **oznacz jako przeczytane** i **oznacz wszystkie**.
2. **Na żywo (WS)**: miej otwartą stronę powiadomień i w drugim oknie/koncie wykonaj akcję generującą powiadomienie (utwórz/akceptuj PR, albo wyślij webhook) → **nowe powiadomienie pojawia się bez odświeżania** (prepend + licznik).
3. **Subskrypcja**: wejdź w zadanie → przycisk **🔕 Obserwuj / 🔔 Obserwujesz** (toggluje subskrypcję). Lista subskrypcji widoczna w `/api/tasks/subscriptions`.
4. **Presence**: po wejściu na stronę powiadomień otwiera się socket → `is_online=true`; po zamknięciu → `false`.

## Backup: curl
```bash
# (wszystko wymaga Bearer)
curl -s -H "Authorization: Bearer TOKEN" localhost:8000/api/notifications?limit=5
curl -s -H "Authorization: Bearer TOKEN" localhost:8000/api/notifications/unread-count
curl -s -X PATCH -H "Authorization: Bearer TOKEN" localhost:8000/api/notifications/read-all

# subskrypcje
curl -s -H "Authorization: Bearer TOKEN" localhost:8000/api/tasks/subscriptions
curl -s -X POST   -H "Authorization: Bearer TOKEN" localhost:8000/api/tasks/104/subscribe
curl -s -X DELETE -H "Authorization: Bearer TOKEN" localhost:8000/api/tasks/104/subscribe

# ręczne zdarzenie powiadomienia (do pokazania WS)
curl -s -X POST -H "Authorization: Bearer TOKEN" -H 'Content-Type: application/json' \
  localhost:8000/api/notifications/events \
  -d '{"type":"TASK_UPDATED","taskId":102,"projectId":1,"title":"Test","message":"Na żywo"}'
```
WebSocket: `ws://localhost:8000/api/ws/notifications?token=TOKEN` (lub `?userId=user-1`).

## Talking points
- `RecipientResolver` dobiera odbiorców wg typu zdarzenia (assignee/reviewer/owner/subskrybenci) na podstawie snapshotu zadania i subskrypcji.
- Dostarczenie online ustawia `is_delivered`; w bazie zostaje też dla offline (odczyt później).
- Powiadomienia powstają automatycznie z akcji (PR_CREATED, PR_REVIEWED, webhook → TASK_UPDATED) — to spina notification z pr-docs i integrations.
