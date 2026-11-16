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
