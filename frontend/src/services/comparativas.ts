import { apiClient } from './api'

// Reflejan ComparativaDatos, Comparativa y PaginaDeComparativas de backend/controller/modelos.py (decisión 025)
export interface DatosComparativa {
  titulo: string
  notas: string | null
  caso_id: string | null
}

export interface Comparativa extends DatosComparativa {
  id: string
  /** De 2 a 4, en el orden en que se muestran (S1, S2…) */
  simulacion_ids: string[]
  creado_en: string
}

export interface PaginaDeComparativas {
  comparativas: Comparativa[]
  siguiente: string | null
}

export const comparativasApi = {
  listar: async (despuesDe?: string | null, casoId?: string | null) =>
    (await apiClient.get<PaginaDeComparativas>('/comparativas',
      { params: { despues_de: despuesDe ?? undefined, caso_id: casoId ?? undefined } })).data,
  ver: async (id: string) => (await apiClient.get<Comparativa>(`/comparativas/${id}`)).data,
  crear: async (datos: DatosComparativa, simulacionIds: string[]) =>
    (await apiClient.post<Comparativa>('/comparativas', { ...datos, simulacion_ids: simulacionIds })).data,
  editar: async (id: string, datos: DatosComparativa) =>
    (await apiClient.put<Comparativa>(`/comparativas/${id}`, datos)).data,
  borrar: async (id: string) => {
    await apiClient.delete(`/comparativas/${id}`)
  },
}

/** Una guardada se abre en la misma pantalla de superposición. */
export const enlaceComparativa = (id: string) => `/superponer?comparativa=${id}`
