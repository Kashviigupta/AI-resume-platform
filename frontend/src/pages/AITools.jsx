import React, { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { listResumes } from '../services/resumeService'
import {
  rewriteBullet,
  generateSummary,
  generateCoverLetter,
  optimizeForATS,
  improveResume,
} from '../services/aiService'

function ErrMsg(err, fallback) {
  return err.response?.data?.detail || fallback
}

function Section({ title, description, children }) {
  return (
    <div className="card p-6 space-y-4">
      <div>
        <h2 className="font-display font-700 text-lg">{title}</h2>
        {description && (
          <p className="text-sm text-ink/60 dark:text-paper/60 mt-0.5">{description}</p>
        )}
      </div>
      {children}
    </div>
  )
}

function ChipList({ items, emptyLabel }) {
  if (!items || items.length === 0) {
    return <span className="text-ink/40 dark:text-paper/40 italic text-sm">{emptyLabel}</span>
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, i) => (
        <span key={i} className="px-2 py-1 rounded-full bg-highlight/20 text-xs font-mono">
          {item}
        </span>
      ))}
    </div>
  )
}

export default function AITools() {
  const [resumes, setResumes] = useState([])
  const [loadingResumes, setLoadingResumes] = useState(true)
  const [resumeId, setResumeId] = useState('')

  // Rewrite bullet (standalone, no resume needed)
  const [bulletInput, setBulletInput] = useState('')
  const [bulletResult, setBulletResult] = useState(null)
  const [bulletLoading, setBulletLoading] = useState(false)

  // Summary
  const [summary, setSummary] = useState(null)
  const [summaryLoading, setSummaryLoading] = useState(false)

  // Cover letter
  const [jdText, setJdText] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [coverLetter, setCoverLetter] = useState(null)
  const [coverLoading, setCoverLoading] = useState(false)

  // ATS optimization
  const [atsResult, setAtsResult] = useState(null)
  const [atsLoading, setAtsLoading] = useState(false)

  // Full improve
  const [improveJdText, setImproveJdText] = useState('')
  const [improveResult, setImproveResult] = useState(null)
  const [improveLoading, setImproveLoading] = useState(false)

  useEffect(() => {
    listResumes()
      .then((data) => {
        setResumes(data)
        if (data.length > 0) setResumeId(String(data[0].id))
      })
      .catch(() => toast.error('Could not load your resumes.'))
      .finally(() => setLoadingResumes(false))
  }, [])

  async function handleRewriteBullet(e) {
    e.preventDefault()
    setBulletLoading(true)
    setBulletResult(null)
    try {
      setBulletResult(await rewriteBullet(bulletInput))
    } catch (err) {
      toast.error(ErrMsg(err, 'Rewrite failed.'))
    } finally {
      setBulletLoading(false)
    }
  }

  async function handleSummary() {
    if (!resumeId) return
    setSummaryLoading(true)
    setSummary(null)
    try {
      setSummary(await generateSummary(Number(resumeId)))
    } catch (err) {
      toast.error(ErrMsg(err, 'Summary generation failed.'))
    } finally {
      setSummaryLoading(false)
    }
  }

  async function handleCoverLetter(e) {
    e.preventDefault()
    if (!resumeId) return
    setCoverLoading(true)
    setCoverLetter(null)
    try {
      setCoverLetter(await generateCoverLetter(Number(resumeId), jdText, companyName))
    } catch (err) {
      toast.error(ErrMsg(err, 'Cover letter generation failed.'))
    } finally {
      setCoverLoading(false)
    }
  }

  async function handleOptimizeATS() {
    if (!resumeId) return
    setAtsLoading(true)
    setAtsResult(null)
    try {
      setAtsResult(await optimizeForATS(Number(resumeId)))
    } catch (err) {
      toast.error(ErrMsg(err, 'ATS optimization failed.'))
    } finally {
      setAtsLoading(false)
    }
  }

  async function handleImproveResume(e) {
    e.preventDefault()
    if (!resumeId) return
    setImproveLoading(true)
    setImproveResult(null)
    try {
      setImproveResult(await improveResume(Number(resumeId), improveJdText))
    } catch (err) {
      toast.error(ErrMsg(err, 'Resume improvement failed.'))
    } finally {
      setImproveLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display font-700 text-2xl mb-1">AI Tools</h1>
        <p className="text-sm text-ink/60 dark:text-paper/60">
          Powered by Gemini. Each tool below returns fresh, structured output — nothing is
          fabricated beyond what's already in your resume.
        </p>
      </div>

      <div className="card p-6">
        <label className="block text-sm font-medium mb-1">Resume (used by every tool below except bullet rewrite)</label>
        {loadingResumes ? (
          <p className="text-sm text-ink/50 dark:text-paper/50">Loading your resumes…</p>
        ) : resumes.length === 0 ? (
          <p className="text-sm text-ink/50 dark:text-paper/50">
            You haven't uploaded a resume yet — upload one first.
          </p>
        ) : (
          <select
            value={resumeId}
            onChange={(e) => setResumeId(e.target.value)}
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

      {/* Rewrite a single bullet point */}
      <Section title="Rewrite a bullet point" description="Paste any one line — no resume needed.">
        <form onSubmit={handleRewriteBullet} className="space-y-3">
          <textarea
            required
            minLength={3}
            rows={2}
            value={bulletInput}
            onChange={(e) => setBulletInput(e.target.value)}
            placeholder="e.g. Responsible for managing a team of developers"
            className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight resize-y"
          />
          <button
            type="submit"
            disabled={bulletLoading}
            className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
          >
            {bulletLoading ? 'Rewriting…' : 'Rewrite'}
          </button>
        </form>
        {bulletResult && (
          <div className="text-sm space-y-1 pt-2 border-t border-slate-150 dark:border-inkline">
            <p><span className="font-medium">Improved:</span> {bulletResult.improved}</p>
            <p className="text-ink/60 dark:text-paper/60">{bulletResult.explanation}</p>
          </div>
        )}
      </Section>

      {/* Generate professional summary */}
      <Section title="Generate professional summary">
        <button
          onClick={handleSummary}
          disabled={summaryLoading || !resumeId}
          className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
        >
          {summaryLoading ? 'Generating…' : 'Generate summary'}
        </button>
        {summary && (
          <p className="text-sm pt-2 border-t border-slate-150 dark:border-inkline">
            {summary.summary}
          </p>
        )}
      </Section>

      {/* Cover letter */}
      <Section title="Generate cover letter">
        <form onSubmit={handleCoverLetter} className="space-y-3">
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Company name (optional)"
            className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight"
          />
          <textarea
            required
            minLength={20}
            rows={6}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the job description here…"
            className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight resize-y"
          />
          <button
            type="submit"
            disabled={coverLoading || !resumeId}
            className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
          >
            {coverLoading ? 'Writing…' : 'Generate cover letter'}
          </button>
        </form>
        {coverLetter && (
          <pre className="text-sm whitespace-pre-wrap font-sans pt-2 border-t border-slate-150 dark:border-inkline">
            {coverLetter.cover_letter}
          </pre>
        )}
      </Section>

      {/* ATS optimization */}
      <Section
        title="Optimize for ATS"
        description="Reuses the missing skills from your most recent Job Match check, if any."
      >
        <button
          onClick={handleOptimizeATS}
          disabled={atsLoading || !resumeId}
          className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
        >
          {atsLoading ? 'Optimizing…' : 'Optimize for ATS'}
        </button>
        {atsResult && (
          <div className="text-sm space-y-3 pt-2 border-t border-slate-150 dark:border-inkline">
            <p>{atsResult.optimized_summary}</p>
            <div>
              <p className="font-medium mb-1">Keywords to add</p>
              <ChipList items={atsResult.keyword_suggestions} emptyLabel="None suggested" />
            </div>
            <div>
              <p className="font-medium mb-1">Formatting suggestions</p>
              <ul className="list-disc list-inside text-ink/70 dark:text-paper/70 space-y-1">
                {atsResult.formatting_suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </Section>

      {/* Full resume improvement */}
      <Section
        title="Improve resume (full pass)"
        description="Rewrites your summary and every experience/project bullet. Optionally tailor toward a JD."
      >
        <form onSubmit={handleImproveResume} className="space-y-3">
          <textarea
            rows={4}
            value={improveJdText}
            onChange={(e) => setImproveJdText(e.target.value)}
            placeholder="Optional: paste a job description to tailor toward"
            className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight resize-y"
          />
          <button
            type="submit"
            disabled={improveLoading || !resumeId}
            className="px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
          >
            {improveLoading ? 'Improving…' : 'Improve resume'}
          </button>
        </form>
        {improveResult && (
          <div className="text-sm space-y-3 pt-2 border-t border-slate-150 dark:border-inkline">
            <p className="text-ink/70 dark:text-paper/70">{improveResult.overall_feedback}</p>
            <div>
              <p className="font-medium mb-1">Improved summary</p>
              <p>{improveResult.improved_summary}</p>
            </div>
            <div>
              <p className="font-medium mb-1">Experience bullets</p>
              <ul className="space-y-2">
                {improveResult.improved_experience_bullets.map((b, i) => (
                  <li key={i}>
                    <p><span className="font-medium">Improved:</span> {b.improved}</p>
                    <p className="text-ink/50 dark:text-paper/50 text-xs">{b.explanation}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-medium mb-1">Project bullets</p>
              <ul className="space-y-2">
                {improveResult.improved_project_bullets.map((b, i) => (
                  <li key={i}>
                    <p><span className="font-medium">Improved:</span> {b.improved}</p>
                    <p className="text-ink/50 dark:text-paper/50 text-xs">{b.explanation}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-medium mb-1">Skills worth adding</p>
              <ChipList items={improveResult.suggested_skills_to_add} emptyLabel="None suggested" />
            </div>
          </div>
        )}
      </Section>
    </div>
  )
}
