import type { Dispatch, ReactNode, SetStateAction } from 'react'
import { Link } from 'react-router-dom'
import Icono from './Icono'
import { avisoPrevio } from './CurvasPerfil'
import { avisoAtencion, botonPrimario, botonSecundario, entrada, etiqueta, panel } from './estilos'
import { Deslizador, EstadoChip } from './ui'
import { detalle, TIPOS, tipoDe, type Tipo } from './perfiles'
import type { Caso } from '../services/casos'
import type { ParametrosSimulacion, PerfilAuditivo, Simulacion } from '../services/tiposSimulacion'

const FRECUENCIAS_RAPIDAS = [500, 1000, 2000, 4000]

interface Props {
  profiles: PerfilAuditivo[]
  /** El perfil elegido; puede ser uno personalizado, que no está en `profiles` */
  perfilActivo: PerfilAuditivo | null
  params: ParametrosSimulacion
  setParams: Dispatch<SetStateAction<ParametrosSimulacion>>
  onRunSimulation: () => void
  /** Mientras se manda el pedido (un instante): después se pasa al detalle de la nueva */
  enviando: boolean
  /** Las del usuario en cola o ejecutando: se puede pedir otra hasta el cupo (RN5a) */
  enCurso: Simulacion[]
  casos: Caso[]
  casoId: string
  setCasoId: (id: string) => void
  /** Vista previa del perfil elegido: va al pie del paso 1 */
  vistaPrevia: ReactNode
}

