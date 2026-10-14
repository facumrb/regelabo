import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutos para simulaciones
})

export const api = {
  // Verificar estado del servidor y solver C
  async getHealth() {
    const response = await apiClient.get('/health')
    return response.data
  },

  // Obtener perfiles de audición disponibles
  async getProfiles() {
    const response = await apiClient.get('/profiles')
    return response.data
  },

  // Ejecutar simulación
  async runSimulation(params) {
    const response = await apiClient.post('/simulate', params)
    return response.data
  },

  // Subir audiograma vía FilePond (multipart/form-data)
  async uploadAudiogram(file, patientName = 'Paciente') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('patient_name', patientName)

    const response = await apiClient.post('/audiogram/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Enviar audiograma ingresado manualmente
  async submitManualAudiogram(patientName, points) {
    const response = await apiClient.post('/audiogram/manual', {
      patient_name: patientName,
      points,
    })
    return response.data
  },
}
