import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { listResumes } from '../services/resumeService'
import { listAllAnalyses } from '../services/analysisService'
import ScoreTrendChart from '../components/ScoreTrendChart.jsx'
import ResumeCard from '../components/ResumeCard.jsx'

const StatCard = ({ label, value, accent }) => (
  <div className="card p-5">
    <p className="text-xs font-mono uppercase tracking-wide text-ink/50 dark:text-paper/50 mb-2">
      {label}
    </p>
    <p className={`font-display font-700 text-3xl ${accent}`}>{value}</p>
  </div>
)

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export default function DashboardHome() {
  const { user } = useAuth()
  const [resumes, setResumes] = useState([])
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Both calls are independent, so run them together instead of one after
    // the other — the page loads roughly twice as fast this way.
    Promise.all([listResumes(), listAllAnalyses()])
      .then(([resumeData, analysisData]) => {
        setResumes(resumeData)
        setAnalyses(analysisData)
      })
      .catch(() => {
        // A failed dashboard fetch shouldn't crash the page — it just shows
        // empty states below, same as a brand-new account would.
      })
      .finally(() => setLoading(false))
  }, [])

  // GET /analysis returns most-recent-first (perfect for a "latest score"
  // lookup, and for the History table). A trend chart reads left-to-right as
  // old -> new though, so we build a reversed copy rather than mutate state.
  const chronological = [...analyses].reverse()
  const atsPoints = chronological.filter((a) => a.ats_score !== null && a.ats_score !== undefined)
  const matchPoints = chronological.filter((a) => a.match_score !== null && a.match_score !== undefined)

  const latestAts = analyses.find((a) => a.ats_score !== null && a.ats_score !== undefined)
  const latestMatch = analyses.find((a) => a.match_score !== null && a.match_score !== undefined)

  return (
    <div>
      <h1 className="font-display font-700 text-2xl mb-1">
        Welcome back{user ? `, ${user.full_name}` : ''}
      </h1>
      <p className="text-sm text-ink/60 dark:text-paper/60 mb-6">
        Here's a snapshot of your latest resume performance.
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Latest ATS score"
          value={latestAts ? `${latestAts.ats_score}` : '—'}
          accent="text-match"
        />
        <StatCard
          label="Latest quality score"
          value={latestAts ? `${latestAts.quality_score}` : '—'}
          accent=""
        />
        <StatCard
          label="Latest match score"
          value={latestMatch ? `${latestMatch.match_score}` : '—'}
          accent="text-highlight"
        />
        <StatCard label="Resumes uploaded" value={resumes.length} accent="" />
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <ScoreTrendChart
          title="ATS & quality score history"
          labels={atsPoints.map((a) => formatDate(a.created_at))}
          datasets={[
            { label: 'ATS score', data: atsPoints.map((a) => a.ats_score), color: '#1F8A70' },
            { label: 'Quality score', data: atsPoints.map((a) => a.quality_score), color: '#F5C518' },
          ]}
          emptyMessage="Run an ATS analysis from the Upload Resume page to see this chart fill in."
        />
        <ScoreTrendChart
          title="Job match score history"
          labels={matchPoints.map((a) => formatDate(a.created_at))}
          datasets={[{ label: 'Match score', data: matchPoints.map((a) => a.match_score), color: '#F5C518' }]}
          emptyMessage="Compare a resume against a job description on the Job Match page to see this chart fill in."
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-display font-700 text-lg">Recent resumes</h2>
          <Link to="/dashboard/upload" className="text-sm font-medium underline">
            Upload another
          </Link>
        </div>

        {loading ? (
          <p className="text-sm text-ink/50 dark:text-paper/50">Loading…</p>
        ) : resumes.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {resumes.slice(0, 6).map((r) => (
              <ResumeCard key={r.id} filename={r.filename} uploadedAt={r.uploaded_at} />
            ))}
          </div>
        ) : (
          <div className="card p-6 text-center text-sm text-ink/60 dark:text-paper/60">
            No resumes yet. Head to{' '}
            <Link to="/dashboard/upload" className="font-medium text-ink dark:text-paper underline">
              Upload Resume
            </Link>{' '}
            to run your first analysis.
          </div>
        )}
      </div>
    </div>
  )
}
