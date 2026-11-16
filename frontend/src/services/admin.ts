import { apiClient } from './api'
import type { TipoPerfil } from './auth'

// Reflejan UsuarioAdmin, PaginaDeUsuarios y ContrasenaTemporal de backend/controller/modelos.py (decisión 028)
export interface UsuarioAdmin {
  id: string
  email: string
  nombre: string
  tipo_perfil: TipoPerfil
  es_admin: boolean
  creado_en: string
  bloqueado_hasta: string | null
  email_verificado: boolean
  /** Cuándo pidió restablecer la contraseña en "olvidé mi contraseña"; null si no hay pedido */
  restablecimiento_pedido_en: string | null
  casos: number
  simulaciones: number
}

export interface PaginaDeUsuarios {
  usuarios: UsuarioAdmin[]
  siguiente: string | null
}

export const usuariosAdminApi = {
  listar: async (filtros: { busqueda?: string; tipo?: TipoPerfil; con_pedido?: boolean }, despuesDe?: string | null) =>
    (await apiClient.get<PaginaDeUsuarios>('/admin/usuarios',
      { params: { ...filtros, despues_de: despuesDe ?? undefined } })).data,
  desbloquear: async (id: string) =>
    (await apiClient.post<UsuarioAdmin>(`/admin/usuarios/${id}/desbloquear`)).data,
  verificarEmail: async (id: string) =>
    (await apiClient.post<UsuarioAdmin>(`/admin/usuarios/${id}/verificar-email`)).data,
  resetearContrasena: async (id: string) =>
    (await apiClient.post<{ contrasena_temporal: string }>(`/admin/usuarios/${id}/resetear-contrasena`)).data
      .contrasena_temporal,
}

// Reflejan EstadoCola y SimulacionEnCurso de backend/controller/modelos.py
export interface SimulacionEnCurso {
  id: string
  usuario_email: string
  estado: 'en_cola' | 'ejecutando'
  creado_en: string
  iniciada_en: string | null
}

export interface EstadoCola {
  en_cola: number
  ejecutando: number
  tope_cola: number
  completadas_24h: number
  desde_cache_24h: number
  errores_24h: number
  duracion_promedio_s: number | null
  /** Deducido: hay simulaciones esperando y ninguna ejecutándose. null si la cola está vacía. */
  worker_detenido: boolean | null
  en_curso: SimulacionEnCurso[]
}

export const colaApi = {
  estado: async () => (await apiClient.get<EstadoCola>('/admin/cola')).data,
}
