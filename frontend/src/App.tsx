import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import JobsPage from './pages/JobsPage'
import CompaniesPage from './pages/CompaniesPage'
import MarketPage from './pages/MarketPage'
import ApplicationsPage from './pages/ApplicationsPage'
import InterviewPage from './pages/InterviewPage'
import SkillGapPage from './pages/SkillGapPage'
import OffersPage from './pages/OffersPage'
import NegotiationPage from './pages/NegotiationPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/companies" element={<CompaniesPage />} />
            <Route path="/market" element={<MarketPage />} />
            <Route path="/applications" element={<ApplicationsPage />} />
            <Route path="/interviews" element={<InterviewPage />} />
            <Route path="/skill-gaps" element={<SkillGapPage />} />
            <Route path="/offers" element={<OffersPage />} />
            <Route path="/negotiation" element={<NegotiationPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
