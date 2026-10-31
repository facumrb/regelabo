import { apiClient } from './api'
import type {
  EstadoSimulacion,
  EstadosInternos,
  PaginaDeSimulaciones,
  ParametrosSimulacion,
  Simulacion,
} from './tiposSimulacion'

export const simulacionesApi = {
  /** Deja la simulación en cola (o completada, si el resultado ya existía). No espera a que termine. */
  crear: async (parametros: ParametrosSimulacion, casoId: string | null) =>
    (await apiClient.post<Simulacion>('/simulaciones', { ...parametros, caso_id: casoId })).data,
  listar: async (despuesDe?: string | null, casoId?: string | null, limite = 20) =>
    (await apiClient.get<PaginaDeSimulaciones>('/simulaciones', {
      params: { limite, despues_de: despuesDe ?? undefined, caso_id: casoId ?? undefined },
    })).data,
  ver: async (id: string) => (await apiClient.get<Simulacion>(`/simulaciones/${id}`)).data,
  /** Pesan varios MB: pedirlos solo cuando se abre el panel. */
  estadosInternos: async (id: string) =>
    (await apiClient.get<EstadosInternos>(`/simulaciones/${id}/estados-internos`)).data,
}

/** Cada cuántos milisegundos se consulta el estado de una simulación pendiente. */
export const INTERVALO_CONSULTA_MS = 3000

export const enCurso = (estado: EstadoSimulacion) => estado === 'en_cola' || estado === 'ejecutando'

export const ETIQUETA_ESTADO: Record<EstadoSimulacion, string> = {
  en_cola: 'En cola',
  ejecutando: 'Ejecutando',
  completada: 'Completada',
  error: 'Error',
}

/** Punto de color que acompaña la etiqueta del estado (decisión 024). */
export const PUNTO_ESTADO: Record<EstadoSimulacion, string> = {
  en_cola: 'bg-tenue',
  ejecutando: 'bg-amber-500',
  completada: 'bg-acento',
  error: 'bg-rose-500',
}

/** "Flat00 · 4000 Hz @ 70 dB · fm 110 Hz · nH 13 / nM 3 / nL 3" */
export function resumenDeParametros(p: ParametrosSimulacion): string {
  return `${p.poles_profile} · ${p.carrier_freq} Hz @ ${p.spl_level} dB · fm ${p.f_mod} Hz · ` +
    `nH ${p.nH} / nM ${p.nM} / nL ${p.nL}`
}

export const formatearFecha = (iso: string) => new Date(iso).toLocaleString('es-AR')
