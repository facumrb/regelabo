import { useEffect, useState } from 'react'
import { Aviso } from '../../components/ui'
import { botonSecundario, botonTexto, entrada, panel, vacio } from '../../components/estilos'
import { mensajeDeError, type TipoPerfil } from '../../services/auth'
import { avisarPendientes, comentariosApi, type Comentario, type EstadoComentario } from '../../services/comentarios'

const ESTADOS: Record<EstadoComentario, string> = { nuevo: 'Nuevo', leido: 'Leído', archivado: 'Archivado' }
export const TIPOS: Record<TipoPerfil, string> = {
  estudiante: 'Estudiante', investigador: 'Investigador', fonoaudiologo: 'Fonoaudiólogo',
}
const ACCIONES: Record<EstadoComentario, string> = {
  nuevo: 'Marcar como nuevo', leido: 'Marcar como leído', archivado: 'Archivar',
}

/** Comentarios y sugerencias de los usuarios (RN13, decisión 028). */
export default function ComentariosAdmin() {
  const [estado, setEstado] = useState<EstadoComentario | ''>('')
  const [tipo, setTipo] = useState<TipoPerfil | ''>('')
  const [comentarios, setComentarios] = useState<Comentario[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargar = async (despuesDe: string | null) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await comentariosApi.listar({ estado: estado || undefined, tipo: tipo || undefined }, despuesDe)
      setComentarios((anteriores) => (despuesDe ? [...anteriores, ...pagina.comentarios] : pagina.comentarios))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar(null)
  }, [estado, tipo])

  const cambiar = async (id: string, nuevo: EstadoComentario) => {
    setError(null)
    try {
      const cambiado = await comentariosApi.cambiarEstado(id, nuevo)
      avisarPendientes()
      // Si ya no entra en el filtro (ej. se archivó viendo los no archivados), sale de la lista
      const sigueVisible = estado ? cambiado.estado === estado : cambiado.estado !== 'archivado'
      setComentarios((lista) => (sigueVisible
        ? lista.map((c) => (c.id === id ? cambiado : c))
        : lista.filter((c) => c.id !== id)))
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-3">
        <label className="sm:w-56 space-y-1.5">
          <span className="text-sm text-tenue">Estado</span>
          <select className={entrada} value={estado} onChange={(e) => setEstado(e.target.value as EstadoComentario | '')}>
            <option value="">Sin archivar</option>
            {Object.entries(ESTADOS).map(([v, texto]) => <option key={v} value={v}>{texto}</option>)}
          </select>
        </label>
        <label className="sm:w-56 space-y-1.5">
          <span className="text-sm text-tenue">Tipo de usuario</span>
          <select className={entrada} value={tipo} onChange={(e) => setTipo(e.target.value as TipoPerfil | '')}>
            <option value="">Todos</option>
            {Object.entries(TIPOS).map(([v, texto]) => <option key={v} value={v}>{texto}</option>)}
          </select>
        </label>
      </div>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && comentarios.length === 0 && <p className={vacio}>No hay comentarios.</p>}

      <ul className="space-y-3">
        {comentarios.map((c) => (
          <li key={c.id} className={`${panel} p-4 md:p-5 space-y-3`}>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
              <span className="font-medium text-tinta">{c.autor_nombre}</span>
              <span className="text-tenue">{TIPOS[c.autor_tipo]}</span>
              <span className="text-tenue break-all">{c.autor_email}</span>
              <span className="text-tenue">{new Date(c.creado_en).toLocaleString('es-AR')}</span>
              <span className={`ml-auto text-xs px-2 py-0.5 rounded-full border border-linea ${
                c.estado === 'nuevo' ? 'text-acento font-semibold' : 'text-tenue'}`}>
                {ESTADOS[c.estado]}
              </span>
            </div>
            <p className="text-tinta whitespace-pre-wrap break-words">{c.texto}</p>
            <div className="flex flex-wrap gap-2">
              {(Object.keys(ACCIONES) as EstadoComentario[]).filter((e) => e !== c.estado).map((e) => (
                <button key={e} type="button" onClick={() => cambiar(c.id, e)} className={botonTexto}>
                  {ACCIONES[e]}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ul>

      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
    </div>
  )
}
