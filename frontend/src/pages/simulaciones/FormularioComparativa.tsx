import { useEffect, useState, type FormEvent } from 'react'
import { Aviso, Campo } from '../../components/ui'
import { botonPrimario, botonTexto, entrada, panel } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import { casosApi, type Caso } from '../../services/casos'
import type { DatosComparativa } from '../../services/comparativas'

/** Título, notas y caso opcional de una comparativa: para guardarla y para editarla (decisión 025). */
export default function FormularioComparativa({ inicial, textoBoton, alGuardar, alCancelar }: {
  inicial: DatosComparativa
  textoBoton: string
  alGuardar: (datos: DatosComparativa) => Promise<void>
  alCancelar: () => void
}) {
  const [titulo, setTitulo] = useState(inicial.titulo)
  const [notas, setNotas] = useState(inicial.notas ?? '')
  const [casoId, setCasoId] = useState(inicial.caso_id ?? '')
  const [casos, setCasos] = useState<Caso[]>([])
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    // shortcut: ofrece solo los 100 casos más nuevos, como Simular
    casosApi.listar(null, 100).then((p) => setCasos(p.casos)).catch(() => setCasos([]))
  }, [])

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await alGuardar({ titulo, notas: notas.trim() || null, caso_id: casoId || null })
    } catch (e) {
      setError(mensajeDeError(e))
      setEnviando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className={`${panel} p-5 space-y-4 print:hidden`}>
      <Campo etiqueta="Título">
        <input className={entrada} value={titulo} maxLength={100} onChange={(e) => setTitulo(e.target.value)}
          placeholder="Ej: Sordera oculta, mismas fibras" autoFocus />
      </Campo>
      <Campo etiqueta="Notas (opcional)">
        <textarea className={`${entrada} min-h-[5rem] resize-y`} value={notas} maxLength={2000}
          onChange={(e) => setNotas(e.target.value)} />
      </Campo>
      <Campo etiqueta="Caso (opcional)">
        <select className={entrada} value={casoId} onChange={(e) => setCasoId(e.target.value)}>
          <option value="">Sin caso</option>
          {casos.map((c) => <option key={c.id} value={c.id}>{c.alias}</option>)}
        </select>
      </Campo>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <div className="flex flex-wrap justify-end gap-2">
        <button type="button" onClick={alCancelar} className={botonTexto}>Cancelar</button>
        <button type="submit" disabled={enviando || !titulo.trim()} className={botonPrimario}>
          {enviando ? 'Guardando…' : textoBoton}
        </button>
      </div>
    </form>
  )
}
