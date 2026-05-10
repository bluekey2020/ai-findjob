import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

interface AppItem {
  id: string
  job_id: string
  company: string
  role: string
  status: string
  resume_version: string | null
  cover_letter_version: string | null
  applied_date: string | null
  last_contact_date: string | null
  next_step: string | null
  notes: string | null
  batch_number: number | null
  updated_at: string | null
}

interface KanbanData {
  columns: Record<string, AppItem[]>
  counts: Record<string, number>
  total: number
  active: number
  rhythm: Record<string, number>
}

const COLUMN_LABELS: Record<string, string> = {
  wishlist: '待投',
  applied: '已投递',
  phone_screen: '电话面',
  onsite: '现场面',
  offer: 'Offer',
  accepted: '已接受',
  rejected: '被拒',
  withdrawn: '已撤回',
}

const COLUMN_COLORS: Record<string, string> = {
  wishlist: 'bg-gray-50 border-gray-200',
  applied: 'bg-blue-50 border-blue-200',
  phone_screen: 'bg-yellow-50 border-yellow-200',
  onsite: 'bg-purple-50 border-purple-200',
  offer: 'bg-green-50 border-green-200',
  accepted: 'bg-emerald-50 border-emerald-200',
  rejected: 'bg-red-50 border-red-200',
  withdrawn: 'bg-gray-50 border-gray-300',
}

export default function ApplicationsPage() {
  const queryClient = useQueryClient()
  const [feedbackAppId, setFeedbackAppId] = useState<string | null>(null)
  const [feedbackText, setFeedbackText] = useState('')
  const [skillGaps, setSkillGaps] = useState('')

  const { data, isLoading } = useQuery<KanbanData>({
    queryKey: ['applications-kanban'],
    queryFn: () => api.get('/applications/kanban'),
    refetchInterval: 15000,
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status, detail }: { id: string; status: string; detail?: string }) =>
      api.put(`/applications/${id}/status`, { new_status: status, detail }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['applications-kanban'] }),
  })

  const feedbackMutation = useMutation({
    mutationFn: ({ id, feedback, skill_gaps }: { id: string; feedback: string; skill_gaps: string[] }) =>
      api.post(`/applications/${id}/interview-feedback`, { feedback, skill_gaps }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications-kanban'] })
      setFeedbackAppId(null)
      setFeedbackText('')
      setSkillGaps('')
    },
  })

  const handleSubmitFeedback = () => {
    if (!feedbackAppId) return
    const gaps = skillGaps.split(',').map((s) => s.trim()).filter(Boolean)
    feedbackMutation.mutate({ id: feedbackAppId, feedback: feedbackText, skill_gaps: gaps })
  }

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  const statusOrder = ['wishlist', 'applied', 'phone_screen', 'onsite', 'offer', 'accepted', 'rejected', 'withdrawn']

  const moveApp = (appId: string, direction: 'left' | 'right') => {
    if (!data) return
    const app = Object.values(data.columns).flat().find((a) => a.id === appId)
    if (!app) return
    const currentIdx = statusOrder.indexOf(app.status)
    const newIdx = direction === 'right' ? currentIdx + 1 : currentIdx - 1
    if (newIdx < 0 || newIdx >= statusOrder.length) return
    statusMutation.mutate({ id: appId, status: statusOrder[newIdx] })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">投递看板</h2>
        <div className="flex gap-3 text-sm text-gray-500">
          <span>节奏: {data?.rhythm.total_per_week}封/周</span>
          <span>·</span>
          <span>活跃: {data?.active}</span>
          <span>·</span>
          <span>总计: {data?.total}</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {statusOrder.map((col) => {
          const apps = data?.columns[col] || []
          if (['rejected', 'withdrawn'].includes(col) && apps.length === 0) return null
          return (
            <div key={col} className={`rounded-lg border ${COLUMN_COLORS[col]} p-3`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">{COLUMN_LABELS[col]}</h3>
                <span className="text-xs bg-white rounded-full px-2 py-0.5">{apps.length}</span>
              </div>
              <div className="space-y-2">
                {apps.map((app) => (
                  <div key={app.id} className="bg-white rounded p-2 shadow-sm text-sm">
                    <p className="font-medium truncate">{app.role}</p>
                    <p className="text-xs text-gray-500">{app.company}</p>
                    {app.applied_date && (
                      <p className="text-xs text-gray-400">{app.applied_date}</p>
                    )}
                    {app.notes && (
                      <p className="text-xs text-gray-500 mt-1 truncate">{app.notes.slice(0, 60)}</p>
                    )}
                    <div className="flex gap-1 mt-2">
                      {(col === 'phone_screen' || col === 'onsite') && (
                        <button
                          onClick={() => {
                            setFeedbackAppId(app.id)
                            setFeedbackText('')
                            setSkillGaps('')
                          }}
                          className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                        >
                          反馈
                        </button>
                      )}
                      {col !== 'accepted' && col !== 'rejected' && col !== 'withdrawn' && (
                        <button
                          onClick={() => moveApp(app.id, 'right')}
                          className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 ml-auto"
                        >
                          →
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {apps.length === 0 && (
                  <p className="text-xs text-gray-400 text-center py-4">空</p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {feedbackAppId && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-3">面试反馈</h3>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={4}
              className="w-full border rounded-lg p-3 text-sm mb-3"
              placeholder="面试中遇到的问题和反馈..."
            />
            <input
              value={skillGaps}
              onChange={(e) => setSkillGaps(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-4"
              placeholder="发现的技能缺口 (逗号分隔)"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setFeedbackAppId(null)}
                className="px-4 py-2 text-sm border rounded-lg"
              >
                取消
              </button>
              <button
                onClick={handleSubmitFeedback}
                disabled={!feedbackText}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg disabled:opacity-50"
              >
                提交 (触发Loop A)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
