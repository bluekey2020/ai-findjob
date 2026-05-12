import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

interface MatchBreakdown {
  jd_match: number
  preference_match: number
  company_health: number
  freshness: number
}

interface Job {
  id: string
  title: string
  company: string
  location: string
  platform: string
  salary_range: string
  match_score: number
  match_breakdown: MatchBreakdown
  match_reasons?: string[]
  missing_skills?: string[]
  fraud_score: number
  fraud_flags?: string[]
  dealbreaker_flags?: string[]
  status: string
  source_type: string
  description: string
  requirements: string[]
  tags: string[]
}

interface SearchResult {
  total: number
  top_picks: number
  mid_tier: number
  flagged: number
  jobs: Job[]
  stats: {
    avg_match_score: number
    avg_fraud_score: number
    top_tier_count: number
    mid_tier_count: number
    flagged_count: number
  }
}

interface ApplyResult {
  job_id: string
  title: string
  company: string
  application: {
    id: string
    status: string
    batch_number: number
  }
  tailored_resume?: Record<string, unknown>
  cover_letter?: Record<string, unknown>
}

export default function JobsPage() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState('all')
  const [showImport, setShowImport] = useState(false)
  const [importText, setImportText] = useState('')
  const [applyingJob, setApplyingJob] = useState<string | null>(null)
  const [applyResults, setApplyResults] = useState<Record<string, ApplyResult>>({})

  const { data, isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => api.get('/jobs?limit=100'),
  })

  const searchMutation = useMutation<SearchResult>({
    mutationFn: () => api.post('/jobs/search'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const importMutation = useMutation({
    mutationFn: (jobs: object[]) => api.post('/jobs/import', jobs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setShowImport(false)
      setImportText('')
    },
  })

  const applyMutation = useMutation<ApplyResult>({
    mutationFn: (jobId: string) => api.post(`/jobs/${jobId}/apply`),
    onSuccess: (result) => {
      setApplyResults((prev) => ({ ...prev, [result.job_id]: result }))
      setApplyingJob(null)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      queryClient.invalidateQueries({ queryKey: ['guide'] })
    },
  })

  const handleImport = () => {
    try {
      const jobs = JSON.parse(importText)
      const arr = Array.isArray(jobs) ? jobs : [jobs]
      importMutation.mutate(arr)
    } catch {
      alert('JSON 格式错误')
    }
  }

  const filtered = (data || []).filter((j) => {
    if (filter === 'all') return true
    if (filter === 'top') return j.match_score >= 70 && j.fraud_score < 20
    if (filter === 'mid') return j.match_score >= 40 && j.match_score < 70
    if (filter === 'flagged') return j.fraud_score >= 50 || j.match_score < 40
    if (filter === 'applied') return j.status === 'applied'
    if (filter === 'skipped') return j.status === 'skipped'
    return true
  })

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">职位浏览</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowImport(!showImport)}
            className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            导入职位
          </button>
          <button
            onClick={() => searchMutation.mutate()}
            disabled={searchMutation.isPending}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {searchMutation.isPending ? '匹配计算中...' : '智能匹配'}
          </button>
        </div>
      </div>

      {searchMutation.data && (
        <div className="grid grid-cols-4 gap-3 mb-6">
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <p className="text-xs text-green-600 mb-1">Top Picks</p>
            <p className="text-xl font-bold text-green-700">{searchMutation.data.top_picks}</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3 text-center">
            <p className="text-xs text-yellow-600 mb-1">Mid Tier</p>
            <p className="text-xl font-bold text-yellow-700">{searchMutation.data.mid_tier}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-3 text-center">
            <p className="text-xs text-red-600 mb-1">Flagged</p>
            <p className="text-xl font-bold text-red-700">{searchMutation.data.flagged}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <p className="text-xs text-blue-600 mb-1">平均匹配</p>
            <p className="text-xl font-bold text-blue-700">{searchMutation.data.stats.avg_match_score}</p>
          </div>
        </div>
      )}

      {showImport && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h3 className="font-semibold mb-2">批量导入职位 (JSON)</h3>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            rows={6}
            className="w-full border rounded-lg p-3 text-sm font-mono"
            placeholder='[{"title": "Python Developer", "company": "Example Inc", "location": "Beijing", ...}]'
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleImport}
              disabled={importMutation.isPending}
              className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {importMutation.isPending ? '导入中...' : '导入'}
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        {['all', 'top', 'mid', 'flagged', 'applied', 'skipped'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 text-sm rounded-full ${
              filter === f ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'all' ? '全部' : f === 'top' ? 'Top' : f === 'mid' ? 'Mid' : f === 'flagged' ? '可疑' : f === 'applied' ? '已投' : '已跳'}
          </button>
        ))}
      </div>

      {!filtered.length ? (
        <p className="text-gray-500 text-center py-12">
          {!data?.length ? '暂无职位数据，请先导入职位' : '没有匹配当前筛选条件的职位'}
        </p>
      ) : (
        <div className="space-y-3">
          {filtered.map((job) => {
            const isApplied = job.status === 'applied' || !!applyResults[job.id]
            const isApplying = applyingJob === job.id
            const result = applyResults[job.id]

            return (
              <div key={job.id} className={`bg-white rounded-lg shadow p-4 transition-shadow ${isApplied ? 'ring-1 ring-green-300' : 'hover:shadow-md'}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg">{job.title}</h3>
                      {job.fraud_score > 20 && (
                        <span className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-700">
                          ⚠ 欺诈风险 {job.fraud_score}
                        </span>
                      )}
                      {job.dealbreaker_flags?.length > 0 && (
                        <span className="text-xs px-2 py-0.5 rounded bg-red-200 text-red-800">
                          Dealbreaker
                        </span>
                      )}
                      {isApplied && (
                        <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">
                          ✓ 已投递
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      {job.company} · {job.location}{job.salary_range ? ` · ${job.salary_range}` : ''}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      来源: {job.platform} · {job.source_type}
                    </p>

                    {job.match_breakdown && (
                      <div className="mt-2 flex gap-4 text-xs text-gray-500">
                        <span>JD匹配: {job.match_breakdown.jd_match}%</span>
                        <span>偏好匹配: {job.match_breakdown.preference_match}%</span>
                        <span>公司健康: {job.match_breakdown.company_health}%</span>
                        <span>新鲜度: {job.match_breakdown.freshness}%</span>
                      </div>
                    )}

                    {(job.match_reasons?.length > 0 || job.missing_skills?.length > 0) && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {job.match_reasons?.map((r) => (
                          <span key={r} className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">
                            ✓ {r}
                          </span>
                        ))}
                        {job.missing_skills?.map((s) => (
                          <span key={s} className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded">
                            ✗ {s}
                          </span>
                        ))}
                      </div>
                    )}

                    {job.fraud_flags?.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {job.fraud_flags.map((flag, i) => (
                          <p key={i} className="text-xs text-red-600">{flag}</p>
                        ))}
                      </div>
                    )}

                    {/* Apply result summary */}
                    {result && (
                      <div className="mt-3 p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-800">
                          ✓ 投递成功 — Batch #{result.application.batch_number}
                        </p>
                        {result.tailored_resume && (
                          <p className="text-xs text-green-600 mt-1">定制简历已生成</p>
                        )}
                        {result.cover_letter && (
                          <p className="text-xs text-green-600">求职信已生成</p>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-2 ml-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-indigo-600">{job.match_score}</p>
                      <p className="text-xs text-gray-400">匹配分</p>
                    </div>
                    {!isApplied ? (
                      <div className="flex gap-1">
                        <button
                          onClick={() => api.put(`/jobs/${job.id}`, { status: 'skipped' }).then(() => {
                            queryClient.invalidateQueries({ queryKey: ['jobs'] })
                          })}
                          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                        >
                          跳过
                        </button>
                        <button
                          onClick={() => {
                            setApplyingJob(job.id)
                            applyMutation.mutate(job.id)
                          }}
                          disabled={isApplying}
                          className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                        >
                          {isApplying ? '投递中...' : '投递 →'}
                        </button>
                      </div>
                    ) : (
                      <span className="text-sm text-green-600 font-medium">已投递</span>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Applying overlay */}
      {applyingJob && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center">
            <div className="animate-spin text-4xl mb-4">⏳</div>
            <h3 className="text-lg font-semibold mb-2">正在投递...</h3>
            <p className="text-sm text-gray-500">
              AI 正在为该职位定制简历和求职信，请稍候
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
