import { isAxiosError } from 'axios'
import { apiClient } from './api'

export type TipoPerfil = 'estudiante' | 'investigador' | 'fonoaudiologo'

export interface Usuario {
  id: string
  email: string
  nombre: string
  tipo_perfil: TipoPerfil
  es_admin: boolean
}

export interface DatosRegistro {
  email: string
  password: string
  nombre: string
  tipo_perfil: TipoPerfil
  acepta_aviso: boolean
}

export const authApi = {
  registro: async (datos: DatosRegistro) => (await apiClient.post<Usuario>('/auth/registro', datos)).data,
  login: async (email: string, password: string) =>
    (await apiClient.post<Usuario>('/auth/login', { email, password })).data,
  logout: async () => {
    await apiClient.post('/auth/logout')
  },
  cambiarContrasena: async (actual: string, nueva: string) => {
    await apiClient.post('/auth/contrasena', { actual, nueva })
  },
  yo: async () => (await apiClient.get<Usuario>('/auth/yo')).data,
}

/** El mensaje en español que manda el backend ({detail: {codigo, mensaje}}), o uno genérico. */
export function mensajeDeError(error: unknown): string {
  if (isAxiosError(error)) {
    if (!error.response) return 'No se pudo conectar con el servidor.'
    const detalle = error.response.data?.detail
    if (typeof detalle === 'string') return detalle // endpoints del prototipo: {detail: "texto"}
    if (typeof detalle?.mensaje === 'string') return detalle.mensaje
    // Errores de validación de FastAPI (422): una lista de {loc, msg}
    if (Array.isArray(detalle)) return `Datos inválidos: ${detalle.map((d) => d.msg).join('; ')}`
  }
  return 'Ocurrió un error inesperado.'
}
