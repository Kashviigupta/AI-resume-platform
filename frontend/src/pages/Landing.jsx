import React from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'

export default function Landing() {
  return (
    <div className="min-h-screen">
      <Navbar />

      <section className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <p className="font-mono text-xs uppercase tracking-widest text-ink/50 dark:text-paper/50 mb-4">
          ATS score · JD match · AI rewrite
        </p>
        <h1 className="font-display font-700 text-4xl md:text-6xl leading-tight tracking-tight mb-6">
          Get your resume{' '}
          <span className="mark-highlight">past the bots</span> —
          <br className="hidden md:block" /> and past the recruiter, too.
        </h1>
        <p className="font-body text-lg text-ink/70 dark:text-paper/70 max-w-xl mx-auto mb-8">
          Upload your resume, paste a job description, and get a real ATS score,
          a match score, missing skills, and AI-rewritten bullet points — in seconds.
        </p>
        <Link
          to="/register"
          className="inline-block px-6 py-3 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink font-medium hover:opacity-90 transition"
        >
          Analyze my resume →
        </Link>
      </section>

      {/* Signature element: a mock "annotated resume" card, like a recruiter's markup pass */}
      <section className="max-w-3xl mx-auto px-6 pb-24">
        <div className="card p-6 md:p-8 relative overflow-hidden">
          <div className="flex items-center justify-between mb-6">
            <span className="font-mono text-xs text-ink/40 dark:text-paper/40">resume_v3.pdf</span>
            <span className="font-mono text-xs px-2 py-1 rounded bg-match/10 text-match font-semibold">
              ATS 82 / 100
            </span>
          </div>
          <div className="space-y-3 font-body text-sm text-ink/80 dark:text-paper/80">
            <p className="line-through decoration-flag/70 decoration-2">
              Responsible for managing a small team of interns.
            </p>
            <p>
              <span className="mark-highlight">Led a 4-person intern team</span>, cutting onboarding time by 30%.
            </p>
            <p className="text-ink/40 dark:text-paper/40 font-mono text-xs pt-2">
              + missing skill detected: <span className="text-flag font-semibold">Docker</span>
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
