import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

interface SkillGap {
  skill: string
  demand_count: number
  importance: number
  user_has: boolean
  user_level: string | null
  user_years: number | null
  gap_size: number
  heat_score: number
  priority: string
}

interface SkillGapData {
  user_skills: Array<{ name: string; level: string; years: number; category: string }>
  market_demand_skills: Array<[string, number]>
  gaps: SkillGap[]
  total_jobs_analyzed: number
  summary: {
    p0_gaps: number
    p1_gaps: number
    p2_gaps: number
    overall_readiness: number
  }
}

interface HeatmapCategory {
  name: string
  skills: SkillGap[]
  avg_heat: number
}

interface HeatmapData {
  categories: HeatmapCategory[]
  max_heat: number
  summary: {
    p0_gaps: number
    p1_gaps: number
    p2_gaps: number
    overall_readiness: number
  }
}

const PRIORITY_COLORS: Record<string, string> = {
  P0: 'bg-red-500',
  P1: 'bg-orange-400',
  P2: 'bg-yellow-400',
}

export default function SkillGapPage() {
  const { data, isLoading } = useQuery<SkillGapData>({
    queryKey: ['skill-gaps'],
    queryFn: () => api.get('/skill-gaps'),
  })

  const { data: heatmap } = useQuery<HeatmapData>({
    queryKey: ['skill-gaps-heatmap'],
    queryFn: () => api.get('/skill-gaps/heatmap'),
  })

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">技能缺口分析</h2>

      {data && (
        <>
          <div className="grid grid-cols-4 gap-3 mb-6">
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-xs text-gray-500 mb-1">整体就绪度</p>
              <p className="text-2xl font-bold text-indigo-600">{data.summary.overall_readiness}%</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-xs text-red-600 mb-1">P0 紧急缺口</p>
              <p className="text-2xl font-bold text-red-700">{data.summary.p0_gaps}</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <p className="text-xs text-orange-600 mb-1">P1 重要缺口</p>
              <p className="text-2xl font-bold text-orange-700">{data.summary.p1_gaps}</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-xs text-yellow-600 mb-1">P2 次要缺口</p>
              <p className="text-2xl font-bold text-yellow-700">{data.summary.p2_gaps}</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">
              技能清单 ({data.user_skills.length} 项) · 分析岗位: {data.total_jobs_analyzed}
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.user_skills.map((s) => (
                <span key={s.name} className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
                  {s.name} · {s.level} · {s.years}yr
                </span>
              ))}
            </div>
          </div>
        </>
      )}

      {heatmap && heatmap.categories.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">技能热力图</h3>
          <div className="space-y-2">
            {heatmap.categories.map((cat) => (
              <div key={cat.name} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium">{cat.name}</h4>
                  <span className="text-xs text-gray-400">avg heat: {cat.avg_heat}</span>
                </div>
                <div className="space-y-1">
                  {cat.skills.map((g) => (
                    <div key={g.skill} className="flex items-center gap-2">
                      <span className="text-xs w-24 truncate">{g.skill}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-3">
                        <div
                          className={`${PRIORITY_COLORS[g.priority] || 'bg-gray-400'} rounded-full h-3 transition-all`}
                          style={{ width: `${Math.min(100, (g.heat_score / heatmap.max_heat) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs w-8 text-right font-mono">{g.heat_score}</span>
                      <span className={`text-xs w-6 ${g.priority === 'P0' ? 'text-red-600 font-bold' : 'text-gray-400'}`}>
                        {g.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data && data.gaps.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">缺口详情</h3>
          <div className="space-y-2">
            {data.gaps.map((g) => (
              <div key={g.skill} className="flex items-center gap-3 border-b pb-2 text-sm">
                <span className={`w-2 h-2 rounded-full ${PRIORITY_COLORS[g.priority] || 'bg-gray-400'}`} />
                <span className="w-32 font-medium">{g.skill}</span>
                <span className="text-gray-500">需求: {g.demand_count}次</span>
                {g.user_has ? (
                  <span className="text-green-600">
                    已有 · {g.user_level} · {g.user_years}yr
                  </span>
                ) : (
                  <span className="text-red-500 font-medium">缺失</span>
                )}
                <span className="ml-auto font-mono text-xs">
                  heat: {g.heat_score}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {(!data || data.gaps.length === 0) && (
        <p className="text-center text-gray-400 py-12">
          暂无技能缺口数据 — 请先在 Phase 2 搜索职位后再查看
        </p>
      )}
    </div>
  )
}
