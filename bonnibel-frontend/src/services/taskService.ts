import { apiFetch } from '@/lib/api'
import type { Task, TaskStatus } from '@/types/domain'
import { mockTasks } from '@/mocks/mockData'

const USE_MOCK = true;
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const taskService = {
  getProjectTasks: async (
    projectId: number,
    filters?: {
      status?: TaskStatus;
      assigneeId?: string;
      reviewerId?: string;
      onlySubscribed?: boolean;
    }
  ): Promise<Task[]> => {
    if (USE_MOCK) {
      await delay(400);
      let tasks = mockTasks.filter(t => t.projectId === projectId);
      
      if (filters?.status) {
        tasks = tasks.filter(t => t.status === filters.status);
      }
      if (filters?.assigneeId) {
        tasks = tasks.filter(t => t.assigneeId === filters.assigneeId);
      }
      if (filters?.reviewerId) {
        tasks = tasks.filter(t => t.reviewerId === filters.reviewerId);
      }
      return tasks;
    }

    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.assigneeId) params.append('assigneeId', filters.assigneeId);
    if (filters?.reviewerId) params.append('reviewerId', filters.reviewerId);
    if (filters?.onlySubscribed !== undefined) params.append('onlySubscribed', String(filters.onlySubscribed));

    return apiFetch<Task[]>(`/projects/${projectId}/tasks?${params.toString()}`);
  },

  getTask: async (projectId: number, taskId: number): Promise<Task> => {
    if (USE_MOCK) {
      await delay(300);
      const foundTask = mockTasks.find(t => t.projectId === projectId && t.taskId === taskId);
      if (!foundTask) throw new Error(`Zadanie o id ${taskId} nie istnieje w projekcie ${projectId}.`);
      return foundTask;
    }
    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}`);
  },

  getMyTasks: async (projectId: number): Promise<Task[]> => {
    if (USE_MOCK) {
      await delay(400);
      return mockTasks.filter(t => t.projectId === projectId && t.assigneeId === 'user-1');
    }
    return apiFetch<Task[]>(`/projects/${projectId}/tasks/my`);
  },

  getUserTasks: async (projectId: number, userId: string): Promise<Task[]> => {
    if (USE_MOCK) {
      await delay(400);
      return mockTasks.filter(t => t.projectId === projectId && t.assigneeId === userId);
    }
    return apiFetch<Task[]>(`/projects/${projectId}/tasks?assigneeId=${userId}`);
  },

  updateStatus: async (projectId: number, taskId: number, status: TaskStatus): Promise<Task> => {
    if (USE_MOCK) {
      await delay(300);
      const task = mockTasks.find(t => t.projectId === projectId && t.taskId === taskId);
      if (!task) throw new Error("Zadanie nie istnieje.");
      
      task.status = status;
      task.updatedAt = new Date().toISOString();
      
      if (status === 'CLOSED') {
        task.closedAt = new Date().toISOString();
      } else {
        task.closedAt = null;
      }
      return task;
    }

    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  createTask: async (
    projectId: number,
    taskData: { title: string; description: string; assigneeId?: string; reviewerId?: string }
  ): Promise<Task> => {
    if (USE_MOCK) {
      await delay(450);
      const newTask: Task = {
        taskId: Date.now(),
        projectId,
        title: taskData.title,
        description: taskData.description,
        status: 'TODO',
        assigneeId: taskData.assigneeId || null,
        reviewerId: taskData.reviewerId || null,
        gitBranchName: null,
        jiraIssueKey: `BON-${Math.floor(Math.random() * 800) + 100}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        closedAt: null,
      };
      mockTasks.push(newTask);
      return newTask;
    }

    return apiFetch<Task>(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  assignTask: async (projectId: number, taskId: number, assigneeId: string | null): Promise<Task> => {
    if (USE_MOCK) {
      await delay(300);
      const task = mockTasks.find(t => t.projectId === projectId && t.taskId === taskId);
      if (!task) throw new Error("Zadanie nie istnieje.");
      
      task.assigneeId = assigneeId;
      task.updatedAt = new Date().toISOString();
      return task;
    }

    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/assign`, {
      method: 'PATCH',
      body: JSON.stringify({ assigneeId }),
    });
  },

  assignReviewer: async (projectId: number, taskId: number, reviewerId: string | null): Promise<Task> => {
    if (USE_MOCK) {
      await delay(300);
      const task = mockTasks.find(t => t.projectId === projectId && t.taskId === taskId);
      if (!task) throw new Error("Zadanie nie istnieje.");
      
      task.reviewerId = reviewerId;
      task.updatedAt = new Date().toISOString();
      return task;
    }

    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/reviewer`, {
      method: 'PATCH',
      body: JSON.stringify({ reviewerId }),
    });
  },

  requestClose: async (projectId: number, taskId: number): Promise<void> => {
    if (USE_MOCK) {
      await delay(300);
      const task = mockTasks.find(t => t.projectId === projectId && t.taskId === taskId);
      if (!task) throw new Error("Zadanie nie istnieje.");
      
      task.status = 'CLOSED';
      task.closedAt = new Date().toISOString();
      task.updatedAt = new Date().toISOString();
      return;
    }

    return apiFetch<void>(`/projects/${projectId}/tasks/${taskId}/request-close`, {
      method: 'POST',
    });
  }
};