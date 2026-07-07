import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import DashboardHome from './pages/DashboardHome.jsx'
import UploadResume from './pages/UploadResume.jsx'
import JDMatch from './pages/JDMatch.jsx'
import AITools from './pages/AITools.jsx'
import History from './pages/History.jsx'
import Settings from './pages/Settings.jsx'

import DashboardLayout from './components/DashboardLayout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardHome />} />
          <Route path="upload" element={<UploadResume />} />
          <Route path="jd-match" element={<JDMatch />} />
          <Route path="ai-tools" element={<AITools />} />
          <Route path="history" element={<History />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </>
  )
}
