import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

interface RiskSignal {
  signal: string
  severity: string
  source: string
  date: string
}

interface OpportunitySignal {
  signal: string
  impact: string
  source: string
}

interface Company {
  id: string
  name: string
  industry: string
  size: string
  location: string
  website: string
  tech_stack: string[]
  culture_summary: string
  financial_health: string
  risk_signals: RiskSignal[]
  opportunity_signals: OpportunitySignal[]
  research_data: Record<string, unknown>
  created_at: string
}

export default function CompaniesPage() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery<Company[]>({
    queryKey: ['companies'],
    queryFn: () => api.get('/companies'),
  })

  const researchAllMutation = useMutation({
    mutationFn: () => api.post('/companies/research'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['companies'] }),
  })

  const researchOneMutation = useMutation({
    mutationFn: (id: string) => api.post(`/companies/${id}/research`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['companies'] }),
  })

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">公司调研</h2>
        <button
          onClick={() => researchAllMutation.mutate()}
          disabled={researchAllMutation.isPending}
          className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {researchAllMutation.isPending ? '调研中...' : '批量调研 (LLM)'}
        </button>
      </div>

      {!data?.length ? (
        <p className="text-gray-500 text-center py-12">暂无公司数据，请先导入职位</p>
      ) : (
        <div className="space-y-4">
          {data.map((c) => (
            <div key={c.id} className="bg-white rounded-lg shadow p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold">{c.name}</h3>
                  <p className="text-sm text-gray-500">
                    {[c.industry, c.size, c.location].filter(Boolean).join(' · ')}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded font-medium ${
                    c.financial_health === 'strong' ? 'bg-green-100 text-green-700' :
                    c.financial_health === 'stable' ? 'bg-blue-100 text-blue-700' :
                    c.financial_health === 'concerning' ? 'bg-yellow-100 text-yellow-700' :
                    c.financial_health === 'critical' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {c.financial_health === 'strong' ? '财务健康' :
                     c.financial_health === 'stable' ? '财务稳定' :
                     c.financial_health === 'concerning' ? '需关注' :
                     c.financial_health === 'critical' ? '高风险' : '未知'}
                  </span>
                  <button
                    onClick={() => researchOneMutation.mutate(c.id)}
                    disabled={researchOneMutation.isPending}
                    className="text-xs text-indigo-600 hover:text-indigo-800"
                  >
                    深度调研
                  </button>
                </div>
              </div>

              {c.culture_summary && (
                <p className="text-sm text-gray-700 mb-3">{c.culture_summary}</p>
              )}

              {c.tech_stack.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {c.tech_stack.map((t: string) => (
                    <span key={t} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                {c.risk_signals.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-red-600 mb-1">Risk Signals</p>
                    {c.risk_signals.map((r, i) => (
                      <div key={i} className="text-xs text-gray-600 mb-1">
                        <span className={`inline-block w-2 h-2 rounded-full mr-1 ${
                          r.severity === 'critical' ? 'bg-red-500' :
                          r.severity === 'high' ? 'bg-red-400' :
                          r.severity === 'medium' ? 'bg-yellow-400' : 'bg-gray-300'
                        }`} />
                        {r.signal}
                        <span className="text-gray-400 ml-1">[{r.source}]</span>
                      </div>
                    ))}
                  </div>
                )}

                {c.opportunity_signals.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-green-600 mb-1">Opportunity Signals</p>
                    {c.opportunity_signals.map((o, i) => (
                      <div key={i} className="text-xs text-gray-600 mb-1">
                        <span className={`inline-block w-2 h-2 rounded-full mr-1 ${
                          o.impact === 'high' ? 'bg-green-500' : o.impact === 'medium' ? 'bg-green-400' : 'bg-green-300'
                        }`} />
                        {o.signal}
                        <span className="text-gray-400 ml-1">[{o.source}]</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
