/** Tipos de la simulación y los audiogramas: reflejan los modelos de backend/controller/modelos.py. */

export interface ParametrosSimulacion {
  carrier_freq: number
  poles_profile: string
  spl_level: number
  f_mod: number
  nH: number
  nM: number
  nL: number
}

export interface Armonico {
  harmonic_order: number
  frequency_hz: number
  amplitude_uv: number
}

export interface EspectroFFT {
  frequencies: number[]
  amplitudes: number[]
}

export interface OndasABR {
  time_ms: number[]
  w1: number[]
  w3: number[]
  w5: number[]
  efr_wave: number[]
}

export interface ResultadoSimulacion {
  status: string
  execution_time_seconds: number
  efr_value_uv: number
  harmonics: Armonico[]
  fft_spectrum: EspectroFFT
  abr_waves: OndasABR
  parameters_used: Partial<ParametrosSimulacion>
}

export interface PuntoAudiograma {
  frequency: number
  hearing_loss_db: number
}

/** Un perfil de polos descripto para el profesional, con la curva pedida y la que el modelo simula. */
export interface PerfilAuditivo {
  /** Identificador interno (carpeta): es el que va en `poles_profile` */
  nombre: string
  etiqueta: string
  forma: 'plana' | 'descendente' | 'combinada' | 'personalizada'
  grado: 'normal' | 'leve' | 'moderada' | 'severa'
  pta: number
  curva_pedida: PuntoAudiograma[]
  /** La pedida, recortada al techo del modelo */
  curva_simulada: PuntoAudiograma[]
  /** Frecuencias donde se simulan más de 5 dB menos de lo pedido */
  frecuencias_recortadas: number[]
}

export interface ResultadoAudiograma {
  status: string
  patient_name: string
  points: PuntoAudiograma[]
  matched_profile: string
  mean_hearing_loss: number
  clinical_classification: string
  notes: string
  perfil: PerfilAuditivo
}

export interface EstadoServidor {
  status: 'online' | 'offline'
  service?: string
  c_solver_available: boolean
}

export type EstadoSimulacion = 'en_cola' | 'ejecutando' | 'completada' | 'error'

/** Una simulación pedida: su estado y, si terminó, el resultado (solo en el detalle, no en el listado). */
export interface Simulacion {
  id: string
  estado: EstadoSimulacion
  caso_id: string | null
  parametros: ParametrosSimulacion
  creado_en: string
  iniciada_en: string | null
  finalizada_en: string | null
  mensaje_error: string | null
  /** El resultado ya existía (RN10): no pasó por la cola */
  reutilizada: boolean
  posicion: number | null
  resultado: ResultadoSimulacion | null
}

export interface PaginaDeSimulaciones {
  simulaciones: Simulacion[]
  /** Se pasa como `despuesDe` para pedir la página siguiente; null si no hay más. */
  siguiente: string | null
}

// ---- Estados internos (decisión 023), reflejan los modelos de backend/controller/modelos.py ----
// Las series son matrices [muestra][canal]; `canales` indica qué entradas de `EstadosInternos.canales` usa.
type Serie = number[][]

export interface CanalInterno {
  frecuencia_solicitada_hz: number
  /** Frecuencia característica del canal coclear más cercano: la que realmente se grafica */
  frecuencia_caracteristica_hz: number
}

export interface EstadosFibra {
  q: Serie
  w: Serie
  a: Serie
}

/** Datos de las siete figuras de estados internos de una simulación (se piden aparte del detalle). */
export interface EstadosInternos {
  canales: CanalInterno[]
  polo_shera: { fs_hz: number; frecuencia_caracteristica_hz: number[]; valores: Serie }
  ihc: {
    fs_hz: number; ventana_ms: number[]; canales: number[]
    imet_na: Serie; ikf_na: Serie; iks_na: Serie; vm_mv: Serie
  }
  vesiculas: { fs_hz: number; ventana_ms: number[]; hsr: EstadosFibra; msr: EstadosFibra; lsr: EstadosFibra }
  cn_ic: {
    fs_hz: number; ventana_ms: number[]; canales: number[]
    cn_exc: Serie; cn_inh: Serie; ic_exc: Serie; ic_inh: Serie
  }
}
