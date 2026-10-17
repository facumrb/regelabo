import { Link } from 'react-router-dom'
import { useSesion } from '../context/SesionContext'
import { botonPrimario, botonSecundario } from './estilos'

/** Parte derecha del navbar: botones de acceso, o el usuario con su botón de cerrar sesión. */
export default function BotonesSesion() {
  const { usuario, cargando, cerrarSesion } = useSesion()

  if (cargando) return null // evita que los botones parpadeen mientras se recupera la sesión

  if (!usuario) {
    return (
      <div className="flex items-center space-x-2">
        <Link to="/login" className={botonSecundario}>
          Iniciar sesión
        </Link>
        <Link to="/registro" className={botonPrimario}>
          Registrarse
        </Link>
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-3">
      <Link to="/casos" className={botonSecundario}>
        Mis casos
      </Link>
      <Link to="/cuenta" title="Mi cuenta" className="text-right leading-tight hover:opacity-80 transition">
        <div className="flex items-center justify-end space-x-2 text-sm font-semibold text-white">
          <span>{usuario.nombre}</span>
          {usuario.es_admin && (
            <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 rounded-full">
              admin
            </span>
          )}
        </div>
        <div className="text-[11px] text-slate-400">
          {usuario.email} · {usuario.tipo_perfil}
        </div>
      </Link>
      <button onClick={cerrarSesion} className={botonSecundario}>
        Cerrar sesión
      </button>
    </div>
  )
}
