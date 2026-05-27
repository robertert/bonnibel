type Props = {
  label: string
  value: number | string
  tone?: 'default' | 'success' | 'warning' | 'info'
}

const TONES: Record<NonNullable<Props['tone']>, string> = {
  default: 'bg-white text-gray-900 border-gray-200',
  success: 'bg-green-50 text-green-800 border-green-200',
  warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  info: 'bg-blue-50 text-blue-800 border-blue-200',
}

export default function StatCard({ label, value, tone = 'default' }: Props) {
  return (
    <div className={`border rounded-2xl p-4 shadow-sm ${TONES[tone]}`}>
      <div className="text-xs uppercase tracking-wide opacity-70">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
    </div>
  )
}
