import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { EstadoNuevaSimulacion } from '../../App'
import PerfilSimulado from '../../components/PerfilSimulado'
import PanelEstadosInternos from '../../components/PanelEstadosInternos'
import PlotsPanel from '../../components/PlotsPanel'
import ResultsSummary from '../../components/ResultsSummary'
import { Aviso, Encabezado, EstadoChip, MasAcciones, Tarjeta, Volver } from '../../components/ui'
import { botonPrimario, botonSecundario, botonTexto, panel } from '../../components/estilos'
import { useSimulacionesEnCurso } from '../../context/SimulacionesEnCurso'
import { detalle, tituloDelTipo } from '../../components/perfiles'
import { api } from '../../services/api'
import { mensajeDeError } from '../../services/auth'
import {
  enCurso, formatearFecha, INTERVALO_CONSULTA_MS, simulacionesApi,
} from '../../services/simulaciones'
import type { PerfilAuditivo, Simulacion } from '../../services/tiposSimulacion'

/** Una simulación: sus parámetros, su estado y, si terminó, los mismos gráficos del simulador. */
export default function DetalleSimulacion() {
  const { id = '' } = useParams()
  const [simulacion, setSimulacion] = useState<Simulacion | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [perfil, setPerfil] = useState<PerfilAuditivo | null>(null)
  const [verParametros, setVerParametros] = useState(false) // en el celular los parámetros van plegados
  const nombrePerfil = simulacion?.parametros.poles_profile
  const { marcarVista } = useSimulacionesEnCurso()

  // Abrir el detalle de una terminada apaga su aviso en la barra
  useEffect(() => {
    if (simulacion && !enCurso(simulacion.estado)) marcarVista(simulacion.id)
  }, [simulacion?.id, simulacion?.estado])

  // Las curvas del perfil para el aviso final; los personalizados viejos no las guardaron (404) y no se muestran
  useEffect(() => {
    setPerfil(null)
    if (!nombrePerfil) return
    let activo = true
    api.getProfile(nombrePerfil).then((p) => { if (activo) setPerfil(p) }).catch(() => {})
    return () => { activo = false }
  }, [nombrePerfil])

  // Mientras está en cola o ejecutando, se vuelve a consultar cada pocos segundos
  useEffect(() => {
    let activo = true
    let temporizador: ReturnType<typeof setTimeout> | undefined
    setSimulacion(null)
    setError(null)

    const consultar = async () => {
      try {
        const actual = await simulacionesApi.ver(id)
        if (!activo) return
        setSimulacion(actual)
        if (enCurso(actual.estado)) temporizador = setTimeout(consultar, INTERVALO_CONSULTA_MS)
      } catch (e) {
        if (activo) setError(mensajeDeError(e))
      }
    }
    consultar()

    return () => {
      activo = false
      clearTimeout(temporizador)
    }
  }, [id])

  if (error && !simulacion) {
    return (
      <Tarjeta titulo="Simulación no encontrada">
        <Aviso tipo="error">{error}</Aviso>
        <Link to="/simulaciones" className={botonSecundario}>Volver al historial</Link>
      </Tarjeta>
    )
  }
  if (!simulacion) return null

  const conEstosParametros: EstadoNuevaSimulacion = {
    parametros: simulacion.parametros, casoId: simulacion.caso_id, perfil,
  }

  return (
    <div className="aparecer space-y-6">
      {/* Retrocede a donde se estaba (el historial con su filtro, Simular…); si se abrió directo, va al historial */}
      <Volver a="/simulaciones" texto="Volver" />
      <Encabezado titulo="Simulación" bajada={perfil?.etiqueta}>
        <EstadoChip estado={simulacion.estado}
          extra={simulacion.estado === 'en_cola' && simulacion.posicion ? ` (lugar ${simulacion.posicion})` : ''} />
      </Encabezado>

      {/* Todas a la vista en PC; en tablet y celular, las secundarias van en el menú ⋯ */}
      <nav aria-label="Qué hacer ahora" className="flex items-center gap-2 lg:flex-wrap">
        <Link to="/simular" state={conEstosParametros} className={`${botonPrimario} flex-1 sm:flex-none`}>
          <span className="sm:hidden">Simular de nuevo</span>
          <span className="hidden sm:inline">Simular nuevamente con estos parámetros</span>
        </Link>
        <Link to="/simular" state={{} satisfies EstadoNuevaSimulacion} className={`${botonSecundario} hidden lg:inline-flex`}>
          Nueva simulación
        </Link>
        {simulacion.estado === 'completada' && (
          <Link to={`/simulaciones?superponer=${simulacion.id}`} className={`${botonSecundario} hidden sm:inline-flex`}>
            Superponer con…
          </Link>
        )}
        <Link to="/simulaciones" className={`${botonTexto} hidden lg:inline-flex`}>Ver historial</Link>
        <Link to="/" className={`${botonTexto} hidden lg:inline-flex`}>Volver al inicio</Link>
        <MasAcciones className="lg:hidden" acciones={[
          { texto: 'Nueva simulación', a: '/simular', state: {} satisfies EstadoNuevaSimulacion },
          ...(simulacion.estado === 'completada'
            ? [{ texto: 'Superponer con…', a: `/simulaciones?superponer=${simulacion.id}`, soloCelular: true }]
            : []),
          { texto: 'Ver historial', a: '/simulaciones' },
          { texto: 'Volver al inicio', a: '/' },
        ]} />
      </nav>

      <button type="button" onClick={() => setVerParametros(!verParametros)} aria-expanded={verParametros}
        aria-controls="parametros-simulacion"
        className={`md:hidden ${panel} w-full min-h-[44px] px-4 py-2.5 flex items-center justify-between gap-3 text-sm`}>
        <b className="font-medium text-tinta">Parámetros</b>
        <span className="font-mono text-xs text-tenue truncate">
          {simulacion.parametros.carrier_freq} Hz · {simulacion.parametros.spl_level} dB · fm {simulacion.parametros.f_mod}
          <span aria-hidden="true"> {verParametros ? '▲' : '▼'}</span>
        </span>
      </button>
      <dl id="parametros-simulacion"
        className={`${verParametros ? 'grid' : 'hidden'} md:grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-x-4 md:gap-x-8 gap-y-3 md:gap-y-4 text-sm text-tenue`}>
        {([
          ...(perfil
            ? [['Tipo de caso', tituloDelTipo(perfil)], ['Perfil auditivo', detalle(perfil)], ['PTA', `${perfil.pta} dB HL`]]
            : [['Perfil', simulacion.parametros.poles_profile]]),
          ['Frecuencia', `${simulacion.parametros.carrier_freq} Hz`],
          ['Nivel', `${simulacion.parametros.spl_level} dB SPL`],
          ['Modulación', `${simulacion.parametros.f_mod} Hz`],
          ['Fibras', `nH ${simulacion.parametros.nH} · nM ${simulacion.parametros.nM} · nL ${simulacion.parametros.nL}`],
          ['Pedida', formatearFecha(simulacion.creado_en)],
          ...(simulacion.iniciada_en ? [['Iniciada', formatearFecha(simulacion.iniciada_en)]] : []),
          ...(simulacion.finalizada_en ? [['Terminó', formatearFecha(simulacion.finalizada_en)]] : []),
        ] as [string, string][]).map(([nombre, valor]) => (
          <div key={nombre}>
            <dt>{nombre}</dt>
            <dd className="font-medium text-tinta">{valor}</dd>
          </div>
        ))}
      </dl>

      {/* Para quien investiga o quiere replicarla: el nombre en el modelo de Verhulst */}
      <p className="-mt-3 text-xs text-tenue">
        Perfil del modelo: <code className="font-mono">{simulacion.parametros.poles_profile}</code>
      </p>

      {(simulacion.reutilizada || simulacion.caso_id) && (
        <p className="flex flex-wrap gap-x-4 text-sm text-tenue">
          {simulacion.reutilizada && <span>Resultado reutilizado de una simulación idéntica</span>}
          {simulacion.caso_id && (
            <Link to={`/casos/${simulacion.caso_id}`} className="text-acento hover:underline">Ver el caso</Link>
          )}
        </p>
      )}
      {enCurso(simulacion.estado) && <p className="text-sm text-tenue">Esta página se actualiza sola cuando termine.</p>}
      {simulacion.estado === 'error' && (
        <Aviso tipo="error">{simulacion.mensaje_error ?? 'La simulación no se pudo completar.'}</Aviso>
      )}

      {simulacion.resultado && (
        <>
          {perfil && <PerfilSimulado perfil={perfil} />}
          <ResultsSummary result={simulacion.resultado} />
          <PlotsPanel result={simulacion.resultado} />
          <PanelEstadosInternos simulacionId={simulacion.id} />
        </>
      )}
    </div>
  )
}
