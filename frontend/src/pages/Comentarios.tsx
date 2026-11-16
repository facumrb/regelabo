import { useState, type FormEvent } from 'react'
import { Aviso, Campo, Centrada, Volver } from '../components/ui'
import { botonPrimario, botonSecundario, entrada } from '../components/estilos'
import { mensajeDeError } from '../services/auth'
import { comentariosApi, LARGO_MAXIMO } from '../services/comentarios'

/** RN13: un solo campo; al enviar, "¡Gracias!" y nada más (el autor no ve estados ni respuestas). */
export default function Comentarios() {
  const [texto, setTexto] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviado, setEnviado] = useState(false)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await comentariosApi.enviar(texto)
      setEnviado(true)
      setTexto('')
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  if (enviado) {
    return (
      <Centrada titulo="¡Gracias!" bajada="Recibimos tu comentario.">
        <button type="button" onClick={() => setEnviado(false)} className={`${botonSecundario} w-full`}>
          Dejar otro comentario
        </button>
      </Centrada>
    )
  }

  return (
    <div className="space-y-4">
      <div className="max-w-md mx-auto"><Volver a="/" texto="Volver" /></div>
      <Centrada titulo="Dejanos un comentario o sugerencia"
        bajada="Contanos qué mejorarías, qué no se entiende o si encontraste un error.">
        <form onSubmit={enviar} noValidate className="space-y-4">
          {error && <Aviso tipo="error">{error}</Aviso>}
          <Campo etiqueta="Comentario">
            <textarea className={`${entrada} min-h-[10rem] resize-y`} value={texto} maxLength={LARGO_MAXIMO}
              onChange={(e) => setTexto(e.target.value)} required />
          </Campo>
          <p className="text-xs text-tenue text-right" aria-live="polite">{texto.length} / {LARGO_MAXIMO}</p>
          <button type="submit" disabled={enviando || !texto.trim()} className={`${botonPrimario} w-full`}>
            {enviando ? 'Enviando…' : 'Enviar'}
          </button>
        </form>
      </Centrada>
    </div>
  )
}
