# Bonnibel — Backend (placeholder)

Folder zarezerwowany na backend systemu Bonnibel. Stack jeszcze nie został
zdecydowany — do uzupełnienia po podjęciu decyzji.

## Co tu się znajdzie (na podstawie dokumentacji)

Architektura warstwowa (layered) z modułami:

- **REST Controllers** — przyjmowanie żądań od klienta frontendowego
- **Hook Handlers** — odbiór webhooków z Git / Jira
- **Auth Module** — `AuthService`, `AuthGuard`, JWT, `PermissionService`
- **Hook Auth Module** — weryfikacja podpisów webhooków (HMAC per provider)
- **Business Modules** — logika biznesowa:
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
- **Notification Module** — `NotificationService`, `WSModule` (WebSocket),
  `RecipientResolver`, `OnlineRepository`, `NotificationRepository`
- **Database** — encje: `Project`, `ProjectMember`, `User`, `Auth`, `Task`,
  `TaskHistory`, `PullRequest`, `ChatMessage`, `Notification`,
  `TaskSubscription`, `ProjectIntegration`, `WebhookSecret`, `Docs`

## Do decyzji

- [ ] Język + framework (kandydaci: Spring Boot, NestJS, FastAPI, Go, …)
- [ ] Baza danych (PostgreSQL prawdopodobnie)
- [ ] ORM / query builder
- [ ] Mechanizm migracji
- [ ] WebSocket (natywny / Socket.IO / STOMP)
- [ ] Sposób uruchamiania (Docker Compose razem z frontendem?)

## Status

Pusto — czekamy na decyzję zespołu o stacku.
