import client from './client'

export const pdfApi = {
  upload(file) {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/pdf/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  imports(params) {
    return client.get('/pdf/imports', { params })
  },
  importDetail(id) {
    return client.get(`/pdf/imports/${id}`)
  },
  deleteImport(id) {
    return client.delete(`/pdf/imports/${id}`)
  }
}
