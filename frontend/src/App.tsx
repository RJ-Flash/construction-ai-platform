import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAtom } from 'jotai'
import { userAtom } from '@/store/auth'

// Layouts
import DashboardLayout from '@/components/layouts/DashboardLayout'
import AuthLayout from '@/components/layouts/AuthLayout'

// Pages
import Dashboard from '@/pages/Dashboard'
import Projects from '@/pages/Projects'
import ProjectDetails from '@/pages/ProjectDetails'
import Documents from '@/pages/Documents'
import DocumentViewer from '@/pages/DocumentViewer'
import Estimations from '@/pages/Estimations'
import EstimationDetails from '@/pages/EstimationDetails'
import Plugins from '@/pages/Plugins'
import Settings from '@/pages/Settings'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import NotFound from '@/pages/NotFound'

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [user] = useAtom(userAtom)
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// App component with routing
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>
        
        {/* Dashboard routes - protected */}
        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId" element={<ProjectDetails />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/:documentId" element={<DocumentViewer />} />
          <Route path="/estimations" element={<Estimations />} />
          <Route path="/estimations/:estimationId" element={<EstimationDetails />} />
          <Route path="/plugins" element={<Plugins />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        
        {/* 404 route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App
