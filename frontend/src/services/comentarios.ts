import { apiClient } from './api'
import type { TipoPerfil } from './auth'

// Reflejan backend/controller/modelos.py (RN13, decisión 028)
export type EstadoComentario = 'nuevo' | 'leido' | 'archivado'

export interface Comentario {
  id: string
  texto: string
  estado: EstadoComentario
  creado_en: string
  autor_nombre: string
  autor_email: string
  autor_tipo: TipoPerfil
}

export interface PaginaDeComentarios {
  comentarios: Comentario[]
  siguiente: string | null
}

export interface Pendientes {
  comentarios_nuevos: number
  /** Usuarios que pidieron restablecer la contraseña y todavía no se atendieron */
  restablecimientos: number
}

export const LARGO_MAXIMO = 2000

const PENDIENTES_CAMBIARON = 'regelabo:pendientes-cambiaron'

/** El panel avisa que cambió algo pendiente, para que el contador del menú se actualice sin esperar a navegar. */
export const avisarPendientes = () => window.dispatchEvent(new Event(PENDIENTES_CAMBIARON))

export const alCambiarPendientes = (accion: () => void) => {
  window.addEventListener(PENDIENTES_CAMBIARON, accion)
  return () => window.removeEventListener(PENDIENTES_CAMBIARON, accion)
}

export const comentariosApi = {
  enviar: async (texto: string) => {
    await apiClient.post('/comentarios', { texto })
  },
  /** Sin `estado` trae los no archivados; sin `tipo`, de todos los tipos de usuario. */
  listar: async (filtros: { estado?: EstadoComentario; tipo?: TipoPerfil }, despuesDe?: string | null) =>
    (await apiClient.get<PaginaDeComentarios>('/admin/comentarios',
      { params: { ...filtros, despues_de: despuesDe ?? undefined } })).data,
  cambiarEstado: async (id: string, estado: EstadoComentario) =>
    (await apiClient.patch<Comentario>(`/admin/comentarios/${id}`, { estado })).data,
  pendientes: async () => (await apiClient.get<Pendientes>('/admin/pendientes')).data,
}
