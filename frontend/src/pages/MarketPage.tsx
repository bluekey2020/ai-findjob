import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

interface SalaryEstimate {
  role: string
  city: string
  experience_years: number
  company_size: string
  estimate: {
    low: number
    mid: number
    high: number
    confidence: number
    factors: string[]
    currency: string
    period: string
  }
  breakdown: {
    base: number
    city_modifier: number
    experience_modifier: number
    company_size_modifier: number
    skill_multiplier: number
  }
}

interface MarketAnalysis {
  analysis: Record<string, unknown>
  usage: Record<string, unknown>
}

export default function MarketPage() {
  const [role, setRole] = useState('python')
  const [city, setCity] = useState('Beijing')
  const [experience, setExperience] = useState(5)
  const [size, setSize] = useState('mid')
  const [skills, setSkills] = useState('')

  const { data: analysis, isLoading: analysisLoading, refetch: runAnalysis } = useQuery<MarketAnalysis>({
    queryKey: ['market-analysis'],
    queryFn: () => api.get('/market/analysis'),
    enabled: false,
  })

  const [salaryData, setSalaryData] = useState<SalaryEstimate | null>(null)
  const [salaryLoading, setSalaryLoading] = useState(false)

  const fetchSalary = async () => {
    setSalaryLoading(true)
    try {
      const params = new URLSearchParams({ role, city, experience_years: String(experience), company_size: size })
      if (skills) params.set('skills', skills)
      const data = await api.get<SalaryEstimate>(`/market/salary-estimate?${params}`)
      setSalaryData(data)
    } finally {
      setSalaryLoading(false)
    }
  }

  const formatMoney = (n: number) => {
    if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
    return n.toLocaleString()
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">市场分析</h2>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">薪资估算 (Zillow模式)</h3>

          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">岗位</label>
              <input
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. python, backend, frontend"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">城市</label>
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. Beijing, Shanghai"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">经验年限</label>
              <input
                type="number"
                value={experience}
                onChange={(e) => setExperience(Number(e.target.value))}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">公司规模</label>
              <select
                value={size}
                onChange={(e) => setSize(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="startup">创业公司</option>
                <option value="small">小型</option>
                <option value="mid">中型</option>
                <option value="large">大厂</option>
                <option value="enterprise">企业级</option>
                <option value="unicorn">独角兽</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">加分技能 (逗号分隔)</label>
              <input
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="ai, kubernetes, rust"
              />
            </div>
            <button
              onClick={fetchSalary}
              disabled={salaryLoading}
              className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
            >
              {salaryLoading ? '计算中...' : '估算薪资'}
            </button>
          </div>

          {salaryData && (
            <div className="mt-4 pt-4 border-t">
              <div className="grid grid-cols-3 gap-3 mb-3">
                <div className="text-center">
                  <p className="text-xs text-gray-400">Low</p>
                  <p className="text-lg font-bold text-gray-600">{formatMoney(salaryData.estimate.low)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Mid</p>
                  <p className="text-2xl font-bold text-indigo-600">{formatMoney(salaryData.estimate.mid)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">High</p>
                  <p className="text-lg font-bold text-gray-600">{formatMoney(salaryData.estimate.high)}</p>
                </div>
              </div>
              <p className="text-xs text-gray-400 text-center mb-3">
                {salaryData.estimate.currency} · {salaryData.estimate.period} · 置信度 {Math.round(salaryData.estimate.confidence * 100)}%
              </p>

              {salaryData.estimate.factors.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {salaryData.estimate.factors.map((f, i) => (
                    <span key={i} className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">{f}</span>
                  ))}
                </div>
              )}

              <div className="text-xs text-gray-500 space-y-1">
                <p>基准: {formatMoney(salaryData.breakdown.base)} | 城市系数: {salaryData.breakdown.city_modifier} | 经验系数: {salaryData.breakdown.experience_modifier}</p>
                <p>公司规模系数: {salaryData.breakdown.company_size_modifier} | 技能溢价: {salaryData.breakdown.skill_multiplier}x</p>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">市场分析 (LLM)</h3>
          <p className="text-sm text-gray-500 mb-4">
            由 Reid Hoffman AI 提供深度市场分析，包含供需比、竞争强度、新兴技能趋势、公司推荐。
          </p>
          <button
            onClick={() => runAnalysis()}
            className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm disabled:opacity-50"
          >
            {analysisLoading ? '分析中...' : '运行市场分析 (Opus)'}
          </button>

          {analysis && analysis.analysis && (
            <div className="mt-4 pt-4 border-t text-sm text-gray-700 whitespace-pre-wrap">
              {typeof analysis.analysis === 'string'
                ? analysis.analysis
                : JSON.stringify(analysis.analysis, null, 2)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
