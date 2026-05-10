import { useQuery } from '@tanstack/react-query'
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
}

export default function ProfilePage() {
  const { data, isLoading } = useQuery<Profile>({
    queryKey: ['profile'],
    queryFn: () => api.get('/profile'),
  })

  if (isLoading) return <p className="text-gray-500">加载中...</p>
  if (!data) return <p className="text-gray-500">暂无画像数据，请先完善个人资料</p>

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">个人画像</h2>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold mb-2">{data.name}</h3>
        <p className="text-gray-600 text-sm mb-1">
          {data.current_role} @ {data.current_company} · {data.years_of_experience}年经验 · {data.location}
        </p>
        <p className="text-gray-700 mt-3">{data.summary}</p>
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
    </div>
  )
}
