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
  accessToken: string;
  refreshToken: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  userId: string;
}