import React, { useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { uploadResume } from '../services/resumeService'
import { runAtsAnalysis } from '../services/analysisService'
import ScoreBar from '../components/ScoreBar.jsx'

const SECTION_LABELS = {
  education: 'Education',
  experience: 'Experience',
  projects: 'Projects',
  certifications: 'Certifications',
}

export default function UploadResume() {
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [resume, setResume] = useState(null) // ResumeDetail from backend
  const [analysis, setAnalysis] = useState(null) // AnalysisOut from backend

  async function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setResume(null)
    setAnalysis(null)
    try {
      const data = await uploadResume(file)
      setResume(data)
      toast.success('Resume uploaded and parsed!')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed.'
      toast.error(msg)
    } finally {
      setUploading(false)
      e.target.value = '' // lets the same file be re-selected later if needed
    }
  }

  async function handleAnalyze() {
    if (!resume) return
    setAnalyzing(true)
    try {
      const data = await runAtsAnalysis(resume.id)
      setAnalysis(data)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Analysis failed.'
      toast.error(msg)
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display font-700 text-2xl mb-1">Upload Resume</h1>
        <p className="text-sm text-ink/60 dark:text-paper/60">
          PDF or DOCX, up to 5MB. We'll extract your sections and score it instantly.
        </p>
      </div>

      <div className="card p-6">
        <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-150 dark:border-inkline rounded-card py-10 cursor-pointer hover:border-highlight transition-colors">
          <span className="font-medium mb-1">{uploading ? 'Uploading…' : 'Click to choose a file'}</span>
          <span className="text-xs text-ink/50 dark:text-paper/50">.pdf or .docx</span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </label>
      </div>

      {resume && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4 gap-3">
            <h2 className="font-display font-700 text-lg truncate">{resume.filename}</h2>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="shrink-0 px-4 py-2 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink text-sm font-medium disabled:opacity-50"
            >
              {analyzing ? 'Analyzing…' : 'Run ATS Analysis'}
            </button>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            {Object.entries(SECTION_LABELS).map(([key, label]) => (
              <div key={key}>
                <p className="font-medium mb-1">{label}</p>
                {resume[key] && resume[key].length > 0 ? (
                  <ul className="list-disc list-inside text-ink/70 dark:text-paper/70 space-y-0.5">
                    {resume[key].slice(0, 4).map((line, i) => (
                      <li key={i} className="truncate">
                        {line}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-ink/40 dark:text-paper/40 italic">Not detected</p>
                )}
              </div>
            ))}
          </div>

          <div className="mt-4">
            <p className="font-medium mb-1 text-sm">Skills detected ({resume.skills?.length || 0})</p>
            <div className="flex flex-wrap gap-2">
              {(resume.skills || []).slice(0, 20).map((skill, i) => (
                <span key={i} className="px-2 py-1 rounded-full bg-highlight/20 text-xs font-mono">
                  {skill}
                </span>
              ))}
              {(!resume.skills || resume.skills.length === 0) && (
                <span className="text-ink/40 dark:text-paper/40 italic text-sm">
                  No skills section detected
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {analysis && (
        <div className="card p-6">
          <h2 className="font-display font-700 text-lg mb-4">Analysis results</h2>
          <ScoreBar label="ATS Score" score={analysis.ats_score} />
          <ScoreBar label="Quality Score" score={analysis.quality_score} />
          <ScoreBar label="Overall Score" score={analysis.overall_score} />

          <div className="mt-4 space-y-4 text-sm">
            <div>
              <p className="font-medium mb-1">ATS notes</p>
              <ul className="list-disc list-inside text-ink/70 dark:text-paper/70 space-y-1">
                {analysis.ats_reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-medium mb-1">Writing quality suggestions</p>
              <ul className="list-disc list-inside text-ink/70 dark:text-paper/70 space-y-1">
                {analysis.quality_suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
