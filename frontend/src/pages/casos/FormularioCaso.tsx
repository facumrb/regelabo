import { useState, type FormEvent } from 'react'
import { Aviso, Campo } from '../../components/ui'
import { botonPrimario, botonSecundario, entrada } from '../../components/estilos'
import { mensajeDeError } from '../../services/auth'
import type { DatosCaso, Sexo } from '../../services/casos'

const VACIO: DatosCaso = { alias: '', edad: null, sexo: null, notas: null }

/** Formulario de crear y de editar: recibe los datos iniciales y qué hacer al guardar. */
export default function FormularioCaso({ inicial = VACIO, alGuardar, alCancelar }: {
  inicial?: DatosCaso
  alGuardar: (datos: DatosCaso) => Promise<void>
  alCancelar: () => void
}) {
  const [alias, setAlias] = useState(inicial.alias)
  const [edad, setEdad] = useState(inicial.edad?.toString() ?? '')
  const [sexo, setSexo] = useState<Sexo | ''>(inicial.sexo ?? '')
  const [notas, setNotas] = useState(inicial.notas ?? '')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      // Vacío se manda como null; las reglas (alias obligatorio, edad 0–120…) las valida el servidor
      await alGuardar({ alias, edad: edad === '' ? null : Number(edad), sexo: sexo || null, notas: notas || null })
    } catch (e) {
      setError(mensajeDeError(e))
      setEnviando(false)
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="space-y-4">
      <Campo etiqueta="Alias *">
        <input className={entrada} type="text" value={alias} placeholder="Caso 1 – Trauma leve"
          onChange={(e) => setAlias(e.target.value)} />
      </Campo>
      <p className="text-sm text-tenue -mt-2">
        No uses nombres, DNI ni otros datos que identifiquen a una persona real.
      </p>
      <div className="grid grid-cols-2 gap-4">
        <Campo etiqueta="Edad">
          <input className={entrada} type="number" value={edad} onChange={(e) => setEdad(e.target.value)} />
        </Campo>
        <Campo etiqueta="Sexo">
          <select className={entrada} value={sexo} onChange={(e) => setSexo(e.target.value as Sexo | '')}>
            <option value="">Sin especificar</option>
            <option value="femenino">Femenino</option>
            <option value="masculino">Masculino</option>
            <option value="otro">Otro</option>
          </select>
        </Campo>
      </div>
      <Campo etiqueta="Notas">
        <textarea className={entrada} rows={4} value={notas} onChange={(e) => setNotas(e.target.value)} />
      </Campo>
      {error && <Aviso tipo="error">{error}</Aviso>}
      <div className="flex justify-end gap-2">
        <button type="button" onClick={alCancelar} className={botonSecundario}>Cancelar</button>
        <button type="submit" disabled={enviando} className={botonPrimario}>
          {enviando ? 'Guardando…' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
