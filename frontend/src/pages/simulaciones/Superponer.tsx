import { useEffect, useState, type ReactNode } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import type { Data } from 'plotly.js'
import Grafico from '../../components/Grafico'
import EtiquetaPerfil from '../../components/EtiquetaPerfil'
import { layoutBase, TRAZOS, useColoresGrafico } from '../../components/graficos'
import { Aviso, Encabezado, Volver } from '../../components/ui'
import { botonPrimario, botonSecundario, panel } from '../../components/estilos'
import { imprimirEnClaro } from '../../context/tema'
import { mensajeDeError } from '../../services/auth'
import { formatearFecha, simulacionesApi } from '../../services/simulaciones'
import type { OndasABR, Simulacion } from '../../services/tiposSimulacion'
import { comparativasApi, type Comparativa } from '../../services/comparativas'
import FormularioComparativa from './FormularioComparativa'

export const MINIMO = 2
export const MAXIMO = 4

/** Dirección de la pantalla sin guardar; una comparativa guardada se abre con ?comparativa=<id> (decisión 025). */
export const enlaceSuperponer = (ids: string[]) => `/superponer?ids=${ids.join(',')}`

type Onda = 'efr_wave' | 'w1' | 'w3' | 'w5'
const ONDAS: [Onda, string][] = [['efr_wave', 'EFR total'], ['w1', 'Onda I'], ['w3', 'Onda III'], ['w5', 'Onda V']]

const nombre = (i: number) => `S${i + 1}`

/** Filas de la tabla: cómo mostrar el valor y con qué compararlo para resaltar lo que difiere. */
const FILAS: { titulo: string; valor: (s: Simulacion) => ReactNode; clave: (s: Simulacion) => string | number }[] = [
  { titulo: 'Perfil auditivo', valor: (s) => <EtiquetaPerfil nombre={s.parametros.poles_profile} />,
    clave: (s) => s.parametros.poles_profile },
  { titulo: 'Frecuencia portadora', valor: (s) => `${s.parametros.carrier_freq} Hz`, clave: (s) => s.parametros.carrier_freq },
  { titulo: 'Nivel', valor: (s) => `${s.parametros.spl_level} dB SPL`, clave: (s) => s.parametros.spl_level },
  { titulo: 'Frecuencia de modulación', valor: (s) => `${s.parametros.f_mod} Hz`, clave: (s) => s.parametros.f_mod },
  { titulo: 'Fibras nH / nM / nL', valor: (s) => `${s.parametros.nH} / ${s.parametros.nM} / ${s.parametros.nL}`,
    clave: (s) => `${s.parametros.nH}/${s.parametros.nM}/${s.parametros.nL}` },
  { titulo: 'EFR', valor: (s) => `${s.resultado!.efr_value_uv.toFixed(4)} µV`,
    clave: (s) => s.resultado!.efr_value_uv.toFixed(4) },
  { titulo: 'Pedida', valor: (s) => formatearFecha(s.creado_en), clave: (s) => s.id },
]

