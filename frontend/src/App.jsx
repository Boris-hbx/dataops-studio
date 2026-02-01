import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Pipelines from './pages/Pipelines'
import QualityRules from './pages/QualityRules'
import CostAnalysis from './pages/CostAnalysis'
import AnnotationTasks from './pages/AnnotationTasks'
import AnnotationWorkspace from './pages/AnnotationWorkspace'

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/pipelines" element={<Pipelines />} />
        <Route path="/quality" element={<QualityRules />} />
        <Route path="/cost" element={<CostAnalysis />} />
        <Route path="/annotation" element={<AnnotationTasks />} />
        <Route path="/annotation/workspace" element={<AnnotationWorkspace />} />
      </Routes>
    </AppLayout>
  )
}
