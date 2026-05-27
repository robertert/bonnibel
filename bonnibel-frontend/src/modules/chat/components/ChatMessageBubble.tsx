import type { ChatMessage } from '@/types/domain'

type Props = {
  message: ChatMessage
  mine: boolean
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

export default function ChatMessageBubble({ message, mine }: Props) {
  return (
    <div className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
          mine
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-white border border-gray-200 text-gray-900 rounded-bl-md'
        }`}
      >
        <div className={`text-xs mb-0.5 font-medium ${mine ? 'text-blue-100' : 'text-gray-600'}`}>
          {message.authorId}
        </div>
        <div className="whitespace-pre-wrap break-words">{message.text}</div>
        <div className={`text-[10px] mt-1 text-right ${mine ? 'text-blue-200' : 'text-gray-500'}`}>
          {formatTime(message.createdAt)}
        </div>
      </div>
    </div>
  )
}
