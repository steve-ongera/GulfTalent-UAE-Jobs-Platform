import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gt_access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('gt_refresh')
        const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh })
        localStorage.setItem('gt_access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.removeItem('gt_access')
        localStorage.removeItem('gt_refresh')
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(err)
  }
)

// ─── Auth ──────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
}

// ─── Categories (Public) ───────────────────────────────────────────────────
export const categoriesAPI = {
  list: () => api.get('/categories/'),
  detail: (slug) => api.get(`/categories/${slug}/`),
  documents: (slug) => api.get(`/categories/${slug}/documents/`),
}

// ─── Jobs (Public) ─────────────────────────────────────────────────────────
export const jobsAPI = {
  list: (params) => api.get('/jobs/', { params }),
  featured: () => api.get('/jobs/featured/'),
  detail: (slug) => api.get(`/jobs/${slug}/`),
}

// ─── Applications (Public) ─────────────────────────────────────────────────
export const applicationsAPI = {
  submit: (formData) => api.post('/applications/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

// ─── Admin — Categories ────────────────────────────────────────────────────
export const adminCategoriesAPI = {
  list: () => api.get('/admin/categories/'),
  create: (data) => api.post('/admin/categories/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  update: (id, data) => api.put(`/admin/categories/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  delete: (id) => api.delete(`/admin/categories/${id}/`),
}

// ─── Admin — Required Documents ───────────────────────────────────────────
export const adminDocumentsAPI = {
  list: (categoryId) => api.get('/admin/documents/', { params: categoryId ? { category: categoryId } : {} }),
  create: (data) => api.post('/admin/documents/', data),
  update: (id, data) => api.put(`/admin/documents/${id}/`, data),
  delete: (id) => api.delete(`/admin/documents/${id}/`),
}

// ─── Admin — Jobs ──────────────────────────────────────────────────────────
export const adminJobsAPI = {
  list: (params) => api.get('/admin/jobs/', { params }),
  create: (data) => api.post('/admin/jobs/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  update: (id, data) => api.put(`/admin/jobs/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  delete: (id) => api.delete(`/admin/jobs/${id}/`),
  toggleFeatured: (id) => api.post(`/admin/jobs/${id}/toggle-featured/`),
  toggleActive: (id) => api.post(`/admin/jobs/${id}/toggle-active/`),
}

// ─── Admin — Applications ──────────────────────────────────────────────────
export const adminApplicationsAPI = {
  list: (params) => api.get('/admin/applications/', { params }),
  detail: (id) => api.get(`/admin/applications/${id}/`),
  updateStatus: (id, data) => api.put(`/admin/applications/${id}/status/`, data),
  export: (params) => api.get('/admin/applications/export/', { params, responseType: 'blob' }),
}

// ─── Admin — Dashboard ─────────────────────────────────────────────────────
export const adminDashboardAPI = {
  stats: () => api.get('/admin/dashboard/stats/'),
}