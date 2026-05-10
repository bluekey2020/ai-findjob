import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'

interface NegotiationStrategy {
  offer: {
    company: string
    role: string
    salary: number
  }
  negotiation_strategy: {
    situation_assessment: {
      batna: string
      leverage_points: string[]
      weaknesses: string[]
      walk_away_number: number
      target_number: number
      optimistic_number: number
    }
    anchor_strategy: {
      who_should_anchor: string
      if_you_anchor: string
      if_they_anchor: string
    }
    ackerman_sequence: Array<{
      round: number
      offer: number
      script_cn: string
      script_en: string
    }>
    calibrated_questions: Array<{
      scenario: string
      question_cn: string
      question_en: string
      expected_response: string
    }>
    non_salary_levers: Array<{
      lever: string
      typical_value: string
      negotiation_tip: string
    }>
    objection_handling: Array<{
      objection: string
      response_cn: string
      response_en: string
    }>
    closing_script: {
      when_to_close: string
      script_cn: string
      script_en: string
    }
    cultural_notes: string
    risk_warnings: string[]
  }
  usage: Record<string, unknown>
}

export default function NegotiationPage() {
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [salary, setSalary] = useState(0)
  const [batna, setBatna] = useState('')
  const [strategy, setStrategy] = useState<NegotiationStrategy | null>(null)

  const negMutation = useMutation<NegotiationStrategy>({
    mutationFn: () => api.post('/offers/negotiate', {
      offer: { company, role, salary },
      batna,
    }),
    onSuccess: (data) => setStrategy(data),
  })

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">薪资谈判 (Chris Voss FBI)</h2>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">公司</label>
            <input value={company} onChange={(e) => setCompany(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">岗位</label>
            <input value={role} onChange={(e) => setRole(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Base 年薪</label>
            <input type="number" value={salary || ''} onChange={(e) => setSalary(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="mb-4">
          <label className="block text-sm text-gray-600 mb-1">BATNA (最佳替代方案)</label>
          <textarea value={batna} onChange={(e) => setBatna(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm" rows={2}
            placeholder="e.g. 另一个Offer / 留在现公司 / 休息充电"
          />
        </div>
        <button
          onClick={() => negMutation.mutate()}
          disabled={!company || !salary || negMutation.isPending}
          className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
        >
          {negMutation.isPending ? 'Chris Voss 为你制定策略...' : '生成谈判策略 (Opus)'}
        </button>
      </div>

      {strategy?.negotiation_strategy && (
        <div className="space-y-4">
          {strategy.negotiation_strategy.situation_assessment && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">形势评估</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">BATNA</p>
                  <p className="font-medium">{strategy.negotiation_strategy.situation_assessment.batna}</p>
                </div>
                <div>
                  <p className="text-gray-500">目标区间</p>
                  <p className="font-medium">
                    底线: {strategy.negotiation_strategy.situation_assessment.walk_away_number?.toLocaleString()} ·
                    目标: {strategy.negotiation_strategy.situation_assessment.target_number?.toLocaleString()} ·
                    乐观: {strategy.negotiation_strategy.situation_assessment.optimistic_number?.toLocaleString()}
                  </p>
                </div>
              </div>
              {strategy.negotiation_strategy.situation_assessment.leverage_points?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-1">谈判筹码</p>
                  {strategy.negotiation_strategy.situation_assessment.leverage_points.map((p, i) => (
                    <p key={i} className="text-sm text-green-700">• {p}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          {strategy.negotiation_strategy.anchor_strategy && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">锚定策略</h3>
              <p className="text-sm font-medium mb-2">
                应该由谁先出价: <span className="text-indigo-600">{strategy.negotiation_strategy.anchor_strategy.who_should_anchor}</span>
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-blue-50 rounded p-3">
                  <p className="font-medium text-blue-800 mb-1">如果你先出价</p>
                  <p className="text-blue-700 whitespace-pre-wrap">{strategy.negotiation_strategy.anchor_strategy.if_you_anchor}</p>
                </div>
                <div className="bg-green-50 rounded p-3">
                  <p className="font-medium text-green-800 mb-1">如果对方先出价</p>
                  <p className="text-green-700 whitespace-pre-wrap">{strategy.negotiation_strategy.anchor_strategy.if_they_anchor}</p>
                </div>
              </div>
            </div>
          )}

          {strategy.negotiation_strategy.ackerman_sequence && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Ackerman 出价序列</h3>
              <div className="space-y-3">
                {strategy.negotiation_strategy.ackerman_sequence.map((round, i) => (
                  <div key={i} className="border-l-2 border-indigo-300 pl-4">
                    <p className="text-sm font-medium">Round {round.round}: {round.offer?.toLocaleString()}</p>
                    <p className="text-xs text-gray-600 mt-1">CN: {round.script_cn}</p>
                    <p className="text-xs text-gray-500">EN: {round.script_en}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {strategy.negotiation_strategy.calibrated_questions && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">校准问题 (Calibrated Questions)</h3>
              <div className="space-y-3">
                {strategy.negotiation_strategy.calibrated_questions.map((q, i) => (
                  <div key={i} className="border rounded-lg p-3">
                    <p className="text-sm font-medium text-indigo-700 mb-1">{q.scenario}</p>
                    <p className="text-sm">CN: {q.question_cn}</p>
                    <p className="text-xs text-gray-500">EN: {q.question_en}</p>
                    <p className="text-xs text-gray-400 mt-1">预期反应: {q.expected_response}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {strategy.negotiation_strategy.objection_handling && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">异议处理</h3>
              {strategy.negotiation_strategy.objection_handling.map((o, i) => (
                <div key={i} className="border rounded-lg p-3 mb-2">
                  <p className="text-sm font-medium text-red-700">"{o.objection}"</p>
                  <p className="text-sm mt-1 text-green-700">→ CN: {o.response_cn}</p>
                  <p className="text-xs text-gray-500">→ EN: {o.response_en}</p>
                </div>
              ))}
            </div>
          )}

          {strategy.negotiation_strategy.non_salary_levers && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">非薪资谈判筹码</h3>
              <div className="grid grid-cols-2 gap-2">
                {strategy.negotiation_strategy.non_salary_levers.map((l, i) => (
                  <div key={i} className="border rounded p-3 text-sm">
                    <p className="font-medium">{l.lever}</p>
                    <p className="text-xs text-gray-500">{l.typical_value}</p>
                    <p className="text-xs text-indigo-600 mt-1">{l.negotiation_tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {strategy.negotiation_strategy.closing_script && (
            <div className="bg-indigo-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2 text-indigo-900">收尾话术</h3>
              <p className="text-xs text-gray-500 mb-2">{strategy.negotiation_strategy.closing_script.when_to_close}</p>
              <p className="text-sm text-indigo-800">CN: {strategy.negotiation_strategy.closing_script.script_cn}</p>
              <p className="text-xs text-indigo-600">EN: {strategy.negotiation_strategy.closing_script.script_en}</p>
            </div>
          )}

          {strategy.negotiation_strategy.risk_warnings?.length > 0 && (
            <div className="bg-red-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-red-800 mb-2">风险警告</h3>
              {strategy.negotiation_strategy.risk_warnings.map((w, i) => (
                <p key={i} className="text-sm text-red-700">• {w}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
