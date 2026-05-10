import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'

interface InterviewPrep {
  company: string
  role: string
  interview_type: string
  prep_plan: {
    prep_summary?: string
    technical_topics?: Array<{
      topic: string
      importance: string
      study_resources: string[]
      practice_problems: string[]
    }>
    behavioral_stories?: Array<{
      theme: string
      star_framework: {
        situation: string
        task: string
        action: string
        result: string
      }
    }>
    questions_to_ask?: string[]
    mock_interview_questions?: Array<{
      question: string
      category: string
      difficulty: string
      hints: string[]
    }>
    skill_gaps_identified?: string[]
    company_specific_tips?: string[]
    prep_timeline?: string
  }
  usage: Record<string, unknown>
  has_company_research: boolean
}

interface Job {
  id: string
  title: string
  company: string
  status: string
}

export default function InterviewPage() {
  const [selectedJobId, setSelectedJobId] = useState('')
  const [interviewType, setInterviewType] = useState('full_loop')
  const [prepData, setPrepData] = useState<InterviewPrep | null>(null)

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => api.get('/jobs?status=applied'),
  })

  const prepMutation = useMutation<InterviewPrep>({
    mutationFn: async () => {
      const params = new URLSearchParams({ job_id: selectedJobId, interview_type: interviewType })
      return api.post(`/interviews/prep?${params}`)
    },
    onSuccess: (data) => setPrepData(data),
  })

  const appliedJobs = (jobs || []).filter((j) => j.status === 'applied')

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">面试准备</h2>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">目标岗位</label>
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="">选择岗位...</option>
              {appliedJobs.map((j) => (
                <option key={j.id} value={j.id}>{j.title} @ {j.company}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">面试类型</label>
            <select
              value={interviewType}
              onChange={(e) => setInterviewType(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="full_loop">完整面试</option>
              <option value="phone_screen">电话初筛</option>
              <option value="technical">技术面</option>
              <option value="system_design">系统设计</option>
              <option value="behavioral">行为面</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => prepMutation.mutate()}
              disabled={!selectedJobId || prepMutation.isPending}
              className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
            >
              {prepMutation.isPending ? 'Gayle McDowell 为你准备中...' : '生成面试准备 (Opus)'}
            </button>
          </div>
        </div>
      </div>

      {prepData && prepData.prep_plan && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">
              {prepData.company} — {prepData.role}
            </h3>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{prepData.prep_plan.prep_summary}</p>
            {prepData.prep_plan.prep_timeline && (
              <div className="mt-3 p-3 bg-blue-50 rounded text-sm">
                <p className="font-medium text-blue-800 mb-1">准备时间线</p>
                <p className="text-blue-700 whitespace-pre-wrap">{prepData.prep_plan.prep_timeline}</p>
              </div>
            )}
          </div>

          {prepData.prep_plan.technical_topics && prepData.prep_plan.technical_topics.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">技术准备</h3>
              <div className="space-y-3">
                {prepData.prep_plan.technical_topics.map((t, i) => (
                  <div key={i} className="border rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium">{t.topic}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        t.importance === 'critical' ? 'bg-red-100 text-red-700' :
                        t.importance === 'important' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>{t.importance}</span>
                    </div>
                    {t.practice_problems.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-1">练习题:</p>
                        {t.practice_problems.map((p, j) => (
                          <p key={j} className="text-sm text-gray-700 ml-2">• {p}</p>
                        ))}
                      </div>
                    )}
                    {t.study_resources.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-500 mb-1">学习资源:</p>
                        {t.study_resources.map((r, j) => (
                          <p key={j} className="text-sm text-indigo-600 ml-2">• {r}</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {prepData.prep_plan.mock_interview_questions && prepData.prep_plan.mock_interview_questions.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">模拟面试题 ({prepData.prep_plan.mock_interview_questions.length})</h3>
              <div className="space-y-2">
                {prepData.prep_plan.mock_interview_questions.map((q, i) => (
                  <details key={i} className="border rounded-lg p-3">
                    <summary className="cursor-pointer text-sm font-medium">
                      [{q.category}] {q.question}
                      <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${
                        q.difficulty === 'hard' ? 'bg-red-100 text-red-600' :
                        q.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-green-100 text-green-600'
                      }`}>{q.difficulty}</span>
                    </summary>
                    {q.hints.length > 0 && (
                      <div className="mt-2 pl-4">
                        <p className="text-xs text-gray-500 mb-1">提示:</p>
                        {q.hints.map((h, j) => (
                          <p key={j} className="text-xs text-gray-600">• {h}</p>
                        ))}
                      </div>
                    )}
                  </details>
                ))}
              </div>
            </div>
          )}

          {prepData.prep_plan.behavioral_stories && prepData.prep_plan.behavioral_stories.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">行为面试 STAR 故事</h3>
              {prepData.prep_plan.behavioral_stories.map((s, i) => (
                <div key={i} className="border-l-2 border-indigo-300 pl-4 mb-4">
                  <h4 className="font-medium mb-2">{s.theme}</h4>
                  <div className="space-y-1 text-sm">
                    <p><span className="text-gray-500">Situation:</span> {s.star_framework.situation}</p>
                    <p><span className="text-gray-500">Task:</span> {s.star_framework.task}</p>
                    <p><span className="text-gray-500">Action:</span> {s.star_framework.action}</p>
                    <p><span className="text-gray-500">Result:</span> {s.star_framework.result}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {prepData.prep_plan.skill_gaps_identified && prepData.prep_plan.skill_gaps_identified.length > 0 && (
            <div className="bg-orange-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-orange-800 mb-2">面试前需提升的技能</h3>
              <div className="flex flex-wrap gap-1">
                {prepData.prep_plan.skill_gaps_identified.map((g, i) => (
                  <span key={i} className="text-xs bg-orange-200 text-orange-800 px-2 py-0.5 rounded">{g}</span>
                ))}
              </div>
            </div>
          )}

          {prepData.prep_plan.company_specific_tips && prepData.prep_plan.company_specific_tips.length > 0 && (
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-green-800 mb-2">针对性建议</h3>
              {prepData.prep_plan.company_specific_tips.map((tip, i) => (
                <p key={i} className="text-sm text-green-700">• {tip}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {!prepData && (
        <p className="text-center text-gray-400 py-12">
          选择一个已投递的岗位开始面试准备 — Gayle McDowell AI 会为你量身定制准备方案
        </p>
      )}
    </div>
  )
}
