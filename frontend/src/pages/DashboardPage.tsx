import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

interface Achievement {
  name: string
  description: string
  xp: number
}

interface TimelineEntry {
  date: string
  phase: number | null
  activities: string[]
  mood: string | null
}

interface Dashboard {
  current_phase: number
  days_active: number
  streak: number
  avg_match_score: number
  funnel_data: Record<string, number>
  xp_total: number
  achievements: Achievement[]
  all_achievements: Achievement[]
  timeline: TimelineEntry[]
}

interface StepStatus {
  step: number
  name: string
  done: boolean
}

interface NextAction {
  step: number
  name: string
  api: string
  route: string
}

interface Guide {
  current_phase: number
  current_step: number
  progress_pct: number
  steps: StepStatus[]
  next_action: NextAction | null
  has_offers: boolean
}

const MOOD_EMOJI: Record<string, string> = {
  excited: '🤩',
  confident: '😎',
  neutral: '😐',
  anxious: '😰',
  frustrated: '😤',
}

const STEP_ROUTES: Record<number, string> = {
  1: '/profile',
  2: '/profile',
  3: '/profile',
  4: '/jobs',
  5: '/jobs',
  6: '/interviews',
}

export default function DashboardPage() {
  const navigate = useNavigate()

  const { data, isLoading } = useQuery<Dashboard>({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/dashboard'),
    refetchInterval: 30000,
  })

  const { data: guide } = useQuery<Guide>({
    queryKey: ['guide'],
    queryFn: () => api.get('/phases/guide'),
    refetchInterval: 15000,
  })

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  const earnedNames = new Set((data?.achievements || []).map((a) => a.name))

  return (
    <div>
      {/* 6-step demo flow wizard */}
      {guide && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">求职进度</h3>
            <span className="text-sm text-indigo-600 font-medium">{guide.progress_pct}%</span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-100 rounded-full h-2 mb-6">
            <div
              className="bg-indigo-500 rounded-full h-2 transition-all duration-500"
              style={{ width: `${guide.progress_pct}%` }}
            />
          </div>

          {/* Steps */}
          <div className="grid grid-cols-6 gap-2">
            {guide.steps.map((s) => {
              const isCurrent = s.step === guide.current_step
              const isDone = s.done
              return (
                <button
                  key={s.step}
                  onClick={() => navigate(STEP_ROUTES[s.step])}
                  className={`flex flex-col items-center p-3 rounded-lg transition-colors text-center ${
                    isCurrent
                      ? 'bg-indigo-50 ring-2 ring-indigo-300'
                      : isDone
                        ? 'bg-green-50 hover:bg-green-100'
                        : 'bg-gray-50 opacity-50'
                  }`}
                >
                  <span className="text-lg mb-1">
                    {isDone ? '✓' : isCurrent ? '→' : '○'}
                  </span>
                  <span className={`text-xs font-medium ${
                    isCurrent ? 'text-indigo-700' : isDone ? 'text-green-700' : 'text-gray-400'
                  }`}>
                    {s.step}
                  </span>
                  <span className={`text-xs mt-0.5 ${
                    isCurrent ? 'text-indigo-600 font-medium' : 'text-gray-500'
                  }`}>
                    {s.name}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Next action hint */}
          {guide.next_action && (
            <div className="mt-4 p-3 bg-indigo-50 rounded-lg flex items-center justify-between">
              <div>
                <span className="text-xs text-indigo-500">下一步</span>
                <p className="text-sm font-medium text-indigo-700">
                  Step {guide.next_action.step}: {guide.next_action.name}
                </p>
                <code className="text-xs text-indigo-400 mt-0.5 block">{guide.next_action.api}</code>
              </div>
              <button
                onClick={() => navigate(guide.next_action!.route)}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                前往
              </button>
            </div>
          )}
        </div>
      )}

      <h2 className="text-2xl font-bold mb-6">求职仪表盘</h2>

      <div className="grid grid-cols-5 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">当前阶段</p>
          <p className="text-2xl font-bold text-indigo-600">Phase {data?.current_phase ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">活跃天数</p>
          <p className="text-2xl font-bold">{data?.days_active ?? 0}</p>
          {data?.streak ? (
            <p className="text-xs text-orange-500">连续 {data.streak} 天 🔥</p>
          ) : null}
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">平均匹配分</p>
          <p className="text-2xl font-bold text-green-600">{data?.avg_match_score ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">经验值</p>
          <p className="text-2xl font-bold text-amber-600">{data?.xp_total ?? 0} XP</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">成就</p>
          <p className="text-2xl font-bold text-purple-600">
            {data?.achievements.length ?? 0}/{data?.all_achievements.length ?? 0}
          </p>
        </div>
      </div>

      {data?.funnel_data && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">求职漏斗</h3>
          <div className="space-y-2">
            {Object.entries(data.funnel_data).map(([key, val]) => (
              <div key={key} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-20 capitalize">{key}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-4">
                  <div
                    className="bg-indigo-500 rounded-full h-4 transition-all"
                    style={{ width: `${Math.min(100, (val / Math.max(...Object.values(data.funnel_data), 1)) * 100)}%` }}
                  />
                </div>
                <span className="text-sm font-medium w-8 text-right">{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data?.achievements && data.achievements.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">已解锁成就</h3>
          <div className="grid grid-cols-4 gap-3">
            {data.achievements.map((a) => (
              <div key={a.name} className="border border-amber-200 bg-amber-50 rounded-lg p-3 text-center">
                <p className="font-medium text-sm text-amber-900">{a.name}</p>
                <p className="text-xs text-amber-700 mt-1">{a.description}</p>
                <p className="text-xs text-amber-500 mt-1">+{a.xp} XP</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        {data?.timeline && data.timeline.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">活动时间线</h3>
            <div className="space-y-2">
              {data.timeline.slice(0, 7).map((t, i) => (
                <div key={i} className="flex items-start gap-3 text-sm">
                  <span className="text-xs text-gray-400 w-20 flex-shrink-0">{t.date}</span>
                  <span className="text-xs text-gray-400 w-12">P{t.phase}</span>
                  <span>
                    {t.mood ? `${MOOD_EMOJI[t.mood] || ''} ` : ''}
                    {(t.activities || []).join(', ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {data?.all_achievements && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">全部成就 ({earnedNames.size}/{data.all_achievements.length})</h3>
            <div className="space-y-1 max-h-80 overflow-y-auto">
              {data.all_achievements.map((a) => (
                <div key={a.name} className={`flex items-center justify-between text-sm py-1 px-2 rounded ${
                  earnedNames.has(a.name) ? 'bg-amber-50' : 'opacity-40'
                }`}>
                  <span>
                    {earnedNames.has(a.name) ? '🏆 ' : '🔒 '}
                    {a.name}
                  </span>
                  <span className="text-xs text-gray-500">{a.description} · +{a.xp}XP</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
