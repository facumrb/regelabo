import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Aviso, Campo, Centrada } from '../components/ui'
import { botonPrimario, botonTexto, entrada } from '../components/estilos'
import { useSesion } from '../context/SesionContext'
import { authApi, mensajeDeError } from '../services/auth'

/** Después de entrar con una contraseña temporal (decisión 031): no pide la actual, solo la nueva. */
export default function ElegirContrasena() {
  const { usuario, verificarSesion, cerrarSesion } = useSesion()
  const navigate = useNavigate()
  const [nueva, setNueva] = useState('')
  const [repetida, setRepetida] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (!usuario) return null // RequiereSesion ya redirige; esto solo satisface a TypeScript
  if (!usuario.debe_cambiar_contrasena) return <Navigate to="/" replace />

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    if (nueva !== repetida) {
      setError('Las contraseñas no coinciden.')
      return
    }
    setEnviando(true)
    try {
      await authApi.elegirContrasena(nueva)
      await verificarSesion() // trae el usuario sin la marca: se libera el resto de la app
      navigate('/', { replace: true })
    } catch (e) {
      setError(mensajeDeError(e))
      setEnviando(false)
    }
  }

  return (
    <Centrada titulo="Elegí tu contraseña"
      bajada="Entraste con una contraseña temporal. Elegí una nueva para seguir; la temporal deja de servir."
      pie={<button type="button" onClick={cerrarSesion} className={botonTexto}>Cerrar sesión</button>}>
      <form onSubmit={enviar} noValidate className="space-y-4">
        <input type="email" autoComplete="username" value={usuario.email} readOnly hidden />
        <Campo etiqueta="Contraseña nueva (entre 8 y 128 caracteres)">
          <input className={entrada} type="password" autoComplete="new-password" value={nueva}
            onChange={(e) => setNueva(e.target.value)} />
        </Campo>
        <Campo etiqueta="Repetí la contraseña nueva">
          <input className={entrada} type="password" autoComplete="new-password" value={repetida}
            onChange={(e) => setRepetida(e.target.value)} />
        </Campo>
        {error && <Aviso tipo="error">{error}</Aviso>}
        <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
          {enviando ? 'Guardando…' : 'Guardar y seguir'}
        </button>
      </form>
    </Centrada>
  )
}
