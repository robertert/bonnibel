import { useEffect, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { chatService, openTaskChatSocket } from '@/services/chatService'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { ChatMessage } from '@/types/domain'
import ChatMessageBubble from './ChatMessageBubble'

type Props = {
  projectId: number
  taskId: number
}

export default function TaskChat({ projectId, taskId }: Props) {
  const currentUserId = useAuthStore((s) => s.userId) ?? 'anon'
  const accessToken = useAuthStore((s) => s.accessToken)
  const queryClient = useQueryClient()
  const queryKey = ['chat', projectId, taskId] as const

  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)
  const scrollBoxRef = useRef<HTMLDivElement | null>(null)

  const {
    data: messages = [],
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey,
    queryFn: () => chatService.getTaskMessages(projectId, taskId),
  })

  const appendMessage = (msg: ChatMessage) => {
    queryClient.setQueryData<ChatMessage[]>(queryKey, (old = []) => {
      if (old.some((m) => m.messageId === msg.messageId)) return old
      return [...old, msg]
    })
  }

  useEffect(() => {
    const ws = openTaskChatSocket(
      taskId,
      (msg) => {
        queryClient.setQueryData<ChatMessage[]>(
          ['chat', projectId, taskId],
          (old: ChatMessage[] = []) => {
            if (old.some((m) => m.messageId === msg.messageId)) return old
            return [...old, msg]
          }
        )
      },
      accessToken,
    )
    return () => {
      ws?.close()
    }
  }, [projectId, taskId, accessToken, queryClient])

  useEffect(() => {
    const el = scrollBoxRef.current
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  }, [messages.length])

  const send = async () => {
    const text = draft.trim()
    if (!text || sending) return
    setSending(true)
    setSendError(null)
    try {
      const msg = await chatService.sendMessage(projectId, taskId, currentUserId, text)
      appendMessage(msg)
      setDraft('')
    } catch (err) {
      console.error('Nie udało się wysłać wiadomości', err)
      setSendError('Nie udało się wysłać wiadomości.')
    } finally {
      setSending(false)
    }
  }

  const onInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <section className="border border-gray-200 rounded-2xl bg-white shadow-sm overflow-hidden">
      <header className="px-4 py-3 border-b flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">Czat zadania</h2>
        <button
          type="button"
          onClick={() => refetch()}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          Odśwież
        </button>
      </header>

      <div
        ref={scrollBoxRef}
        className="h-80 overflow-y-auto p-4 space-y-2 bg-gray-50 overscroll-contain"
      >
        {isLoading && <p className="text-sm text-gray-500">Wczytywanie wiadomości…</p>}
        {isError && (
          <p className="text-sm text-red-600">Nie udało się pobrać wiadomości.</p>
        )}
        {!isLoading && messages.length === 0 && (
          <p className="text-sm text-gray-500">Brak wiadomości. Napisz pierwszą!</p>
        )}
        {messages.map((m) => (
          <ChatMessageBubble
            key={m.messageId}
            message={m}
            mine={m.authorId === currentUserId}
          />
        ))}
      </div>

      <div className="p-3 border-t">
        {sendError && (
          <p className="text-xs text-red-600 mb-2">{sendError}</p>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onInputKeyDown}
            placeholder="Napisz wiadomość…"
            className="flex-1 px-4 py-2 border border-gray-200 rounded-full text-sm bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="button"
            onClick={send}
            disabled={sending || !draft.trim()}
            className="px-5 py-2 text-sm text-white bg-blue-600 rounded-full hover:bg-blue-700 disabled:bg-blue-300 shadow-sm"
          >
            {sending ? 'Wysyłam…' : 'Wyślij'}
          </button>
        </div>
      </div>
    </section>
  )
}
