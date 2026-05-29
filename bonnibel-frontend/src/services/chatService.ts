import { apiFetch } from '@/lib/api'
import { WS_BASE_URL } from '@/lib/env'
import type { ChatMessage } from '@/types/domain'

// Ścieżki czatu wg bonnibel-backend/app/modules/chat/router.py (router pod prefiksem /api).
// Base URL w apiFetch zawiera już /api, więc tutaj ścieżki są bez wiodącego /api.
function messagesUrl(projectId: number, taskId: number) {
  return `/projects/${projectId}/tasks/${taskId}/messages`
}

function messageUrl(projectId: number, taskId: number, messageId: number) {
  return `${messagesUrl(projectId, taskId)}/${messageId}`
}

// Backend bywa niespójny w nazewnictwie: GET zwraca surowe ORM (snake_case),
// POST/PATCH zwracają dict w camelCase. Normalizujemy obie formy do domeny.
type RawMessage = {
  id?: number
  messageId?: number
  message_id?: number
  taskId?: number
  task_id?: number
  authorId?: string
  author_id?: string
  authorEmail?: string | null
  author_email?: string | null
  text?: string
  createdAt?: string
  created_at?: string
}

function normalize(msg: RawMessage): ChatMessage {
  return {
    messageId: (msg.messageId ?? msg.message_id ?? msg.id) as number,
    taskId: (msg.taskId ?? msg.task_id) as number,
    authorId: (msg.authorId ?? msg.author_id) as string,
    authorEmail: msg.authorEmail ?? msg.author_email ?? null,
    text: msg.text as string,
    createdAt: (msg.createdAt ?? msg.created_at) as string,
  }
}

export const chatService = {
  getTaskMessages: async (projectId: number, taskId: number): Promise<ChatMessage[]> => {
    const raw = await apiFetch<RawMessage[]>(messagesUrl(projectId, taskId))
    return raw.map(normalize)
  },

  // Uwaga: backend (chat/router.py:get_current_user) używa placeholdera autora,
  // więc parametr authorId nie trafia do bazy — autor ustalany jest po stronie API.
  sendMessage: async (
    projectId: number,
    taskId: number,
    _authorId: string,
    text: string
  ): Promise<ChatMessage> => {
    const created = await apiFetch<RawMessage>(messagesUrl(projectId, taskId), {
      method: 'POST',
      body: JSON.stringify({ text }),
    })
    return normalize(created)
  },

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

// Realtime czatu: backend nie ma jeszcze WebSocketu (notification/ws.py puste).
// Gdy WS_BASE_URL jest pusty, funkcja zwraca null (no-op) i UI działa na refetch.
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
