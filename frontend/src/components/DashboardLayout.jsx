import React from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Sidebar from './Sidebar.jsx'

export default function DashboardLayout() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="max-w-6xl mx-auto flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
