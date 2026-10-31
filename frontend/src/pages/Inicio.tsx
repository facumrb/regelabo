import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EtiquetaPerfil from '../components/EtiquetaPerfil'
import Icono, { type NombreIcono } from '../components/Icono'
import { botonSecundario, etiqueta, panel } from '../components/estilos'
import { EstadoChip, Encabezado } from '../components/ui'
import { useSesion } from '../context/SesionContext'
import { mensajeDeError } from '../services/auth'
import { enCurso, formatearFecha, simulacionesApi } from '../services/simulaciones'
import type { Simulacion } from '../services/tiposSimulacion'

const PASOS = [
  ['01', 'Cargá un audiograma', 'Ingresá los umbrales o subí un CSV y generá un perfil.', '/simular/audiograma'],
  ['02', 'Simulá', 'El modelo corre en segundo plano, unos 80 segundos.', '/simular'],
  ['03', 'Interpretá', 'EFR, ABR y espectro, más los estados internos.', '/simulaciones'],
]

interface Accion { a: string; icono: NombreIcono; titulo: string; texto: string }

function Item({ simulacion }: { simulacion: Simulacion }) {
  const p = simulacion.parametros
  return (
    <li className={`${panel} rounded-xl px-5 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3`}>
      <div>
        <b className="font-medium text-tinta"><EtiquetaPerfil nombre={p.poles_profile} /></b>
        <small className="block text-sm text-tenue">
          {p.carrier_freq} Hz · {p.spl_level} dB SPL · {formatearFecha(simulacion.creado_en)}
        </small>
      </div>
      <div className="flex items-center gap-5">
        <EstadoChip estado={simulacion.estado} />
        {!enCurso(simulacion.estado) && (
          <Link to={`/simulaciones/${simulacion.id}`} className={botonSecundario}>Ver resultado</Link>
        )}
      </div>
    </li>
  )
}

/** Pantalla principal con sesión (decisión 024): qué se hace acá, accesos directos y las últimas simulaciones. */
export default function Inicio() {
  const { usuario } = useSesion()
  const [simulaciones, setSimulaciones] = useState<Simulacion[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    simulacionesApi.listar(null, null, 5)
      .then((pagina) => setSimulaciones(pagina.simulaciones))
      .catch((err) => setError(mensajeDeError(err)))
  }, [])

  const acciones: Accion[] = [
    { a: '/simular', icono: 'simular', titulo: 'Nueva simulación', texto: 'Elegí un caso y un perfil y corré el modelo.' },
    { a: '/simular/audiograma', icono: 'subir', titulo: 'Cargar audiograma', texto: 'Subí un CSV o ingresá los umbrales.' },
    { a: '/casos', icono: 'casos', titulo: 'Mis casos', texto: 'Casos y audiogramas guardados.' },
    { a: '/simulaciones', icono: 'historial', titulo: 'Historial', texto: 'Todas tus simulaciones y sus resultados.' },
  ]
  // La última terminada va destacada; el resto de las 5 más nuevas (en cola incluidas) va en "recientes"
  const ultima = simulaciones?.find((s) => !enCurso(s.estado))
  const recientes = simulaciones?.filter((s) => s !== ultima) ?? []

  return (
    <div className="space-y-10">
      <Encabezado titulo={`Hola, ${usuario?.nombre ?? ''}`} bajada="Simulá cómo responde la cóclea a partir de un audiograma." />

      <ol className="grid md:grid-cols-3 gap-4 md:gap-8 py-5 border-y border-linea">
        {PASOS.map(([n, titulo, texto, a]) => (
          <li key={n}>
            <Link to={a} className="group grid grid-cols-[2rem_1fr] md:block">
              <span className="font-mono text-sm text-acento md:block">{n}</span>
              <div>
                <b className="block font-semibold text-tinta group-hover:text-acento group-hover:underline">{titulo}</b>
                <span className="text-sm text-tenue">{texto}</span>
              </div>
            </Link>
          </li>
        ))}
      </ol>

      <div className="grid sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1fr] gap-3 md:gap-4">
        {acciones.map(({ a, icono, titulo, texto }, i) => {
          const principal = i === 0
          const clases = `flex sm:flex-col items-center sm:items-start gap-4 sm:gap-3.5 p-5 rounded-2xl border text-left transition sm:min-h-[8rem] ${
            principal
              ? 'sm:col-span-2 lg:col-span-1 bg-acento border-acento text-acento-tinta hover:brightness-110'
              : 'bg-panel border-linea text-tinta hover:border-acento'
          }`
          const contenido = (
            <>
              <Icono nombre={icono} tamano={24} className={`shrink-0 ${principal ? '' : 'text-acento'}`} />
              <div>
                <b className="block font-semibold">{titulo}</b>
                <span className={`text-sm leading-snug ${principal ? 'opacity-85' : 'text-tenue'}`}>{texto}</span>
              </div>
            </>
          )
          return <Link key={titulo} to={a} className={clases}>{contenido}</Link>
        })}
      </div>

      {error && <p role="alert" className="text-sm text-tenue">No se pudieron cargar tus simulaciones: {error}</p>}
      {simulaciones && simulaciones.length === 0 && (
        <p className="text-tenue">Todavía no pediste ninguna simulación.</p>
      )}
      {ultima && (
        <section className="space-y-3">
          <h2 className={etiqueta}>Continuá donde dejaste</h2>
          <ul><Item simulacion={ultima} /></ul>
        </section>
      )}
      {recientes.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-baseline justify-between gap-4">
            <h2 className={etiqueta}>Simulaciones recientes</h2>
            <Link to="/simulaciones" className="text-sm text-acento hover:underline">Ver todas</Link>
          </div>
          <ul className="space-y-2">{recientes.map((s) => <Item key={s.id} simulacion={s} />)}</ul>
        </section>
      )}
    </div>
  )
}
