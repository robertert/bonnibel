// Placeholdery typów domenowych z dokumentacji.
// TODO: dopracować po zdefiniowaniu API backendu.

export type ProjectRole = 'OWNER' | 'DEVELOPER' | 'REVIEWER'
export type UserStatus = 'ACTIVE' | 'INACTIVE' | 'BANNED'
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
  | 'TASK_CLOSED'
  | 'CHAT_MESSAGE_CREATED'


export interface Notification {
  notificationId: number;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  linkUrl: string | null;
  isRead: boolean;
  isDelivered: boolean;
  createdAt: string;
}


export interface User {
  userId: string;
  email: string;
  name: string;
  surname: string;
  status: UserStatus;
  isOnline: boolean;
}

export interface Task {
  taskId: number;
  projectId: number;
  title: string;
  description: string;
  status: TaskStatus;
  assigneeId: string | null;
  reviewerId: string | null;
  gitBranchName: string | null;
  jiraIssueKey: string | null;
  createdAt: string;
  updatedAt: string;
  closedAt: string | null;
}

export interface TaskDoc {
  docsId: number;
  taskId: number;
  title: string;
  url: string;
  externalId: string | null;
}

export interface TaskSubscription {
  taskId: number;
  userId: string;
}

export interface TaskHistory {
  eventId: number;
  taskId: number;
  type: TaskEventType;
  actorId: string;
  title: string;
  description: string;
  url: string;
}



export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user_id?: string;
}

// Dopasowanie do bonnibel-backend/app/core/models.py:ChatMessage
//   message_id, task_id, author_id, text, created_at  (BRAK updated_at).
export interface ChatMessage {
  messageId: number;
  taskId: number;
  authorId: string;
  authorEmail?: string | null;
  text: string;
  createdAt: string;
}

// Dopasowanie do bonnibel-backend/app/modules/analytics/schemas.py:AnalyticsOverviewResponse
// Backend udostępnia jeden endpoint /analytics/overview zwracający komplet metryk.
//   tasksByStatus — klucze to wartości TaskStatus (TODO/IN_PROGRESS/IN_REVIEW/DONE),
//   tasksByUser   — klucz to assignee_id (może być pusty/null dla nieprzypisanych).
export interface AnalyticsOverview {
  taskCount: number;
  doneTasks: number;
  openTasks: number;
  completionRate: number;
  unassignedTasks: number;
  staleTasks: number;
  avgCycleTimeHours: number | null;
  tasksByStatus: Record<string, number>;
  tasksByUser: Record<string, number>;
  tasksByReviewer: Record<string, number>;
  wipByUser: Record<string, number>;
  throughputByDay: Record<string, number>;
}

export interface PullRequest {
  pullRequestId: number;
  taskId: number;
  externalId: string;
  title: string;
  url: string;
  reviewerId: string | null;
  status: 'OPEN' | 'MERGED' | 'CLOSED';
  createdAt: string;
  updatedAt: string;
  mergedAt: string | null;
}
