import axios from 'axios'
import type {
  EstadoServidor,
  ParametrosSimulacion,
  PuntoAudiograma,
  ResultadoAudiograma,
  ResultadoSimulacion,
} from './tiposSimulacion'

// Mismo origen que la página: en desarrollo Vite reenvía /api al backend (ver vite.config.js)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutos para simulaciones
})

export const api = {
  // Verificar estado del servidor y solver C
  async getHealth(): Promise<EstadoServidor> {
    const response = await apiClient.get<EstadoServidor>('/health')
    return response.data
  },

  // Obtener perfiles de audición disponibles
  async getProfiles(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/profiles')
    return response.data
  },

  // Ejecutar simulación
  async runSimulation(params: ParametrosSimulacion): Promise<ResultadoSimulacion> {
    const response = await apiClient.post<ResultadoSimulacion>('/simulate', params)
    return response.data
  },

  // Subir audiograma vía FilePond (multipart/form-data)
  async uploadAudiogram(file: File, patientName = 'Paciente'): Promise<ResultadoAudiograma> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('patient_name', patientName)

    const response = await apiClient.post<ResultadoAudiograma>('/audiogram/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Enviar audiograma ingresado manualmente
  async submitManualAudiogram(patientName: string, points: PuntoAudiograma[]): Promise<ResultadoAudiograma> {
    const response = await apiClient.post<ResultadoAudiograma>('/audiogram/manual', {
      patient_name: patientName,
      points,
    })
    return response.data
  },
}
