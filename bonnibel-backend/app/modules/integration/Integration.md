# Integration Module

---

## IntegrationProvider

```java
enum IntegrationProvider {
    GITHUB,
    JIRA,
    CONFLUENCE
}
```

---

## ProjectIntegration

```java
class ProjectIntegration {
    Long integrationId;
    Long projectId;

    String externalId;
    IntegrationProvider provider;
    String accessToken;

    Boolean isActive;
}
```

---

## ProjectIntegrationRepository

```java
interface ProjectIntegrationRepository {
    ProjectIntegration save(ProjectIntegration integration);

    Optional<ProjectIntegration> findByProjectIdAndProvider(
        Long projectId,
        IntegrationProvider provider
    );

    ProjectIntegration getActiveIntegration(
        Long projectId,
        IntegrationProvider provider
    );

    void updateAccessToken(
        Long projectId,
        IntegrationProvider provider,
        String accessToken
    );

    void disableIntegration(Long projectId, IntegrationProvider provider);

    boolean hasActiveIntegration(Long projectId, IntegrationProvider provider);
}
```
## WebhookSecretRepository
```java
interface WebhookSecretRepository {
    WebhookSecret save(WebhookSecret secret);

    WebhookSecret findActiveSecret(Long projectId, IntegrationProvider provider);

    void disableSecrets(Long projectId, IntegrationProvider provider);
}
```

---

## IntegrationHttpClient

```java
class IntegrationHttpClient {
    ExternalResponse get(String url, String token, Map<String, String> queryParams);
    ExternalResponse post(String url, String token, Map<String, Object> body);
    ExternalResponse put(String url, String token, Map<String, Object> body);
    ExternalResponse delete(String url, String token);
}
```

---

## GitIntegrationClient

```java
class GitIntegrationClient {
    private IntegrationConfigRepository configRepository;
    private IntegrationHttpClient httpClient;

    GitBranchRef createBranch(
        Long projectId,
        Long taskId,
        String jiraTicketKey,
        String assigneeName,
        String baseBranch
    );

    GitPullRequestRef createPullRequest(
        Long projectId,
        Long taskId,
        String title,
        String description,
        String sourceBranch,
        String targetBranch,
        String reviewerId
    );

    void mergePullRequest(Long projectId, String pullRequestExternalId);

    void deleteBranch(Long projectId, String branchName);
}
```

---

## JiraIntegrationClient

```java
class JiraIntegrationClient {
    private final ProjectIntegrationRepository configRepository;
    private final IntegrationHttpClient httpClient;

    JiraIntegrationClient(
        ProjectIntegrationRepository configRepository,
        IntegrationHttpClient httpClient
    );

    JiraTicketRef createTicket(
        Long projectId,
        Long taskId,
        String title,
        String description
    );

    void assignTicket(
        Long projectId,
        String jiraTicketKey,
        String assigneeId
    );

    void moveTicketToInProgress(
        Long projectId,
        String jiraTicketKey
    );

    void moveTicketToDone(
        Long projectId,
        String jiraTicketKey
    );

    JiraTicketRef getTicket(
        Long projectId,
        String jiraTicketKey
    );
}
```

---

## DocsIntegrationClient

```java
class DocsIntegrationClient {
    private IntegrationConfigRepository configRepository;
    private IntegrationHttpClient httpClient;

    DocsPageRef createTaskPage(
        Long projectId,
        Long taskId,
        String taskTitle,
        String content,
        String authorId
    );

    DocsPageRef updateTaskPage(
        Long projectId,
        String pageExternalId,
        String title,
        String content
    );

    DocsPageRef getPage(Long projectId, String pageExternalId);
}

---

## GitBranchRef

Возвращается после создания ветки. Внутри Bonnibel из него нужен `branchName`, который сохраняется в `Task.gitBranch`.

```java
class GitBranchRef {
    Long taskId;

    String branchName;
    String externalId;
    String url;
}
```

---

## GitPullRequestRef

Возвращается после создания Pull Request. Эти данные соответствуют таблице `PullRequest`.

```java
class GitPullRequestRef {
    String pullRequestExternalId;

    Long taskId;
    String reviewerId;

    PullRequestStatus status;

    String title;
    String url;

    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

---

## PullRequestStatus

```java
enum PullRequestStatus {
    OPEN,
    APPROVED,
    DECLINED,
    MERGED,
    CLOSED
}
```

---

## JiraTicketRef

Возвращается после создания или получения Jira ticket. Внутри Bonnibel из него нужен `ticketKey`, который сохраняется в `Task.jiraTicket`.

```java
class JiraTicketRef {
    Long taskId;

    String ticketExternalId;
    String ticketKey;
    String url;

    JiraTicketStatus status;
}
```

---

## JiraTicketStatus

```java
enum JiraTicketStatus {
    TODO,
    IN_PROGRESS,
    DONE
}
```

---

## DocsPageRef

Возвращается после создания или обновления страницы документации. Внутри Bonnibel из него нужен `url`, который сохраняется в `Task.docsLink`.

```java
class DocsPageRef {
    Long taskId;

    String pageExternalId;
    String title;
    String url;
}
```