import React from 'react'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/** One resume's summary card, used in the Dashboard's "Recent resumes" grid. */
export default function ResumeCard({ filename, uploadedAt }) {
  return (
    <div className="card p-4">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 shrink-0 rounded-card bg-highlight/20 flex items-center justify-center font-display font-700 text-sm">
          {filename.split('.').pop()?.slice(0, 3).toUpperCase() || 'DOC'}
        </div>
        <div className="min-w-0">
          <p className="font-medium text-sm truncate">{filename}</p>
          <p className="text-xs font-mono text-ink/50 dark:text-paper/50">
            Uploaded {formatDate(uploadedAt)}
          </p>
        </div>
      </div>
    </div>
  )
}
