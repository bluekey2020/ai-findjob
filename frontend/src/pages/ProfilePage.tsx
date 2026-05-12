import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

interface Skill {
  id: string
  name: string
  level: string
  years: number
  category: string
}

interface WorkExperience {
  id: string
  company: string
  title: string
  start_date: string
  end_date: string
  description: string
  highlights: string[]
  tech_stack: string[]
}

interface Profile {
  name: string
  email: string
  location: string
  current_role: string
  current_company: string
  years_of_experience: number
  summary: string
  skills: Skill[]
  work_experiences: WorkExperience[]
  highlights: string[]
  target_roles: string[]
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [rawText, setRawText] = useState('')
  const [fileName, setFileName] = useState('')

  const { data, isLoading } = useQuery<Profile>({
    queryKey: ['profile'],
    queryFn: () => api.get('/profile'),
    retry: false,
  })

  const analyzeMutation = useMutation({
    mutationFn: (body: FormData) => api.postFormData('/profile/analyze', body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['guide'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const handleFileUpload = () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setFileName(file.name)
    const formData = new FormData()
    formData.append('file', file)
    analyzeMutation.mutate(formData)
  }

  const handleTextSubmit = () => {
    if (!rawText.trim()) return
    const formData = new FormData()
    formData.append('raw_text', rawText)
    analyzeMutation.mutate(formData)
  }

  if (isLoading) return <p className="text-gray-500">加载中...</p>

  const hasProfile = !!data

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">个人画像</h2>

      {/* Step 2: Upload/paste resume — shown prominently when no profile exists */}
      {!hasProfile && (
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg shadow p-6 mb-6 border border-indigo-100">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-lg">📄</span>
            <h3 className="text-lg font-semibold text-indigo-900">Step 2: 提交你的简历</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            上传简历文件或粘贴简历文本，AI 会自动提取你的技能、工作经历和教育背景，生成结构化画像。
          </p>

          {/* File upload */}
          <div className="mb-4">
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleFileUpload}
              className="hidden"
            />
            <div className="flex gap-2">
              <button
                onClick={() => fileRef.current?.click()}
                className="px-4 py-2 text-sm border border-indigo-300 rounded-lg hover:bg-indigo-50 text-indigo-700"
                disabled={analyzeMutation.isPending}
              >
                上传文件 (PDF/DOCX/TXT)
              </button>
              {fileName && <span className="text-sm text-gray-500 self-center">{fileName}</span>}
            </div>
          </div>

          {/* Text paste */}
          <div className="mb-3">
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows={8}
              className="w-full border border-gray-300 rounded-lg p-3 text-sm font-mono"
              placeholder="或者直接粘贴简历文本...&#10;&#10;张三&#10;Python 工程师 | 5年经验&#10;……"
            />
          </div>

          <button
            onClick={handleTextSubmit}
            disabled={analyzeMutation.isPending || !rawText.trim()}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {analyzeMutation.isPending ? 'AI 分析中...' : '提交分析'}
          </button>

          {analyzeMutation.isPending && (
            <p className="text-sm text-indigo-600 mt-3 animate-pulse">
              AI 正在分析你的简历，提取结构化数据...
            </p>
          )}

          {analyzeMutation.isSuccess && (
            <div className="mt-4 p-3 bg-green-50 rounded-lg flex items-center justify-between">
              <span className="text-sm text-green-700">✓ 分析完成！AI 已生成结构化画像</span>
              <button
                onClick={() => navigate('/jobs')}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Step 4: 去搜索职位 →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Profile display */}
      {hasProfile && (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-2">{data.name}</h3>
            <p className="text-gray-600 text-sm mb-1">
              {data.current_role} @ {data.current_company} · {data.years_of_experience}年经验 · {data.location}
            </p>
            <p className="text-gray-700 mt-3">{data.summary}</p>
            {data.target_roles?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                <span className="text-xs text-gray-500">目标岗位：</span>
                {data.target_roles.map((r, i) => (
                  <span key={i} className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded">{r}</span>
                ))}
              </div>
            )}
          </div>

          {data.skills.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4">技能</h3>
              <div className="flex flex-wrap gap-2">
                {data.skills.map((skill) => (
                  <span
                    key={skill.id}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-indigo-50 text-indigo-700"
                  >
                    {skill.name}
                    <span className="text-indigo-400">·</span>
                    {skill.level}
                    <span className="text-indigo-400">·</span>
                    {skill.years}y
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.work_experiences.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">工作经历</h3>
              <div className="space-y-4">
                {data.work_experiences.map((exp) => (
                  <div key={exp.id} className="border-l-2 border-indigo-300 pl-4">
                    <p className="font-medium">{exp.title}</p>
                    <p className="text-sm text-gray-500">{exp.company} · {exp.start_date} - {exp.end_date}</p>
                    <p className="text-sm text-gray-700 mt-1">{exp.description}</p>
                    {exp.tech_stack.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {exp.tech_stack.map((tech) => (
                          <span key={tech} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{tech}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
