import React, { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { listResumes } from '../services/resumeService'
import { matchJobDescription } from '../services/jdService'
import ScoreBar from '../components/ScoreBar.jsx'

export default function JDMatch() {
  const [resumes, setResumes] = useState([])
  const [loadingResumes, setLoadingResumes] = useState(true)
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [jdText, setJdText] = useState('')
  const [matching, setMatching] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    listResumes()
      .then((data) => {
        setResumes(data)
        if (data.length > 0) setSelectedResumeId(String(data[0].id))
      })
      .catch(() => toast.error('Could not load your resumes.'))
      .finally(() => setLoadingResumes(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!selectedResumeId) {
      toast.error('Upload a resume first.')
      return
    }
    setMatching(true)
    setResult(null)
    try {
      const data = await matchJobDescription(Number(selectedResumeId), jdText)
      setResult(data)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Matching failed.'
      toast.error(msg)
    } finally {
      setMatching(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display font-700 text-2xl mb-1">Job Description Match</h1>
        <p className="text-sm text-ink/60 dark:text-paper/60">
          Paste a job description to see how well one of your resumes matches it, and which
          skills it's missing.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Resume</label>
          {loadingResumes ? (
            <p className="text-sm text-ink/50 dark:text-paper/50">Loading your resumes…</p>
          ) : resumes.length === 0 ? (
            <p className="text-sm text-ink/50 dark:text-paper/50">
              You haven't uploaded a resume yet — upload one first.
            </p>
          ) : (
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
              className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.filename}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Job description</label>
          <textarea
            required
            minLength={20}
            rows={8}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the full job description here…"
            className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight resize-y"
          />
        </div>

        <button
          type="submit"
          disabled={matching || resumes.length === 0}
          className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
        >
          {matching ? 'Matching…' : 'Check match'}
        </button>
      </form>

      {result && (
        <div className="card p-6 space-y-4">
          <h2 className="font-display font-700 text-lg">Match results</h2>
          <ScoreBar label="Match Score" score={result.match_score} />

          <div>
            <p className="font-medium mb-1 text-sm">Skills matched ({result.matched_skills.length})</p>
            <div className="flex flex-wrap gap-2">
              {result.matched_skills.length === 0 ? (
                <span className="text-ink/40 dark:text-paper/40 italic text-sm">None found</span>
              ) : (
                result.matched_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-1 rounded-full bg-match/20 text-xs font-mono">
                    {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          <div>
            <p className="font-medium mb-1 text-sm">
              Missing skills ({result.missing_skills.length})
            </p>
            <div className="flex flex-wrap gap-2">
              {result.missing_skills.length === 0 ? (
                <span className="text-ink/40 dark:text-paper/40 italic text-sm">
                  None — great coverage!
                </span>
              ) : (
                result.missing_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-1 rounded-full bg-flag/20 text-xs font-mono">
                    {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          <div>
            <p className="font-medium mb-1 text-sm">Top JD keywords</p>
            <div className="flex flex-wrap gap-2">
              {result.jd_keywords.map((kw, i) => (
                <span
                  key={i}
                  className="px-2 py-1 rounded-full bg-slate-150/60 dark:bg-inkline text-xs font-mono"
                >
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