export default function SimulationControls({
  profiles,
  perfilActivo,
  params,
  setParams,
  onRunSimulation,
  enviando,
  enCurso,
  casos,
  casoId,
  setCasoId,
  vistaPrevia,
}: Props) {
  const handleChange = <K extends keyof ParametrosSimulacion>(field: K, value: ParametrosSimulacion[K]) => {
    setParams(prev => ({ ...prev, [field]: value }))
  }

  // El personalizado elegido no viene en la lista (es de este usuario): se suma a su grupo
  const opciones = perfilActivo && !profiles.some(p => p.nombre === perfilActivo.nombre)
    ? [perfilActivo, ...profiles]
    : profiles
  const aviso = perfilActivo ? avisoPrevio(perfilActivo) : null
  const tipoActivo = perfilActivo ? tipoDe(perfilActivo) : 'normal'
  const tiposDisponibles = TIPOS.filter(({ tipo }) => opciones.some(p => tipoDe(p) === tipo))
  const delTipo = opciones.filter(p => tipoDe(p) === tipoActivo)

  // Al cambiar de tipo se elige su primer perfil, el de menor pérdida (el backend los manda ordenados por PTA)
  const elegirTipo = (tipo: Tipo) => {
    const primero = opciones.find(p => tipoDe(p) === tipo)
    if (primero) handleChange('poles_profile', primero.nombre)
  }

  return (
    // Paso 1 a la izquierda y paso 2 a la derecha, de alto parecido; en el celular, uno debajo del otro
    <div className="grid gap-6 lg:gap-8 lg:grid-cols-2 items-start">
      <section className={`${panel} p-5 space-y-3.5`}>
        <h2 className={etiqueta}>1 · Caso y perfil</h2>
        <div className="grid gap-4">
          <label className="block">
            <span className="block text-sm text-tenue mb-1.5">Caso (opcional)</span>
            <select value={casoId} onChange={(e) => setCasoId(e.target.value)} disabled={enviando} className={entrada}>
              <option value="">Sin caso</option>
              {casos.map((c) => (
                <option key={c.id} value={c.id}>{c.alias}</option>
              ))}
            </select>
          </label>
          {tiposDisponibles.length > 0 && (
            <label className="block">
              <span className="block text-sm text-tenue mb-1.5">Tipo de caso</span>
              <select value={tipoActivo} disabled={enviando} className={entrada}
                onChange={(e) => elegirTipo(e.target.value as Tipo)}>
                {tiposDisponibles.map(({ tipo, titulo }) => <option key={tipo} value={tipo}>{titulo}</option>)}
              </select>
            </label>
          )}
          <div>
            <label htmlFor="perfil-auditivo" className="block text-sm text-tenue mb-1.5">Perfil auditivo</label>
            <div className="grid grid-cols-[1fr_auto] gap-2">
              <select id="perfil-auditivo" value={params.poles_profile} disabled={enviando} className={entrada}
                onChange={(e) => handleChange('poles_profile', e.target.value)}>
                {delTipo.length > 0 ? (
                  delTipo.map(p => <option key={p.nombre} value={p.nombre}>{detalle(p)}</option>)
                ) : (
                  <option value="Flat00">Sin pérdida (0 dB HL)</option>
                )}
              </select>
              {/* Sin aria-label: lo que se ve y lo que lee el lector de pantalla es lo mismo (WCAG 2.5.3) */}
              <Link to="/simular/audiograma" aria-disabled={enviando}
                className={`${botonSecundario} px-3 gap-2 ${enviando ? 'pointer-events-none opacity-50' : ''}`}>
                <Icono nombre="subir" tamano={18} />Cargar audiograma
              </Link>
            </div>
            <p className="mt-1.5 text-sm text-tenue">¿Buscás otra configuración? Cargá su audiograma y se genera el perfil.</p>
          </div>
        </div>
        {/* Cartel previo (Q20): no frena, solo avisa que el perfil se simulará recortado */}
        {aviso && <p role="status" className={`text-sm border rounded-lg px-3 py-2 ${avisoAtencion}`}>⚠ {aviso}</p>}
        {vistaPrevia}
      </section>

      <div className="space-y-6">
        <section className={`${panel} p-5 space-y-4`}>
          <h2 className={etiqueta}>2 · Estímulo</h2>
          {/* Uno por fila: de a dos, la barra quedaba de ~6rem en la columna de 30rem */}
          <div className="grid gap-5">
            <Deslizador id="nivel" etiqueta="Intensidad del estímulo" unidad="dB SPL" min={20} max={95} paso={5}
              valor={params.spl_level} deshabilitado={enviando} onCambio={(v) => handleChange('spl_level', v)}
              marcas={['20 · muy bajo', '70 · estándar clínico', '95 · elevado']} />
            <div className="space-y-2">
              <Deslizador id="frecuencia" etiqueta="Frecuencia portadora" unidad="Hz" min={250} max={8000} paso={250}
                valor={params.carrier_freq} deshabilitado={enviando} onCambio={(v) => handleChange('carrier_freq', v)} />
              <div className="flex flex-wrap gap-1.5" role="group" aria-label="Frecuencias habituales">
                {FRECUENCIAS_RAPIDAS.map(f => (
                  <button key={f} type="button" disabled={enviando} onClick={() => handleChange('carrier_freq', f)}
                    aria-pressed={params.carrier_freq === f}
                    className={`min-h-[36px] px-3 rounded-full border text-xs font-medium transition ${
                      params.carrier_freq === f
                        ? 'bg-acento-suave border-acento text-tinta'
                        : 'border-linea text-tenue hover:text-tinta hover:border-tenue'
                    }`}>
                    {f} Hz
                  </button>
                ))}
              </div>
            </div>
            <Deslizador id="modulacion" etiqueta="Frecuencia de modulación" sigla="f_mod" unidad="Hz" min={50} max={250} paso={10}
              valor={params.f_mod} deshabilitado={enviando} onCambio={(v) => handleChange('f_mod', v)} />
          </div>

          <details className="group border-t border-linea pt-3">
            <summary className="flex items-center justify-between min-h-[44px] cursor-pointer list-none text-sm font-medium text-tinta">
              Fibras del Nervio Auditivo (Sinaptopatía)
              <span className="text-tenue group-open:hidden">▼ Configurar</span>
              <span className="text-tenue hidden group-open:inline">▲ Ocultar</span>
            </summary>
            <div className="pt-3 space-y-4">
              <p className="text-sm text-tenue">
                Modulá las fibras por célula ciliada interna para simular pérdida sináptica coclear (sordera oculta).
              </p>
              <div className="grid gap-4">
                <Deslizador id="nh" etiqueta="Alta tasa (HSR)" sigla="nH" unidad="fibras" min={0} max={20} valor={params.nH}
                  deshabilitado={enviando} onCambio={(v) => handleChange('nH', Math.round(v))} />
                <Deslizador id="nm" etiqueta="Media tasa (MSR)" sigla="nM" unidad="fibras" min={0} max={10} valor={params.nM}
                  deshabilitado={enviando} onCambio={(v) => handleChange('nM', Math.round(v))} />
                <Deslizador id="nl" etiqueta="Baja tasa (LSR)" sigla="nL" unidad="fibras" min={0} max={10} valor={params.nL}
                  deshabilitado={enviando} onCambio={(v) => handleChange('nL', Math.round(v))} />
              </div>
            </div>
          </details>
        </section>

        <button type="button" onClick={onRunSimulation} disabled={enviando}
          className={`${botonPrimario} w-full min-h-[52px] text-base`}>
          {enviando && (
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          <span aria-live="polite">{enviando ? 'Pidiendo la simulación…' : 'Ejecutar Simulación Biológica'}</span>
        </button>
        {/* La caché (RN10) es por huella: no se puede anticipar cuáles salen al instante */}
        <p className="-mt-4 text-center text-sm text-tenue">
          Tarda unos 80 s. Si esta misma combinación ya se calculó antes, el resultado aparece al instante.
        </p>
        {enCurso.length > 0 && (
          <section aria-labelledby="titulo-en-curso" className={`${panel} p-4 space-y-2`}>
            <h2 id="titulo-en-curso" className="text-sm font-medium text-tinta">
              {enCurso.length === 1 ? '1 simulación en curso' : `${enCurso.length} simulaciones en curso`}
            </h2>
            <p className="text-xs text-tenue">
              Podés pedir otra mientras tanto, hasta tu cupo de simultáneas. La barra avisa cuando termine cada una.
            </p>
            <ul className="space-y-1">
              {enCurso.map((s) => (
                <li key={s.id} className="flex flex-wrap items-center gap-x-3 text-sm">
                  <EstadoChip estado={s.estado} extra={s.estado === 'en_cola' && s.posicion ? ` (lugar ${s.posicion})` : ''} />
                  <span className="font-mono text-xs text-tenue">
                    {s.parametros.carrier_freq} Hz @ {s.parametros.spl_level} dB
                  </span>
                  <Link to={`/simulaciones/${s.id}`} className="ml-auto inline-flex items-center min-h-[44px] text-acento hover:underline">
                    Ver detalle
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}
