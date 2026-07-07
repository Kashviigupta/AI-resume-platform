import api from './api'

export async function runAtsAnalysis(resumeId) {
  const res = await api.post(`/analysis/${resumeId}/ats-score`)
  return res.data
}

export async function listAnalyses(resumeId) {
  const res = await api.get(`/analysis/${resumeId}`)
  return res.data
}

// Every analysis for the logged-in user, across every resume — most recent
// first. Powers the Dashboard charts and the History page (Milestone 11).
export async function listAllAnalyses() {
  const res = await api.get('/analysis')
  return res.data
}
