import api from './api'

export async function matchJobDescription(resumeId, jobDescriptionText) {
  const res = await api.post('/jd/match', {
    resume_id: resumeId,
    job_description_text: jobDescriptionText,
  })
  return res.data
}

export async function jdMatchHistory(resumeId) {
  const res = await api.get(`/jd/history/${resumeId}`)
  return res.data
}
