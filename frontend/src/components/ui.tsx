import type { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Icono from './Icono'
import { avisoError, avisoOk, entrada, panel } from './estilos'
import { ETIQUETA_ESTADO, PUNTO_ESTADO } from '../services/simulaciones'
import type { EstadoSimulacion } from '../services/tiposSimulacion'

const claseVolver = 'inline-flex items-center gap-2 min-h-[44px] pl-2.5 pr-3.5 -ml-1 rounded-lg border border-linea ' +
  'bg-panel text-sm font-medium text-tinta hover:border-tenue transition'

/**
 * Botón de volver: vuelve a la pantalla anterior si se llegó navegando dentro de la app;
 * si se entró directo por la dirección, va a `a` (la pantalla de arriba).
 */
export function Volver({ a, texto, alHacerClic }: { a?: string; texto: string; alHacerClic?: () => void }) {
  const navigate = useNavigate()
  const { key } = useLocation()
  const contenido = <><Icono nombre="atras" tamano={18} />{texto}</>
  if (alHacerClic) return <button type="button" onClick={alHacerClic} className={claseVolver}>{contenido}</button>
  // 'default' = primera pantalla de la pestaña: no hay a dónde volver en el historial
  if (key === 'default' || !a) return <Link to={a ?? '/'} className={claseVolver}>{contenido}</Link>
  return <button type="button" onClick={() => navigate(-1)} className={claseVolver}>{contenido}</button>
}

export interface Columna<T> {
  titulo: string
  celda: (fila: T) => ReactNode
  /** Valores numéricos o parámetros: en monoespaciada */
  mono?: boolean
}

/**
 * Tabla del prototipo: columnas en PC y una tarjeta por fila en el celular (cada dato con su rótulo).
 * Toda la fila lleva a `enlace`; la primera celda es además un link, para el teclado y los lectores de pantalla.
 */
export function Tabla<T>({ filas, columnas, clave, enlace, nombre }: {
  filas: T[]; columnas: Columna<T>[]; clave: (fila: T) => string; enlace: (fila: T) => string; nombre: string
}) {
  const navigate = useNavigate()
  const [primera, ...resto] = columnas
  return (
    <table className="w-full border-collapse" aria-label={nombre}>
      <thead className="hidden sm:table-header-group">
        <tr>
          {columnas.map((c) => (
            <th key={c.titulo} scope="col" className="text-left text-xs font-medium uppercase tracking-wider text-tenue px-3 pb-3">
              {c.titulo}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="block sm:table-row-group">
        {filas.map((fila) => (
          <tr key={clave(fila)} onClick={() => navigate(enlace(fila))}
            className="grid grid-cols-2 gap-x-4 gap-y-1.5 py-4 sm:py-0 border-t border-linea sm:table-row cursor-pointer hover:bg-acento-suave transition">
            <td className="col-span-2 sm:table-cell sm:px-3 sm:py-4 sm:border-t sm:border-linea">
              <Link to={enlace(fila)} onClick={(e) => e.stopPropagation()} className="font-medium text-tinta hover:underline">
                {primera.celda(fila)}
              </Link>
            </td>
            {resto.map((c) => (
              <td key={c.titulo} className={`sm:table-cell sm:px-3 sm:py-4 sm:border-t sm:border-linea text-sm ${c.mono ? 'font-mono' : ''} text-tinta`}>
                <span className="block sm:hidden text-xs text-tenue font-sans">{c.titulo}</span>
                {c.celda(fila)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

/** Título de página con su bajada y, opcional, la acción principal a la derecha (abajo en el celular). */
export function Encabezado({ titulo, bajada, children }: { titulo: string; bajada?: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-tinta break-words">{titulo}</h1>
        {bajada && <p className="mt-1.5 text-tenue">{bajada}</p>}
      </div>
      {children && <div className="flex flex-wrap gap-2 [&>*]:flex-1 sm:[&>*]:flex-none">{children}</div>}
    </div>
  )
}

/** Estado de una simulación: punto de color más la etiqueta (el color nunca va solo). */
export function EstadoChip({ estado, extra }: { estado: EstadoSimulacion; extra?: string }) {
  return (
    <span className="inline-flex items-center gap-2 text-sm text-tinta whitespace-nowrap">
      <span className={`w-2 h-2 rounded-full ${PUNTO_ESTADO[estado]}`} aria-hidden="true" />
      {ETIQUETA_ESTADO[estado]}{extra}
    </span>
  )
}

/** Pestañas subrayadas; `opciones` es [valor, texto]. */
export function Pestanas<T extends string>({ opciones, valor, onCambio, nombre }: {
  opciones: [T, string][]; valor: T; onCambio: (v: T) => void; nombre: string
}) {
  return (
    <div role="tablist" aria-label={nombre} className="flex gap-6 border-b border-linea">
      {opciones.map(([v, texto]) => (
        <button key={v} type="button" role="tab" aria-selected={valor === v} onClick={() => onCambio(v)}
          className={`min-h-[44px] -mb-px border-b-2 text-sm font-medium transition ${
            valor === v ? 'border-acento text-tinta' : 'border-transparent text-tenue hover:text-tinta'
          }`}>
          {texto}
        </button>
      ))}
    </div>
  )
}

/** Pantalla angosta y centrada (login, registro): título afuera, el formulario en un panel y un pie opcional. */
export function Centrada({ titulo, bajada, pie, children }: { titulo: string; bajada?: string; pie?: ReactNode; children: ReactNode }) {
  return (
    <div className="max-w-md mx-auto md:mt-6 space-y-6">
      <Encabezado titulo={titulo} bajada={bajada} />
      <div className={`${panel} p-5 md:p-7 space-y-5`}>{children}</div>
      {pie && <p className="text-sm text-tenue text-center">{pie}</p>}
    </div>
  )
}

export function Tarjeta({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <div className={`max-w-md mx-auto ${panel} p-6 space-y-5`}>
      <h2 className="text-xl font-semibold text-tinta">{titulo}</h2>
      {children}
    </div>
  )
}

export function Campo({ etiqueta, children }: { etiqueta: string; children: ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm text-tenue">{etiqueta}</span>
      {children}
    </label>
  )
}

export function Aviso({ tipo, children }: { tipo: 'error' | 'ok'; children: ReactNode }) {
  return (
    <div role={tipo === 'error' ? 'alert' : 'status'}
      className={`px-3 py-2 rounded-lg border text-sm ${tipo === 'error' ? avisoError : avisoOk}`}>
      {children}
    </div>
  )
}

interface PropsDeslizador {
  id: string
  etiqueta: string
  unidad: string
  valor: number
  min: number
  max: number
  paso?: number
  deshabilitado?: boolean
  /** Nombre técnico del parámetro (ej. "f_mod"), visible al pasar el mouse por la etiqueta */
  sigla?: string
  /** Referencias de la escala debajo del slider (ej. "20 · muy bajo") */
  marcas?: string[]
  onCambio: (valor: number) => void
}

/** Slider con el número editable al lado: el slider para explorar, el número para un valor exacto. */
export function Deslizador({ id, etiqueta, unidad, valor, min, max, paso = 1, deshabilitado, sigla, marcas, onCambio }: PropsDeslizador) {
  return (
    <div>
      <label htmlFor={id} title={sigla} className="block text-sm text-tenue mb-1">{etiqueta}</label>
      <div className="grid grid-cols-[1fr_7.5rem] gap-3 items-center">
        <input type="range" min={min} max={max} step={paso} value={valor} disabled={deshabilitado}
          aria-label={`${etiqueta} (${unidad})`}
          onChange={(e) => onCambio(e.target.valueAsNumber)}
          className="w-full h-9 accent-acento cursor-pointer disabled:cursor-not-allowed" />
        <div className="relative">
          <input id={id} type="number" min={min} max={max} step={paso} value={valor} disabled={deshabilitado}
            // un campo vacío o a medio escribir no pisa el valor
            onChange={(e) => !Number.isNaN(e.target.valueAsNumber) && onCambio(e.target.valueAsNumber)}
            className={`${entrada} pr-14 text-right font-mono [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none`} />
          <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-tenue pointer-events-none">{unidad}</span>
        </div>
      </div>
      {marcas && (
        <div className="flex justify-between gap-2 mt-1 text-[11px] text-tenue">
          {marcas.map((m) => <span key={m}>{m}</span>)}
        </div>
      )}
    </div>
  )
}
