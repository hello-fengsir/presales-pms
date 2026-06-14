import axios from 'axios'
const api = axios.create({
  baseURL: '/api/v1/presales',
  timeout: 60000,
})
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)
// Auth
export const login = (username: string, password: string) =>
  axios.post('/api/v1/auth/login', { username, password })
// Dashboard
export const getDashboardStats = (params?: Record<string, string>) =>
  api.get('/dashboard/stats', { params })
// Projects
export const getProjects = (params?: Record<string, string>) =>
  api.get('/projects', { params })
export const getProject = (id: number) => api.get(`/projects/${id}`)
export const createProject = (data: any) => api.post('/projects', data)
export const parseNotes = (notes: string, signal?: AbortSignal) => api.post('/projects/parse-notes', { notes }, { signal })
export const updateProject = (id: number, data: any) => api.put(`/projects/${id}`, data)
export const deleteProject = (id: number) => api.delete(`/projects/${id}`)
export const uploadTopology = (id: number, file: File) => {
  const fd = new FormData(); fd.append('file', file)
  return api.post(`/projects/${id}/topology`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
// Follow-ups
export const getFollowUps = (projectId: number) => api.get(`/projects/${projectId}/follow-ups`)
export const createFollowUp = (projectId: number, data: any) => api.post(`/projects/${projectId}/follow-ups`, data)
export const updateFollowUp = (projectId: number, fuId: number, data: any) => api.put(`/projects/${projectId}/follow-ups/${fuId}`, data)
export const deleteFollowUp = (projectId: number, fuId: number) => api.delete(`/projects/${projectId}/follow-ups/${fuId}`)
export const getFollowUpAttachments = (projectId: number, fuId: number) => api.get(`/projects/${projectId}/follow-ups/${fuId}/attachments`)
// Attachments
export const getAttachments = (projectId: number, attachmentType?: string) =>
  api.get(`/projects/${projectId}/attachments`, { params: attachmentType ? { attachment_type: attachmentType } : {} })
export const uploadAttachment = (projectId: number, file: File, followUpId?: number) => {
  const fd = new FormData(); fd.append('file', file)
  if (followUpId) fd.append('follow_up_id', String(followUpId))
  return api.post(`/projects/${projectId}/attachments`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const deleteAttachment = (projectId: number, id: number) =>
  api.delete(`/projects/${projectId}/attachments/${id}`)
// Customers
export const getCustomers = (params?: Record<string, string>) =>
  api.get('/customers', { params })
export const getCustomer = (id: number) => api.get(`/customers/${id}`)
export const createCustomer = (data: any) => api.post('/customers', data)
export const updateCustomer = (id: number, data: any) => api.put(`/customers/${id}`, data)
export const deleteCustomer = (id: number) => api.delete(`/customers/${id}`)
export const enrichCustomers = (customerIds: number[], save: boolean = false) =>
  api.post('/customers/enrich', { customer_ids: customerIds, save })
export const enrichCustomersFromText = (customerIds: number[], text: string) =>
  api.post('/customers/enrich-text', { customer_ids: customerIds, text })
export const addContact = (cid: number, data: any) => api.post(`/customers/${cid}/contacts`, data)
export const deleteContact = (cid: number, ctid: number) => api.delete(`/customers/${cid}/contacts/${ctid}`)
// Channels
export const getChannels = (params?: Record<string, string>) =>
  api.get('/channels', { params })
export const createChannel = (data: any) => api.post('/channels', data)
export const updateChannel = (id: number, data: any) => api.put(`/channels/${id}`, data)
export const deleteChannel = (id: number) => api.delete(`/channels/${id}`)
// Products
export const getProducts = (params?: Record<string, string>) =>
  api.get('/products', { params })
export const getProductCategories = () => api.get('/products/categories')
export const createProduct = (data: any) => api.post('/products', data)
export const updateProduct = (id: number, data: any) => api.put(`/products/${id}`, data)
export const deleteProduct = (id: number) => api.delete(`/products/${id}`)
export const getProductModels = (productId: number) => api.get(`/products/${productId}/models`)
// Sales
export const getSales = (params?: Record<string, string>) =>
  api.get('/sales', { params })
export const createSales = (data: any) => api.post('/sales', data)
export const updateSales = (id: number, data: any) => api.put(`/sales/${id}`, data)
export const deleteSales = (id: number) => api.delete(`/sales/${id}`)
export const getMonthlyRevenue = () => api.get('/sales/monthly-revenue')
// Reports
export const getReports = (params?: Record<string, string>) =>
  api.get('/reports', { params })
export default api
