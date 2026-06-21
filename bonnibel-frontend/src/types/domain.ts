// Placeholdery typow domenowych z dokumentacji.
// TODO: dopracowac po zdefiniowaniu API backendu.

export type ProjectRole = 'OWNER' | 'DEVELOPER' | 'REVIEWER'
export type UserStatus = 'ACTIVE' | 'INACTIVE' | 'BANNED'
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE' | 'CLOSED'
export type PullRequestStatus = 'OPEN' | 'MERGED' | 'CLOSED'
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

export interface PullRequest {
  pullRequestId: number;
  projectId?: number | null;
  taskId: number;
  externalId: string;
  title: string;
  url: string;
  assigneeId?: string | null;
  reviewerId: string | null;
  status: PullRequestStatus;
  createdAt: string;
  updatedAt: string | null;
  mergedAt: string | null;
}

export interface ProjectMember {
  projectId: number;
  userId: string;
  role: ProjectRole;
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

export interface ChatMessage {
  messageId: number;
  taskId: number;
  authorId: string;
  authorEmail?: string | null;
  text: string;
  createdAt: string;
}

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

export type AnalyticsByAssignee = Record<string, number>

export interface AnalyticsCommits {
  commitCount: number;
  byActor: Record<string, number>;
}
