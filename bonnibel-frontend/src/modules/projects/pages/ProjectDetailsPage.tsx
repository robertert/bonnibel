import { useParams } from 'react-router-dom'

export default function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold mb-4">Projekt #{projectId}</h1>
      <p className="text-gray-500">TODO: szczegóły projektu, edycja, usuwanie</p>
    </div>
  )
}
