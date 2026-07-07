import api from './api'

export async function rewriteBullet(bulletText) {
  const res = await api.post('/ai/rewrite-bullet', { bullet_text: bulletText })
  return res.data // { original, improved, explanation }
}

export async function generateSummary(resumeId) {
  const res = await api.post(`/ai/summary/${resumeId}`)
  return res.data // { summary }
}

export async function generateCoverLetter(resumeId, jobDescriptionText, companyName = '') {
  const res = await api.post(`/ai/cover-letter/${resumeId}`, {
    job_description_text: jobDescriptionText,
    company_name: companyName,
  })
  return res.data // { cover_letter }
}

export async function optimizeForATS(resumeId, missingSkills = null) {
  const res = await api.post(`/ai/optimize-ats/${resumeId}`, {
    missing_skills: missingSkills, // null => backend reuses the last JD match's missing skills
  })
  return res.data // { optimized_summary, keyword_suggestions, formatting_suggestions }
}

export async function improveResume(resumeId, jobDescriptionText = '') {
  const res = await api.post(`/ai/improve-resume/${resumeId}`, {
    job_description_text: jobDescriptionText,
  })
  return res.data // { overall_feedback, improved_summary, improved_experience_bullets, improved_project_bullets, suggested_skills_to_add }
}
