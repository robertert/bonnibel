import { apiFetch } from '@/lib/api'
import { API_BASE_URL, WS_BASE_URL, isUsingFastApiBackend } from '@/lib/env'
import type { ChatMessage } from '@/types/domain'

function jsonServerPath(projectId: number, taskId: number) {
  if (isUsingFastApiBackend()) {
    return `/api/projects/${projectId}/tasks/${taskId}/messages`
  }
  // json-server: bezpośrednio na kolekcji chatMessages z filtrem
  return `/chatMessages?taskId=${taskId}&_sort=createdAt&_order=asc`
}

function messageUrl(projectId: number, taskId: number, messageId: number) {
  if (isUsingFastApiBackend()) {
    return `/api/projects/${projectId}/tasks/${taskId}/messages/${messageId}`
  }
  return `/chatMessages/${messageId}`
}

// Wire format z backendu (snake_case w core/models.py → JSON FastAPI).
// json-server używa formy bliskiej naszej domenowej; obsługujemy obie.
type RawMessage = {
  id?: number
  messageId?: number
  message_id?: number
  taskId?: number
  task_id?: number
  authorId?: string
  author_id?: string
  text?: string
  createdAt?: string
  created_at?: string
}

function normalize(msg: RawMessage): ChatMessage {
  return {
    messageId: (msg.messageId ?? msg.message_id ?? msg.id) as number,
    taskId: (msg.taskId ?? msg.task_id) as number,
    authorId: (msg.authorId ?? msg.author_id) as string,
    text: msg.text as string,
    createdAt: (msg.createdAt ?? msg.created_at) as string,
  }
}

export const chatService = {
  getTaskMessages: async (projectId: number, taskId: number): Promise<ChatMessage[]> => {
    const raw = await apiFetch<RawMessage[]>(jsonServerPath(projectId, taskId))
    return raw.map(normalize)
  },

  sendMessage: async (
    projectId: number,
    taskId: number,
    authorId: string,
    text: string
  ): Promise<ChatMessage> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<ChatMessage>(
        `/api/projects/${projectId}/tasks/${taskId}/messages`,
        {
          method: 'POST',
          body: JSON.stringify({ text }),
        }
      )
    }

    // json-server: musimy sami złożyć obiekt (autorId, createdAt) i POST-ować na /chatMessages
    const payload = {
      taskId,
      authorId,
      text,
      createdAt: new Date().toISOString(),
    }
    const created = await apiFetch<RawMessage>('/chatMessages', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    return normalize(created)
  },

  // TODO: backend (app/core/models.py → ChatMessage) nie ma jeszcze pola
  // updated_at ani endpointu PATCH. Działa na json-server; po stronie FastAPI
  // wymaga dodania zarówno migracji jak i routera.
  updateMessage: async (
    projectId: number,
    taskId: number,
    messageId: number,
    text: string
  ): Promise<ChatMessage> => {
    const updated = await apiFetch<RawMessage>(
      messageUrl(projectId, taskId, messageId),
      {
        method: 'PATCH',
        body: JSON.stringify({ text }),
      }
    )
    return normalize(updated)
  },

  deleteMessage: async (
    projectId: number,
    taskId: number,
    messageId: number
  ): Promise<void> => {
    await apiFetch<unknown>(messageUrl(projectId, taskId, messageId), {
      method: 'DELETE',
    })
  },
}

export function openTaskChatSocket(
  taskId: number,
  onMessage: (msg: ChatMessage) => void,
  token: string | null
): WebSocket | null {
  if (!WS_BASE_URL) {
    return null
  }
  const url = new URL(`/api/ws/tasks/${taskId}/chat`, WS_BASE_URL.replace(/^ws/, 'http'))
  url.protocol = WS_BASE_URL.startsWith('wss') ? 'wss:' : 'ws:'
  if (token) url.searchParams.set('token', token)

  const ws = new WebSocket(url.toString())
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as ChatMessage
      onMessage(data)
    } catch (err) {
      console.warn('Niepoprawna wiadomość WS', event.data, err)
    }
  }
  return ws
}

// Re-export bez użycia, gdyby przyszły moduły potrzebowały bazowego URL.
export const _API_BASE_URL = API_BASE_URL
