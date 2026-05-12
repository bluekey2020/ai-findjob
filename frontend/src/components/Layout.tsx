import { useEffect, useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { setAccessToken, getAccessToken } from '../lib/api'

export default function Layout() {
  const navigate = useNavigate()
  const isLoggedIn = !!getAccessToken()
  const [showMore, setShowMore] = useState(false)

  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login')
    }
  }, [isLoggedIn, navigate])

  const handleLogout = () => {
    setAccessToken(null)
    navigate('/login')
  }

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:text-gray-900'}`

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <div className="flex items-center gap-5">
            <h1 className="text-lg font-bold text-indigo-600">AI Job Hunter</h1>

            {/* Core 6-step flow */}
            <NavLink to="/" end className={linkClass}>仪表盘</NavLink>
            <NavLink to="/profile" className={linkClass}>画像</NavLink>
            <NavLink to="/jobs" className={linkClass}>职位</NavLink>
            <NavLink to="/applications" className={linkClass}>投递</NavLink>
            <NavLink to="/interviews" className={linkClass}>面试</NavLink>
            <NavLink to="/offers" className={linkClass}>Offer</NavLink>

            {/* More dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowMore(!showMore)}
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                更多 ▾
              </button>
              {showMore && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowMore(false)} />
                  <div className="absolute top-full mt-1 left-0 bg-white rounded-lg shadow-lg border z-20 py-1 min-w-32">
                    <NavLink to="/companies" className={({ isActive }) =>
                      `block px-4 py-1.5 text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                      onClick={() => setShowMore(false)}
                    >公司</NavLink>
                    <NavLink to="/market" className={({ isActive }) =>
                      `block px-4 py-1.5 text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                      onClick={() => setShowMore(false)}
                    >市场</NavLink>
                    <NavLink to="/skill-gaps" className={({ isActive }) =>
                      `block px-4 py-1.5 text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                      onClick={() => setShowMore(false)}
                    >技能</NavLink>
                    <NavLink to="/negotiation" className={({ isActive }) =>
                      `block px-4 py-1.5 text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}
                      onClick={() => setShowMore(false)}
                    >谈判</NavLink>
                  </div>
                </>
              )}
            </div>
          </div>
          <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-gray-700">
            退出
          </button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
