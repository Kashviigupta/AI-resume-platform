import React from 'react'

function colorFor(score) {
  if (score >= 75) return 'bg-match'
  if (score >= 50) return 'bg-highlight'
  return 'bg-flag'
}

export default function ScoreBar({ label, score }) {
  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium">{label}</span>
        <span className="font-mono">{score}/100</span>
      </div>
      <div className="w-full h-2.5 rounded-full bg-slate-150 dark:bg-inkline overflow-hidden">
        <div
          className={`h-full ${colorFor(score)} transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  )
}
