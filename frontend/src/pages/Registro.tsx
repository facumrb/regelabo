import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { Aviso, Campo, Tarjeta } from '../components/ui'
import { botonPrimario, entrada } from '../components/estilos'
import { useSesion } from '../context/SesionContext'
import { mensajeDeError, type TipoPerfil } from '../services/auth'

const PERFILES: { valor: TipoPerfil; etiqueta: string }[] = [
  { valor: 'estudiante', etiqueta: 'Estudiante' },
  { valor: 'investigador', etiqueta: 'Investigador' },
  { valor: 'fonoaudiologo', etiqueta: 'Fonoaudiólogo' },
]

export default function Registro() {
  const { usuario, cargando, registrarse } = useSesion()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [nombre, setNombre] = useState('')
  const [password, setPassword] = useState('')
  const [tipoPerfil, setTipoPerfil] = useState<TipoPerfil>('estudiante')
  const [aceptaAviso, setAceptaAviso] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (cargando) return null
  if (usuario) return <Navigate to="/" replace />

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await registrarse({ email, password, nombre, tipo_perfil: tipoPerfil, acepta_aviso: aceptaAviso })
      navigate('/login', { state: { email } })
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Tarjeta titulo="Crear cuenta">
      {/* noValidate: el navegador no valida nada, así todo llega al servidor y se pueden verificar sus reglas */}
      <form onSubmit={enviar} noValidate className="space-y-4">
        <Campo etiqueta="Email">
          <input className={entrada} type="email" autoComplete="username" value={email}
            onChange={(e) => setEmail(e.target.value)} />
        </Campo>
        <Campo etiqueta="Nombre">
          <input className={entrada} type="text" autoComplete="name" value={nombre}
            onChange={(e) => setNombre(e.target.value)} />
        </Campo>
        <Campo etiqueta="Contraseña (entre 8 y 128 caracteres)">
          <input className={entrada} type="password" autoComplete="new-password" value={password}
            onChange={(e) => setPassword(e.target.value)} />
        </Campo>
        <Campo etiqueta="Tipo de perfil">
          <select className={entrada} value={tipoPerfil} onChange={(e) => setTipoPerfil(e.target.value as TipoPerfil)}>
            {PERFILES.map((p) => (
              <option key={p.valor} value={p.valor}>{p.etiqueta}</option>
            ))}
          </select>
        </Campo>
        <label className="flex items-start space-x-2 text-xs text-slate-300">
          <input type="checkbox" className="mt-0.5" checked={aceptaAviso}
            onChange={(e) => setAceptaAviso(e.target.checked)} />
          <span>
            Entiendo que esta herramienta es de estudio y experimentación, no es de uso profesional, y que
            sus resultados no constituyen un diagnóstico clínico.
          </span>
        </label>
        {error && <Aviso tipo="error">{error}</Aviso>}
        <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
          {enviando ? 'Creando cuenta…' : 'Registrarse'}
        </button>
      </form>
      <p className="text-xs text-slate-400 text-center">
        ¿Ya tenés cuenta? <Link to="/login" className="text-cyan-400 hover:underline">Iniciá sesión</Link>
      </p>
    </Tarjeta>
  )
}
