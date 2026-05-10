import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'

interface Offer {
  company: string
  role: string
  salary: number
  bonus_pct: number
  equity: string
  sign_on: number
  location: string
  remote_policy: string
}

interface EvaluationResult {
  offers_count: number
  evaluation: {
    offers_compared: Array<Record<string, unknown>>
    dimension_weights: Record<string, number>
    decision_matrix: Array<{
      dimension: string
      weight: number
      scores: Record<string, number>
    }>
    weighted_totals: Record<string, number>
    bias_corrections_applied: Array<{
      bias: string
      description: string
      correction_action: string
      impact_on_decision: string
    }>
    arguments_against_each: Record<string, string[]>
    gains_losses_symmetry: Array<{
      option: string
      gains: string[]
      losses: string[]
    }>
    recommendation: string
    timeline_strategy: string
    red_flags_per_offer: Record<string, string[]>
  }
  usage: Record<string, unknown>
}

const DIMENSION_NAMES: Record<string, string> = {
  salary_equity: '薪资与股权',
  growth_potential: '成长空间',
  culture_team: '文化与团队',
  wlb_benefits: 'WLB与福利',
  stability_risk: '稳定性与风险',
  location_commute: '地理与通勤',
  brand_network: '品牌与背书',
}

export default function OffersPage() {
  const [offers, setOffers] = useState<Offer[]>([
    { company: '', role: '', salary: 0, bonus_pct: 0, equity: '', sign_on: 0, location: '', remote_policy: 'onsite' }
  ])

  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null)

  const evalMutation = useMutation<EvaluationResult>({
    mutationFn: () => api.post('/offers/evaluate', offers),
    onSuccess: (data) => setEvaluation(data),
  })

  const addOffer = () => {
    if (offers.length >= 5) return
    setOffers([...offers, { company: '', role: '', salary: 0, bonus_pct: 0, equity: '', sign_on: 0, location: '', remote_policy: 'onsite' }])
  }

  const updateOffer = (idx: number, field: keyof Offer, value: string | number) => {
    const updated = [...offers]
    updated[idx] = { ...updated[idx], [field]: value }
    setOffers(updated)
  }

  const removeOffer = (idx: number) => {
    if (offers.length <= 1) return
    setOffers(offers.filter((_, i) => i !== idx))
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Offer 评估 (Daniel Kahneman AI)</h2>

      <div className="space-y-4 mb-6">
        {offers.map((o, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Offer {String.fromCharCode(65 + i)}</h3>
              <button onClick={() => removeOffer(i)} className="text-xs text-red-500 hover:text-red-700">
                移除
              </button>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">公司</label>
                <input value={o.company} onChange={(e) => updateOffer(i, 'company', e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">岗位</label>
                <input value={o.role} onChange={(e) => updateOffer(i, 'role', e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">年薪 (Base)</label>
                <input type="number" value={o.salary || ''} onChange={(e) => updateOffer(i, 'salary', Number(e.target.value))}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">奖金%</label>
                <input type="number" value={o.bonus_pct || ''} onChange={(e) => updateOffer(i, 'bonus_pct', Number(e.target.value))}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">股权</label>
                <input value={o.equity} onChange={(e) => updateOffer(i, 'equity', e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm" placeholder="e.g. 1000 RSU" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">签约费</label>
                <input type="number" value={o.sign_on || ''} onChange={(e) => updateOffer(i, 'sign_on', Number(e.target.value))}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">地点</label>
                <input value={o.location} onChange={(e) => updateOffer(i, 'location', e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Remote</label>
                <select value={o.remote_policy} onChange={(e) => updateOffer(i, 'remote_policy', e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm">
                  <option value="onsite">Onsite</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="remote">Remote</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mb-6">
        <button onClick={addOffer} className="px-4 py-2 text-sm border border-dashed border-gray-400 rounded-lg hover:bg-gray-50">
          + Add Offer
        </button>
        <button
          onClick={() => evalMutation.mutate()}
          disabled={evalMutation.isPending || !offers[0].company}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
        >
          {evalMutation.isPending ? 'Kahneman 为你分析中...' : '对比分析 (Opus)'}
        </button>
      </div>

      {evaluation?.evaluation && (
        <div className="space-y-4">
          {/* Decision Matrix */}
          {evaluation.evaluation.decision_matrix && (
            <div className="bg-white rounded-lg shadow p-6 overflow-x-auto">
              <h3 className="text-lg font-semibold mb-4">决策矩阵</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">维度</th>
                    <th className="text-center py-2">权重</th>
                    {offers.map((o, i) => (
                      <th key={i} className="text-center py-2">{o.company || `Offer ${String.fromCharCode(65 + i)}`}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {evaluation.evaluation.decision_matrix.map((row, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-2">{DIMENSION_NAMES[row.dimension] || row.dimension}</td>
                      <td className="text-center">{row.weight}%</td>
                      {Object.entries(row.scores).map(([company, score]) => (
                        <td key={company} className="text-center">
                          <span className={`font-medium ${score >= 8 ? 'text-green-600' : score >= 5 ? 'text-yellow-600' : 'text-red-600'}`}>
                            {score}/10
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                  {evaluation.evaluation.weighted_totals && (
                    <tr className="bg-indigo-50 font-bold">
                      <td className="py-2">加权总分</td>
                      <td className="text-center">100%</td>
                      {Object.entries(evaluation.evaluation.weighted_totals).map(([company, total]) => (
                        <td key={company} className="text-center text-indigo-700">
                          {typeof total === 'number' ? total.toFixed(1) : total}
                        </td>
                      ))}
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Bias Corrections */}
          {evaluation.evaluation.bias_corrections_applied && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">6 层认知偏差纠正</h3>
              <div className="grid grid-cols-2 gap-3">
                {evaluation.evaluation.bias_corrections_applied.map((b, i) => (
                  <div key={i} className="border rounded-lg p-3">
                    <p className="font-medium text-sm">{b.bias}</p>
                    <p className="text-xs text-gray-500 mt-1">{b.description}</p>
                    <div className="mt-2 text-xs bg-blue-50 text-blue-700 p-2 rounded">
                      {b.correction_action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Arguments Against */}
          {evaluation.evaluation.arguments_against_each && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">反方论据 (对抗确认偏差)</h3>
              {Object.entries(evaluation.evaluation.arguments_against_each).map(([company, args]) => (
                <div key={company} className="mb-3">
                  <p className="font-medium text-sm text-red-700">{company}</p>
                  {(args as string[]).map((arg: string, i: number) => (
                    <p key={i} className="text-sm text-gray-600 ml-4">• {arg}</p>
                  ))}
                </div>
              ))}
            </div>
          )}

          {/* Recommendation */}
          {evaluation.evaluation.recommendation && (
            <div className="bg-indigo-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-indigo-900">分析建议</h3>
              <p className="text-indigo-800 whitespace-pre-wrap">{evaluation.evaluation.recommendation}</p>
            </div>
          )}

          {/* Timeline Strategy */}
          {evaluation.evaluation.timeline_strategy && (
            <div className="bg-green-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-green-900">时间线策略</h3>
              <p className="text-green-800 whitespace-pre-wrap">{evaluation.evaluation.timeline_strategy}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
