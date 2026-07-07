import api from './api'

export async function registerUser({ fullName, email, password }) {
  const res = await api.post('/auth/register', {
    full_name: fullName,
    email,
    password,
  })
  return res.data
}

export async function loginUser({ email, password }) {
  const res = await api.post('/auth/login', { email, password })
  return res.data // { access_token, token_type }
}

export async function fetchCurrentUser() {
  const res = await api.get('/auth/me')
  return res.data
}
