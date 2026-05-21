import { useParams } from 'react-router-dom'

export default function TaskDetailsPage() {
  const { taskId } = useParams<{ taskId: string }>()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold mb-4">Zadanie #{taskId}</h1>
      <p className="text-gray-500">
        TODO: szczegóły zadania, historia, dokumentacja, PR, chat, subskrypcje
      </p>
    </div>
  )
}
