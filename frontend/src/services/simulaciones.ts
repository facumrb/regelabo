import { apiClient } from './api'
import type {
  EstadoSimulacion,
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

export const COLOR_ESTADO: Record<EstadoSimulacion, string> = {
  en_cola: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
  ejecutando: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  completada: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  error: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
}

/** "Flat00 · 4000 Hz @ 70 dB · fm 110 Hz · nH 13 / nM 3 / nL 3" */
export function resumenDeParametros(p: ParametrosSimulacion): string {
  return `${p.poles_profile} · ${p.carrier_freq} Hz @ ${p.spl_level} dB · fm ${p.f_mod} Hz · ` +
    `nH ${p.nH} / nM ${p.nM} / nL ${p.nL}`
}

export const formatearFecha = (iso: string) => new Date(iso).toLocaleString('es-AR')
