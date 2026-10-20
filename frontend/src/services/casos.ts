import { apiClient } from './api'

export type Sexo = 'femenino' | 'masculino' | 'otro'

/** Lo que se carga al crear o editar un caso (nada que identifique a una persona). */
export interface DatosCaso {
  alias: string
  edad: number | null
  sexo: Sexo | null
  notas: string | null
}

export interface Caso extends DatosCaso {
  id: string
  creado_en: string
}

export interface PaginaDeCasos {
  casos: Caso[]
  /** Se pasa como `despuesDe` para pedir la página siguiente; null si no hay más. */
  siguiente: string | null
}

/** "25 años · femenino · 16/10/2026" (omite lo que no se cargó). */
export function resumenDelCaso(caso: Caso): string {
  return [
    caso.edad !== null ? `${caso.edad} años` : null,
    caso.sexo,
    new Date(caso.creado_en).toLocaleDateString('es-AR'),
  ].filter(Boolean).join(' · ')
}

export const casosApi = {
  listar: async (despuesDe?: string | null, limite = 20) =>
    (await apiClient.get<PaginaDeCasos>('/casos', { params: { limite, despues_de: despuesDe ?? undefined } })).data,
  ver: async (id: string) => (await apiClient.get<Caso>(`/casos/${id}`)).data,
  crear: async (datos: DatosCaso) => (await apiClient.post<Caso>('/casos', datos)).data,
  editar: async (id: string, datos: DatosCaso) => (await apiClient.put<Caso>(`/casos/${id}`, datos)).data,
  borrar: async (id: string) => {
    await apiClient.delete(`/casos/${id}`)
  },
}
