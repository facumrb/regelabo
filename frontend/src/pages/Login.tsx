import { useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Aviso, Campo, Tarjeta } from '../components/ui'
import { botonPrimario, entrada } from '../components/estilos'
import { useSesion } from '../context/SesionContext'
import { mensajeDeError } from '../services/auth'

export default function Login() {
  const { usuario, cargando, iniciarSesion } = useSesion()
  const navigate = useNavigate()
  const desdeRegistro = useLocation().state as { email: string } | null
  const [email, setEmail] = useState(desdeRegistro?.email ?? '')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (cargando) return null
  if (usuario) return <Navigate to="/" replace />

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await iniciarSesion(email, password)
      navigate('/')
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Tarjeta titulo="Iniciar sesión">
      {desdeRegistro && <Aviso tipo="ok">Cuenta creada. Ya podés iniciar sesión.</Aviso>}
      {/* noValidate: el navegador no valida nada, así todo llega al servidor y se pueden verificar sus reglas */}
      <form onSubmit={enviar} noValidate className="space-y-4">
        <Campo etiqueta="Email">
          <input className={entrada} type="email" autoComplete="username" value={email}
            onChange={(e) => setEmail(e.target.value)} />
        </Campo>
        <Campo etiqueta="Contraseña">
          <input className={entrada} type="password" autoComplete="current-password" value={password}
            onChange={(e) => setPassword(e.target.value)} />
        </Campo>
        {error && <Aviso tipo="error">{error}</Aviso>}
        <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
          {enviando ? 'Ingresando…' : 'Iniciar sesión'}
        </button>
      </form>
      <p className="text-xs text-slate-400 text-center">
        ¿No tenés cuenta? <Link to="/registro" className="text-cyan-400 hover:underline">Registrate</Link>
      </p>
    </Tarjeta>
  )
}
