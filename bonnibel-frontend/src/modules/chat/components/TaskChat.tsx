type Props = {
  taskId: string
}

export default function TaskChat({ taskId }: Props) {
  return (
    <div className="border rounded p-4">
      <h2 className="font-semibold mb-2">Czat zadania #{taskId}</h2>
      <p className="text-gray-500 text-sm">TODO: wiadomości, wysyłanie, powiadomienia subów</p>
    </div>
  )
}
