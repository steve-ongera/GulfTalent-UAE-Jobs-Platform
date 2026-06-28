import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AuthProvider } from './context/AuthContext'

// Public pages
import Home from './pages/Home'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Apply from './pages/Apply'
import ApplicationSuccess from './pages/ApplicationSuccess'
import Categories from './pages/Categories'
import CategoryJobs from './pages/CategoryJobs'
import About from './pages/About'
import Contact from './pages/Contact'
import NotFound from './pages/NotFound'

// Admin pages
import AdminLogin from './pages/admin/AdminLogin'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminJobs from './pages/admin/AdminJobs'
import AdminJobEdit from './pages/admin/AdminJobEdit'
import AdminCategories from './pages/admin/AdminCategories'
import AdminDocuments from './pages/admin/AdminDocuments'
import AdminApplications from './pages/admin/AdminApplications'
import AdminApplicationDetail from './pages/admin/AdminApplicationDetail'

function ProtectedRoute({ children }) {
  const { admin, loading } = useAuth()
  if (loading) return <div className="page-loading"><div className="spinner"></div></div>
  return admin ? children : <Navigate to="/admin/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* ── Public ── */}
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/:slug" element={<JobDetail />} />
        <Route path="/jobs/:slug/apply" element={<Apply />} />
        <Route path="/apply/success" element={<ApplicationSuccess />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/categories/:slug" element={<CategoryJobs />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        {/* ── Admin ── */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/jobs" element={<ProtectedRoute><AdminJobs /></ProtectedRoute>} />
        <Route path="/admin/jobs/new" element={<ProtectedRoute><AdminJobEdit /></ProtectedRoute>} />
        <Route path="/admin/jobs/:id/edit" element={<ProtectedRoute><AdminJobEdit /></ProtectedRoute>} />
        <Route path="/admin/categories" element={<ProtectedRoute><AdminCategories /></ProtectedRoute>} />
        <Route path="/admin/documents" element={<ProtectedRoute><AdminDocuments /></ProtectedRoute>} />
        <Route path="/admin/applications" element={<ProtectedRoute><AdminApplications /></ProtectedRoute>} />
        <Route path="/admin/applications/:id" element={<ProtectedRoute><AdminApplicationDetail /></ProtectedRoute>} />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  )
}