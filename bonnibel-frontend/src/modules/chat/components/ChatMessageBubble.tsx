import { useEffect, useRef, useState } from 'react'
import type { ChatMessage } from '@/types/domain'

type Props = {
  message: ChatMessage
  mine: boolean
  onEdit?: (messageId: number, newText: string) => Promise<void> | void
  onDelete?: (messageId: number) => Promise<void> | void
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

export default function ChatMessageBubble({ message, mine, onEdit, onDelete }: Props) {
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(message.text)
  const [busy, setBusy] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus()
      textareaRef.current.selectionStart = textareaRef.current.value.length
    }
  }, [isEditing])

  const startEdit = () => {
    setDraft(message.text)
    setIsEditing(true)
  }

  const cancelEdit = () => {
    setDraft(message.text)
    setIsEditing(false)
  }

  const saveEdit = async () => {
    const trimmed = draft.trim()
    if (!onEdit || !trimmed || trimmed === message.text || busy) {
      if (trimmed === message.text) cancelEdit()
      return
    }
    setBusy(true)
    try {
      await onEdit(message.messageId, trimmed)
      setIsEditing(false)
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete || busy) return
    if (!window.confirm('Usunąć tę wiadomość?')) return
    setBusy(true)
    try {
      await onDelete(message.messageId)
    } finally {
      setBusy(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      saveEdit()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      cancelEdit()
    }
  }

  return (
    <div className={`group flex ${mine ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
          mine
            ? 'bg-blue-100 border border-blue-200 text-gray-900 rounded-br-md'
            : 'bg-white border border-gray-200 text-gray-900 rounded-bl-md'
        }`}
      >
        <div
          className={`text-xs mb-0.5 font-medium ${
            mine ? 'text-blue-700' : 'text-gray-600'
          }`}
        >
          {message.authorEmail ?? message.authorId}
        </div>

        {isEditing ? (
          <div className="space-y-2">
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKeyDown}
              rows={Math.min(6, Math.max(2, draft.split('\n').length))}
              className={`w-full rounded-md px-2 py-1 text-sm resize-none focus:outline-none ${
                mine
                  ? 'bg-white/95 text-gray-900'
                  : 'bg-gray-50 text-gray-900 border border-gray-200'
              }`}
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={cancelEdit}
                disabled={busy}
                className={`text-xs px-2 py-1 rounded ${
                  mine
                    ? 'bg-blue-500 hover:bg-blue-400 text-white'
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                }`}
              >
                Anuluj
              </button>
              <button
                type="button"
                onClick={saveEdit}
                disabled={busy || !draft.trim()}
                className={`text-xs px-2 py-1 rounded font-medium ${
                  mine
                    ? 'bg-white text-blue-700 hover:bg-blue-50 disabled:bg-blue-200 disabled:text-blue-500'
                    : 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300'
                }`}
              >
                {busy ? 'Zapisuję…' : 'Zapisz'}
              </button>
            </div>
          </div>
        ) : (
          <div className="whitespace-pre-wrap break-words">{message.text}</div>
        )}

        <div
          className={`flex items-center justify-between gap-3 text-[10px] mt-1 ${
            mine ? 'text-blue-700' : 'text-gray-500'
          }`}
        >
          <span>{formatTime(message.createdAt)}</span>

          {mine && !isEditing && (onEdit || onDelete) && (
            <span className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              {onEdit && (
                <button
                  type="button"
                  onClick={startEdit}
                  className={`hover:underline ${
                    mine ? 'text-blue-700' : 'text-gray-600'
                  }`}
                >
                  Edytuj
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={busy}
                  className={`hover:underline ${
                    mine ? 'text-red-600' : 'text-red-600'
                  }`}
                >
                  Usuń
                </button>
              )}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
