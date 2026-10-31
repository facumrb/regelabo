import type { PerfilAuditivo } from '../services/tiposSimulacion'

// Primero el tipo de caso y después el perfil dentro de él (decisión 026)
export type Tipo = 'personalizada' | 'normal' | 'plana' | 'descendente' | 'combinada'
export const TIPOS: { tipo: Tipo; titulo: string }[] = [
  { tipo: 'personalizada', titulo: 'Desde tu audiograma' },
  { tipo: 'normal', titulo: 'Audición normal' },
  { tipo: 'plana', titulo: 'Hipoacusia plana' },
  { tipo: 'descendente', titulo: 'Caída en agudos' },
  { tipo: 'combinada', titulo: 'Plana + caída en agudos' },
]
// "Audición normal" es la plana con grado normal según RN2 (PTA ≤ 20 dB HL)
export const tipoDe = (p: PerfilAuditivo): Tipo => (p.forma === 'plana' && p.grado === 'normal' ? 'normal' : p.forma)
const titulo = (tipo: Tipo) => TIPOS.find((t) => t.tipo === tipo)!.titulo

/** Para el historial y el detalle: un personalizado se clasifica como los precargados (RN2) y se marca su origen. */
export function tituloDelTipo(p: PerfilAuditivo) {
  if (p.forma !== 'personalizada') return titulo(tipoDe(p))
  const tipo: Tipo = p.patron === 'caida_en_agudos' ? 'descendente' : p.grado === 'normal' ? 'normal' : 'plana'
  return `${titulo(tipo)} (tu audiograma)`
}

/** Lo que cambia dentro del tipo: lo que sigue al " · " de la etiqueta ("Hasta 25 dB HL en 8 kHz"). */
export function detalle(p: PerfilAuditivo) {
  // Los personalizados: el nombre que les puso el usuario y su PTA
  if (p.forma === 'personalizada') return `${p.etiqueta.replace(/ \(personalizado\)$/, '')} · PTA ${p.pta} dB HL`
  const corte = p.etiqueta.indexOf(' · ')
  if (corte < 0) return p.etiqueta
  const resto = p.etiqueta.slice(corte + 3)
  return resto.charAt(0).toUpperCase() + resto.slice(1)
}
