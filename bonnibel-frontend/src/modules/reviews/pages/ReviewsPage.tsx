import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectService } from '@/services/projectService'
import { taskService } from '@/services/taskService'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { Task } from '@/types/domain'

interface ReviewItem {
  task: Task
  projectName: string
}

export default function ReviewsPage() {
  const userId = useAuthStore((s) => s.userId)
  const [items, setItems] = useState<ReviewItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) {
      setLoading(false)
      return
    }
    setLoading(true)
    projectService.list()
      .then(async (projects) => {
        const lists = await Promise.all(
          projects.map(async (p) => {
            const tasks = await taskService
              .getProjectTasks(p.projectId, { reviewerId: userId, status: 'IN_REVIEW' })
              .catch(() => [] as Task[])
            return tasks.map((task) => ({ task, projectName: p.name }))
          })
        )
        setItems(lists.flat())
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [userId])

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-semibold mb-2">Do recenzji</h1>
      <p className="text-gray-500 text-sm mb-6">Zadania w statusie review, w których jesteś recenzentem.</p>

      {loading ? (
        <p className="text-gray-500">Wczytywanie…</p>
      ) : items.length === 0 ? (
        <p className="text-gray-500">Brak zadań oczekujących na Twoją recenzję.</p>
      ) : (
        <ul className="space-y-3">
          {items.map(({ task, projectName }) => (
            <li key={task.taskId}>
              <Link
                to={`/projects/${task.projectId}/tasks/${task.taskId}`}
                className="block rounded-xl border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium text-gray-900">{task.title}</span>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">
                    IN_REVIEW
                  </span>
                </div>
                <div className="mt-1 text-xs text-gray-400">
                  {projectName} · {task.jiraIssueKey ?? `#${task.taskId}`}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
