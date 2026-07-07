import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

// Chart.js requires every element/plugin it uses to be registered once,
// globally, before any <Line> renders. Doing it here (module scope) means it
// runs exactly once no matter how many times this component mounts.
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

/**
 * A small wrapper around react-chartjs-2's <Line> chart, styled to match the
 * app's "editorial markup" theme and pre-configured for 0-100 score data.
 *
 * @param {string} title - Card heading shown above the chart.
 * @param {string[]} labels - X-axis labels (e.g. formatted dates), one per data point.
 * @param {{label: string, data: number[], color: string}[]} datasets - One or more score lines.
 * @param {string} [emptyMessage] - Shown instead of the chart when there are no data points yet.
 */
export default function ScoreTrendChart({ title, labels, datasets, emptyMessage }) {
  const hasData = labels.length > 0

  const data = {
    labels,
    datasets: datasets.map((ds) => ({
      label: ds.label,
      data: ds.data,
      borderColor: ds.color,
      backgroundColor: `${ds.color}33`, // ~20% opacity fill under the line
      tension: 0.35,
      fill: true,
      pointRadius: 3,
      pointBackgroundColor: ds.color,
    })),
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: datasets.length > 1,
        labels: { font: { family: 'Inter', size: 12 }, boxWidth: 10 },
      },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      y: { min: 0, max: 100, ticks: { stepSize: 25 } },
      x: { grid: { display: false } },
    },
  }

  return (
    <div className="card p-5">
      <p className="font-display font-700 text-sm mb-4">{title}</p>
      {hasData ? (
        <div style={{ height: 220 }}>
          <Line data={data} options={options} />
        </div>
      ) : (
        <div className="h-[220px] flex items-center justify-center text-center px-4 text-sm text-ink/40 dark:text-paper/40 italic">
          {emptyMessage || 'Not enough data yet.'}
        </div>
      )}
    </div>
  )
}
