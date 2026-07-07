import api from './api'

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  // Don't set Content-Type manually — axios detects FormData and sets the
  // correct multipart/form-data boundary header automatically.
  const res = await api.post('/resumes/upload', formData)
  return res.data
}

export async function listResumes() {
  const res = await api.get('/resumes')
  return res.data
}

export async function getResume(resumeId) {
  const res = await api.get(`/resumes/${resumeId}`)
  return res.data
}
