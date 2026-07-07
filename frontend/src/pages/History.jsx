import React, { useEffect, useMemo, useState } from 'react'
import { listAllAnalyses } from '../services/analysisService'

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'ats', label: 'ATS Analysis' },
  { key: 'jd_match', label: 'JD Match' },
]

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function ScoreCell({ value }) {
  if (value === null || value === undefined) {
    return <span className="text-ink/30 dark:text-paper/30">—</span>
  }
  return <span className="font-mono">{value}</span>
}

export default function History() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    listAllAnalyses()
      .then(setAnalyses)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    return analyses.filter((a) => {
      if (filter !== 'all' && a.analysis_type !== filter) return false
      if (search && !a.resume_filename.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [analyses, filter, search])

  if (loading) {
    return <div className="card p-6 text-sm text-ink/60 dark:text-paper/60">Loading history…</div>
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h1 className="font-display font-700 text-2xl">Analysis history</h1>
        <input
          type="text"
          placeholder="Filter by filename…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 rounded-card border border-slate-150 dark:border-inkline bg-white dark:bg-inkline text-sm w-56 focus:outline-none focus:ring-2 focus:ring-highlight/50"
        />
      </div>

      <div className="flex gap-2 mb-4">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-card text-sm font-medium transition-colors ${
              filter === f.key
                ? 'bg-ink text-paper dark:bg-highlight dark:text-ink'
                : 'bg-slate-150/50 dark:bg-inkline text-ink/60 dark:text-paper/60'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="card p-6 text-center text-sm text-ink/60 dark:text-paper/60">
          {analyses.length === 0
            ? 'No analyses yet — run an ATS analysis from Upload Resume, or a job match from Job Match.'
            : 'No analyses match this filter.'}
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-150 dark:border-inkline text-left text-xs uppercase tracking-wide text-ink/50 dark:text-paper/50">
                <th className="px-4 py-3">Resume</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">ATS</th>
                <th className="px-4 py-3">Quality</th>
                <th className="px-4 py-3">Match</th>
                <th className="px-4 py-3">Overall</th>
                <th className="px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr key={a.id} className="border-b border-slate-150 dark:border-inkline last:border-0">
                  <td className="px-4 py-3 max-w-[180px] truncate">{a.resume_filename}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${
                        a.analysis_type === 'jd_match'
                          ? 'bg-highlight/20 text-ink dark:text-paper'
                          : 'bg-match/20 text-match'
                      }`}
                    >
                      {a.analysis_type === 'jd_match' ? 'JD Match' : 'ATS Analysis'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <ScoreCell value={a.ats_score} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreCell value={a.quality_score} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreCell value={a.match_score} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreCell value={a.overall_score} />
                  </td>
                  <td className="px-4 py-3 text-ink/60 dark:text-paper/60 whitespace-nowrap">
                    {formatDateTime(a.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
