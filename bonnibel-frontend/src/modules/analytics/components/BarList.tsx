type Entry = { label: string; value: number }

type Props = {
  entries: Entry[]
  emptyText?: string
}

export default function BarList({ entries, emptyText = 'Brak danych.' }: Props) {
  if (!entries.length) {
    return <p className="text-sm text-gray-500">{emptyText}</p>
  }
  const max = Math.max(...entries.map((e) => e.value), 1)
  return (
    <ul className="space-y-2">
      {entries.map((e) => {
        const pct = Math.round((e.value / max) * 100)
        return (
          <li key={e.label} className="text-sm">
            <div className="flex justify-between mb-1">
              <span className="font-medium text-gray-700">{e.label}</span>
              <span className="text-gray-500">{e.value}</span>
            </div>
            <div className="w-full h-2.5 bg-gray-100 rounded-full">
              <div
                className="h-2.5 bg-blue-500 rounded-full"
                style={{ width: `${pct}%` }}
              />
            </div>
          </li>
        )
      })}
    </ul>
  )
}
