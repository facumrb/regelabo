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

export interface ResultadoAudiograma {
  status: string
  patient_name: string
  points: PuntoAudiograma[]
  matched_profile: string
  mean_hearing_loss: number
  clinical_classification: string
  notes: string
}

export interface EstadoServidor {
  status: 'online' | 'offline'
  service?: string
  c_solver_available: boolean
}
