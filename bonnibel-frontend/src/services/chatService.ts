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

type RawMessage = Partial<ChatMessage> & { id?: number }

function normalize(msg: RawMessage): ChatMessage {
  return {
    messageId: (msg.messageId ?? msg.id) as number,
    taskId: msg.taskId as number,
    authorId: msg.authorId as string,
    text: msg.text as string,
    createdAt: msg.createdAt as string,
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
