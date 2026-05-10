import { useEffect } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { setAccessToken, getAccessToken } from '../lib/api'

export default function Layout() {
  const navigate = useNavigate()
  const isLoggedIn = !!getAccessToken()

  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login')
    }
  }, [isLoggedIn, navigate])

  const handleLogout = () => {
    setAccessToken(null)
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
          <div className="flex items-center gap-5">
            <h1 className="text-lg font-bold text-indigo-600">AI Job Hunter</h1>
            <NavLink to="/" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              仪表盘
            </NavLink>
            <NavLink to="/profile" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              画像
            </NavLink>
            <NavLink to="/jobs" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              职位
            </NavLink>
            <NavLink to="/companies" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              公司
            </NavLink>
            <NavLink to="/market" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              市场
            </NavLink>
            <span className="text-gray-300">|</span>
            <NavLink to="/applications" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              投递
            </NavLink>
            <NavLink to="/interviews" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              面试
            </NavLink>
            <NavLink to="/skill-gaps" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              技能
            </NavLink>
            <NavLink to="/offers" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              Offer
            </NavLink>
            <NavLink to="/negotiation" className={({ isActive }) => `text-sm ${isActive ? 'text-indigo-600 font-medium' : 'text-gray-600'}`}>
              谈判
            </NavLink>
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
