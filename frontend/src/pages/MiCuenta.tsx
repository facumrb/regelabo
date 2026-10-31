import { useState, type FormEvent } from 'react'
import { Aviso, Campo, Encabezado, Volver } from '../components/ui'
import { botonPrimario, entrada, etiqueta, panel } from '../components/estilos'
import { useSesion } from '../context/SesionContext'
import { authApi, mensajeDeError } from '../services/auth'

export default function MiCuenta() {
  const { usuario } = useSesion()
  const [actual, setActual] = useState('')
  const [nueva, setNueva] = useState('')
  const [repetida, setRepetida] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [exito, setExito] = useState(false)
  const [enviando, setEnviando] = useState(false)

  if (!usuario) return null // RequiereSesion ya redirige; esto solo satisface a TypeScript

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setExito(false)
    // Lo único que se controla en la pantalla: el servidor solo recibe la actual y la nueva
    if (nueva !== repetida) {
      setError('Las contraseñas nuevas no coinciden.')
      return
    }
    setEnviando(true)
    try {
      await authApi.cambiarContrasena(actual, nueva)
      setExito(true)
      setActual('')
      setNueva('')
      setRepetida('')
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      <Volver a="/" texto="Volver" />
      <Encabezado titulo="Mi cuenta" />
      <dl className={`${panel} p-5 md:p-7 grid grid-cols-[auto_1fr] gap-x-6 gap-y-3`}>
        <dt className="text-tenue">Nombre</dt>
        <dd className="text-tinta break-words">{usuario.nombre}</dd>
        <dt className="text-tenue">Email</dt>
        <dd className="text-tinta break-all">{usuario.email}</dd>
        <dt className="text-tenue">Perfil</dt>
        <dd className="text-tinta">{usuario.tipo_perfil}{usuario.es_admin && ' · admin'}</dd>
      </dl>

      <section className={`${panel} p-5 md:p-7 space-y-5`}>
        <h2 className={etiqueta}>Cambiar contraseña</h2>
        <form onSubmit={enviar} noValidate className="space-y-4">
          {/* El campo de usuario oculto ayuda a los gestores de contraseñas a saber de qué cuenta es */}
          <input type="email" autoComplete="username" value={usuario.email} readOnly hidden />
          <Campo etiqueta="Contraseña actual">
            <input className={entrada} type="password" autoComplete="current-password" value={actual}
              onChange={(e) => setActual(e.target.value)} />
          </Campo>
          <Campo etiqueta="Contraseña nueva (entre 8 y 128 caracteres)">
            <input className={entrada} type="password" autoComplete="new-password" value={nueva}
              onChange={(e) => setNueva(e.target.value)} />
          </Campo>
          <Campo etiqueta="Repetí la contraseña nueva">
            <input className={entrada} type="password" autoComplete="new-password" value={repetida}
              onChange={(e) => setRepetida(e.target.value)} />
          </Campo>
          {error && <Aviso tipo="error">{error}</Aviso>}
          {exito && <Aviso tipo="ok">Contraseña actualizada. Cerramos tus otras sesiones.</Aviso>}
          <button type="submit" disabled={enviando} className={`${botonPrimario} w-full`}>
            {enviando ? 'Guardando…' : 'Cambiar contraseña'}
          </button>
        </form>
      </section>
    </div>
  )
}
