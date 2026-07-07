import axios from 'axios'

// All backend calls go through this single instance. Pages/components should
// never call axios directly — they should call functions exported from
// services/ so the network layer stays in one place.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Attach the JWT (if present) to every outgoing request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// If the backend ever responds 401 (expired/invalid token), log the user out
// client-side so the UI doesn't get stuck in a broken "logged in" state.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
