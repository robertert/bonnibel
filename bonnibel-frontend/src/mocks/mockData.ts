import type { Task, User } from '../types/domain';

// Przykładowi użytkownicy
export const mockUsers: User[] = [
  {
    userId: 'user-1',
    email: 'jan.kowalski@example.com',
    name: 'Jan',
    surname: 'Kowalski',
    status: 'AVAILABLE',
    isOnline: true,
  },
  {
    userId: 'user-2',
    email: 'anna.nowak@example.com',
    name: 'Anna',
    surname: 'Nowak',
    status: 'BUSY',
    isOnline: false,
  },
  {
    userId: 'user-3',
    email: 'piotr.zielinski@example.com',
    name: 'Piotr',
    surname: 'Zieliński',
    status: 'OPEN_TO_TASKS',
    isOnline: true,
  }
];

// Przykładowe zadania
export const mockTasks: Task[] = [
  {
    taskId: 101,
    projectId: 1,
    title: 'Konfiguracja boilerplate projektu',
    description: 'Przygotowanie struktury katalogów React i konfiguracji tsconfig.',
    status: 'DONE',
    assigneeId: 'user-3',
    reviewerId: 'user-1',
    gitBranchName: 'feature/bon-101-boilerplate',
    jiraIssueKey: 'BON-101',
    createdAt: '2026-05-20T10:00:00.000Z',
    updatedAt: '2026-05-21T12:00:00.000Z',
    closedAt: '2026-05-21T12:00:00.000Z',
  },
  {
    taskId: 102,
    projectId: 1,
    title: 'Integracja Auth Module z frontendem',
    description: 'Zaimplementowanie widoków rejestracji (signup) oraz logowania (login).',
    status: 'IN_PROGRESS',
    assigneeId: 'user-2',
    reviewerId: 'user-1',
    gitBranchName: 'feature/bon-102-auth-integration',
    jiraIssueKey: 'BON-102',
    createdAt: '2026-05-22T08:30:00.000Z',
    updatedAt: '2026-05-24T11:00:00.000Z',
    closedAt: null,
  },
  {
    taskId: 103,
    projectId: 1,
    title: 'Stworzenie widoku Tablicy Zadań (Kanban)',
    description: 'Zaprojektowanie i oprogramowanie komponentów tablicy z podziałem na kolumny Todo/Progress/Review/Done.',
    status: 'TODO',
    assigneeId: 'user-1',
    reviewerId: null,
    gitBranchName: null,
    jiraIssueKey: 'BON-103',
    createdAt: '2026-05-23T15:00:00.000Z',
    updatedAt: '2026-05-23T15:00:00.000Z',
    closedAt: null,
  }
];