/** CSV de la tabla: una fila por simulación, separado por comas y con punto decimal. */
function descargarCsv(simulaciones: Simulacion[]) {
  const encabezado = ['simulacion', 'id', 'perfil', 'frecuencia_portadora_hz', 'nivel_db_spl', 'frecuencia_modulacion_hz',
    'nH', 'nM', 'nL', 'efr_uv', 'pedida']
  const filas = simulaciones.map((s, i) => {
    const p = s.parametros
    return [nombre(i), s.id, p.poles_profile, p.carrier_freq, p.spl_level, p.f_mod, p.nH, p.nM, p.nL,
      s.resultado!.efr_value_uv, s.creado_en]
  })
  const texto = [encabezado, ...filas].map((fila) => fila.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\r\n')
  // BOM: así Excel reconoce los acentos (UTF-8)
  const enlace = document.createElement('a')
  enlace.href = URL.createObjectURL(new Blob(['\ufeff' + texto], { type: 'text/csv;charset=utf-8' }))
  enlace.download = 'superposicion-simulaciones.csv'
  enlace.click()
  setTimeout(() => URL.revokeObjectURL(enlace.href), 1000) // revocarlo enseguida puede cortar la descarga
}

/**
 * Superponer de 2 a 4 simulaciones propias y terminadas (decisión 025), sin guardar (?ids=) o una
 * comparativa guardada (?comparativa=), que se puede editar o borrar. RN4 la cumple el backend.
 */
export default function Superponer() {
  const navigate = useNavigate()
  const [parametros, setParametros] = useSearchParams()
  const comparativaId = parametros.get('comparativa')
  const [comparativa, setComparativa] = useState<Comparativa | null>(null)
  const [formulario, setFormulario] = useState<'guardar' | 'editar' | null>(null)
  const ids = comparativa?.simulacion_ids ?? [...new Set((parametros.get('ids') ?? '').split(',').filter(Boolean))]
  const clave = ids.join(',')
  const [simulaciones, setSimulaciones] = useState<Simulacion[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [onda, setOnda] = useState<Onda>('efr_wave')
  const c = useColoresGrafico()

  useEffect(() => {
    if (!comparativaId) {
      setComparativa(null)
      return
    }
    if (comparativa?.id === comparativaId) return // recién guardada: ya se tiene
    setError(null)
    comparativasApi.ver(comparativaId).then(setComparativa).catch((e) => setError(mensajeDeError(e)))
  }, [comparativaId])

  useEffect(() => {
    setSimulaciones(null)
    if (comparativaId && !comparativa) return // todavía se carga la comparativa
    setError(null)
    if (ids.length < MINIMO || ids.length > MAXIMO) {
      setError(`Elegí entre ${MINIMO} y ${MAXIMO} simulaciones desde el historial.`)
      return
    }
    let activo = true
    Promise.all(ids.map((id) => simulacionesApi.ver(id)))
      .then((lista) => {
        if (!activo) return
        if (lista.some((s) => s.estado !== 'completada' || !s.resultado)) {
          setError('Solo se pueden superponer simulaciones terminadas. Elegí otras desde el historial.')
        } else {
          setSimulaciones(lista)
        }
      })
      .catch((e) => { if (activo) setError(mensajeDeError(e)) })
    return () => { activo = false }
  }, [clave])

  const guardar = async (datos: Parameters<typeof comparativasApi.crear>[0]) => {
    const nueva = await comparativasApi.crear(datos, ids)
    setComparativa(nueva)
    setFormulario(null)
    setParametros({ comparativa: nueva.id }, { replace: true })
  }

  const editar = async (datos: Parameters<typeof comparativasApi.editar>[1]) => {
    setComparativa(await comparativasApi.editar(comparativa!.id, datos))
    setFormulario(null)
  }

  const borrar = async () => {
    if (!comparativa || !window.confirm(`¿Borrar la comparativa "${comparativa.titulo}"? Las simulaciones no se borran.`)) return
    try {
      await comparativasApi.borrar(comparativa.id)
      navigate('/simulaciones?ver=comparativas', { replace: true })
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  const encabezado = (
    <>
      <div className="print:hidden"><Volver a="/simulaciones" texto="Volver" /></div>
      <Encabezado titulo={comparativa?.titulo ?? 'Superponer simulaciones'}
        bajada={comparativa ? (comparativa.notas ?? 'Comparativa guardada.')
          : 'Las curvas de cada simulación en un mismo gráfico, para ver qué cambia entre ellas.'}>
        {simulaciones && !formulario && (
          comparativa ? (
            <>
              <button type="button" onClick={() => setFormulario('editar')} className={`${botonSecundario} print:hidden`}>
                Editar
              </button>
              <button type="button" onClick={borrar}
                className={`${botonSecundario} print:hidden hover:!border-rose-400 hover:!text-rose-700 dark:hover:!text-rose-300`}>
                Borrar
              </button>
            </>
          ) : (
            <button type="button" onClick={() => setFormulario('guardar')} className={`${botonPrimario} print:hidden`}>
              Guardar comparativa
            </button>
          )
        )}
        {simulaciones && (
          <>
            <button type="button" onClick={() => descargarCsv(simulaciones)} className={`${botonSecundario} print:hidden`}>
              Descargar CSV
            </button>
            <button type="button" onClick={imprimirEnClaro} className={`${botonSecundario} print:hidden`}>
              Imprimir o guardar PDF
            </button>
          </>
        )}
      </Encabezado>
      {formulario === 'guardar' && (
        <FormularioComparativa inicial={{ titulo: '', notas: null, caso_id: null }} textoBoton="Guardar"
          alGuardar={guardar} alCancelar={() => setFormulario(null)} />
      )}
      {formulario === 'editar' && comparativa && (
        <FormularioComparativa inicial={comparativa} textoBoton="Guardar cambios"
          alGuardar={editar} alCancelar={() => setFormulario(null)} />
      )}
    </>
  )

  if (error) {
    return (
      <div className="space-y-6">
        {encabezado}
        <Aviso tipo="error">{error}</Aviso>
        <Link to="/simulaciones" className={botonSecundario}>Ir al historial</Link>
      </div>
    )
  }
  if (!simulaciones) return <div className="space-y-6">{encabezado}</div>

  // Mismo color y trazo para cada simulación en los dos gráficos y en la tabla
  const estilo = (i: number) => ({ color: c.series[i], dash: TRAZOS[i] })
  const fft: Data[] = simulaciones.map((s, i) => ({
    x: s.resultado!.fft_spectrum.frequencies, y: s.resultado!.fft_spectrum.amplitudes,
    type: 'scatter', mode: 'lines', name: nombre(i), line: { ...estilo(i), width: 2 },
    hovertemplate: `${nombre(i)} · %{x:.1f} Hz: %{y:.4f} µV<extra></extra>`,
  }))
  const ondas: Data[] = simulaciones.map((s, i) => {
    const abr: OndasABR = s.resultado!.abr_waves
    return {
      x: abr.time_ms, y: abr[onda], type: 'scatter', mode: 'lines', name: nombre(i), line: { ...estilo(i), width: 2 },
      hovertemplate: `${nombre(i)} · %{x:.2f} ms: %{y:.4f} µV<extra></extra>`,
    }
  })
  const margen = { l: 52, r: 16, t: 16, b: 90 }

  return (
    <div className="aparecer space-y-6">
      {encabezado}

      <div className={`${panel} overflow-x-auto`}>
        <table className="w-full text-sm" aria-label="Diferencias entre las simulaciones">
          <thead>
            <tr>
              <th scope="col" className="text-left px-4 py-3 text-xs font-medium uppercase tracking-wider text-tenue">Dato</th>
              {simulaciones.map((s, i) => (
                <th key={s.id} scope="col" className="text-left px-4 py-3">
                  <Link to={`/simulaciones/${s.id}`} className="inline-flex items-center gap-2 font-semibold text-tinta hover:underline">
                    <span className="inline-block w-5 border-t-[3px]"
                      style={{ borderColor: c.series[i], borderTopStyle: i % 2 ? 'dashed' : 'solid' }} aria-hidden="true" />
                    {nombre(i)}
                  </Link>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {FILAS.map((fila) => {
              const difiere = new Set(simulaciones.map(fila.clave)).size > 1 && fila.titulo !== 'Pedida'
              return (
                <tr key={fila.titulo} className="border-t border-linea">
                  <th scope="row" className="text-left px-4 py-3 font-normal text-tenue whitespace-nowrap">
                    {fila.titulo}{difiere && <span className="sr-only"> (difiere)</span>}
                  </th>
                  {simulaciones.map((s) => (
                    <td key={s.id} className={`px-4 py-3 ${difiere ? 'font-semibold text-acento' : 'text-tinta'}`}>
                      {fila.valor(s)}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
        <p className="px-4 pb-3 text-xs text-tenue">En color, los datos que cambian entre las simulaciones.</p>
      </div>

      <div className={`${panel} p-3 md:p-5 break-inside-avoid`}>
        <Grafico titulo="Espectro FFT del EFR" archivo="superposicion-fft" data={fft}
          layout={layoutBase(c, {
            xaxis: { title: { text: 'Frecuencia (Hz)' }, range: [0, 600] },
            yaxis: { title: { text: 'Amplitud (µV)' } },
            margin: margen,
          })} />
      </div>

      <div className={`${panel} p-3 md:p-5 space-y-3 break-inside-avoid`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-linea">
          <span className="text-sm text-tenue">Onda que se superpone</span>
          <div className="flex flex-wrap gap-1.5 print:hidden" role="group" aria-label="Onda que se superpone">
            {ONDAS.map(([v, texto]) => (
              <button key={v} type="button" onClick={() => setOnda(v)} aria-pressed={onda === v}
                className={`min-h-[36px] px-3 rounded-full border text-xs font-medium transition ${
                  onda === v ? 'bg-acento-suave border-acento text-tinta' : 'border-linea text-tenue hover:text-tinta'
                }`}>
                {texto}
              </button>
            ))}
          </div>
        </div>
        <Grafico titulo={`Dominio temporal: ${ONDAS.find(([v]) => v === onda)![1]}`} archivo={`superposicion-${onda}`}
          data={ondas}
          layout={layoutBase(c, {
            xaxis: { title: { text: 'Tiempo (ms)' }, range: [0, 50] },
            yaxis: { title: { text: 'Amplitud (µV)' } },
            margin: margen,
          })} />
      </div>
    </div>
  )
}
