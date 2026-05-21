// Placeholdery typów domenowych z dokumentacji.
// TODO: dopracować po zdefiniowaniu API backendu.

export type ProjectRole = 'OWNER' | 'DEVELOPER' | 'REVIEWER'
export type UserStatus = 'AVAILABLE' | 'BUSY' | 'OPEN_TO_TASKS'
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE' | 'CLOSED'
export type PullRequestStatus = 'OPEN' | 'APPROVED' | 'DECLINED' | 'MERGED'
export type IntegrationProvider = 'GITHUB' | 'JIRA' | 'CONFLUENCE'
export type NotificationType =
  | 'TASK_ASSIGNED'
  | 'TASK_UPDATED'
  | 'PR_CREATED'
  | 'PR_REVIEWED'
  | 'CHAT_MESSAGE'
export type TaskEventType =
  | 'CREATED'
  | 'STATUS_CHANGED'
  | 'COMMIT'
  | 'PR_OPENED'
  | 'PR_MERGED'
  | 'DOCS_ADDED'
