import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useSesion } from '../context/SesionContext'
import { useSimulacionesEnCurso } from '../context/SimulacionesEnCurso'
import { IndicadorSimulaciones } from './AvisosSimulacion'
import { cambiarTema, useTema } from '../context/tema'
import Icono, { type NombreIcono } from './Icono'
import { botonPrimario, botonTexto } from './estilos'
import type { EstadoServidor } from '../services/tiposSimulacion'

const SECCIONES: { a: string; texto: string; icono: NombreIcono }[] = [
  { a: '/', texto: 'Inicio', icono: 'inicio' },
  { a: '/simular', texto: 'Simular', icono: 'simular' },
  { a: '/casos', texto: 'Casos', icono: 'casos' },
  { a: '/simulaciones', texto: 'Historial', icono: 'historial' },
]

function BotonTema() {
  const tema = useTema()
  const siguiente = tema === 'claro' ? 'oscuro' : 'claro'
  return (
    <button onClick={() => cambiarTema(siguiente)} aria-label={`Cambiar a tema ${siguiente}`} title={`Tema ${siguiente}`}
      className="grid place-items-center w-11 h-11 rounded-lg border border-linea text-tenue hover:text-tinta">
      <Icono nombre={tema === 'claro' ? 'luna' : 'sol'} tamano={18} />
    </button>
  )
}

/** Menú de usuario (decisión 024): Cuenta, tema y Salir. Se cierra con Escape o al hacer clic afuera. */
function MenuUsuario() {
  const { usuario, cerrarSesion } = useSesion()
  const tema = useTema()
  const navigate = useNavigate()
  const [abierto, setAbierto] = useState(false)
  const caja = useRef<HTMLDivElement>(null)
  const boton = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!abierto) return
    const alClic = (e: MouseEvent) => { if (!caja.current?.contains(e.target as Node)) setAbierto(false) }
    const alTeclear = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      setAbierto(false)
      boton.current?.focus()
    }
    document.addEventListener('mousedown', alClic)
    document.addEventListener('keydown', alTeclear)
    return () => {
      document.removeEventListener('mousedown', alClic)
      document.removeEventListener('keydown', alTeclear)
    }
  }, [abierto])

  if (!usuario) return null
  const opcion = 'flex items-center gap-3 w-full min-h-[44px] px-3 rounded-lg text-left text-sm text-tinta ' +
    'hover:bg-acento-suave focus-visible:bg-acento-suave'
  const elegir = (accion: () => void) => () => { setAbierto(false); accion() }

  return (
    <div className="relative" ref={caja}>
      <button ref={boton} onClick={() => setAbierto(!abierto)} aria-haspopup="menu" aria-expanded={abierto}
        aria-label={`Menú de ${usuario.nombre}`}
        className="flex items-center gap-2 min-h-[44px] pl-1 pr-2 md:pr-3 rounded-full border border-linea text-sm text-tinta hover:border-tenue">
        <span className="grid place-items-center w-8 h-8 rounded-full bg-acento text-acento-tinta font-semibold text-sm">
          {usuario.nombre.charAt(0).toUpperCase()}
        </span>
        <span className="hidden md:inline">{usuario.nombre}</span>
        <Icono nombre="abajo" tamano={16} className={`text-tenue transition-transform ${abierto ? 'rotate-180' : ''}`} />
      </button>

      {abierto && (
        <div role="menu"
          className="fixed md:absolute inset-x-3 md:inset-x-auto md:right-0 top-[3.75rem] md:top-[calc(100%+0.5rem)] md:w-64 z-50 bg-panel border border-linea rounded-xl p-1.5 shadow-xl">
          <div className="px-3 pt-2 pb-3 mb-1.5 border-b border-linea">
            <div className="flex items-center gap-2 text-tinta font-medium">
              {usuario.nombre}
              {usuario.es_admin && <span className="text-[11px] px-1.5 rounded-full border border-linea text-tenue">admin</span>}
            </div>
            <div className="text-sm text-tenue truncate">{usuario.email} · {usuario.tipo_perfil}</div>
          </div>
          <button role="menuitem" className={opcion} onClick={elegir(() => navigate('/cuenta'))}>
            <Icono nombre="cuenta" tamano={18} className="text-tenue" />Cuenta
          </button>
          <button role="menuitem" className={opcion} onClick={() => cambiarTema(tema === 'claro' ? 'oscuro' : 'claro')}>
            <Icono nombre={tema === 'claro' ? 'luna' : 'sol'} tamano={18} className="text-tenue" />Tema
            <span className="ml-auto text-tenue">{tema === 'claro' ? 'Claro' : 'Oscuro'}</span>
          </button>
          {usuario.es_admin && (
            <a role="menuitem" href="/api/docs" target="_blank" rel="noreferrer" className={`${opcion} xl:hidden`}>
              <Icono nombre="descargar" tamano={18} className="text-tenue -rotate-90" />Swagger API
            </a>
          )}
          <hr className="border-linea my-1.5" />
          <button role="menuitem" className={opcion} onClick={elegir(cerrarSesion)}>
            <Icono nombre="salir" tamano={18} className="text-tenue" />Cerrar sesión
          </button>
        </div>
      )}
    </div>
  )
}

/** Estado del backend y del solver; un clic vuelve a consultarlo. `compacto`: solo el punto. */
function EstadoServidorChip({ estado, onRefrescar, compacto }: {
  estado: EstadoServidor | null; onRefrescar: () => void; compacto?: boolean
}) {
  const isOnline = estado?.status === 'online'
  const texto = isOnline ? 'Backend Online' : 'Backend Desconectado'
  const solver = estado?.c_solver_available ? 'Solver C Activo' : 'Solver Python'
  return (
    <button onClick={onRefrescar} title="Hacer clic para reconectar con el backend"
      aria-label={compacto ? `${texto}${isOnline ? ` · ${solver}` : ''}. Reconectar` : undefined}
      className={`flex items-center gap-2 rounded-lg border border-linea bg-panel text-xs text-tinta hover:border-tenue transition ${
        compacto ? 'w-11 h-11 justify-center' : 'min-h-[36px] px-3'
      }`}>
      <span className={`w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} aria-hidden="true" />
      {!compacto && <span>{texto}</span>}
      {!compacto && isOnline && (
        <span className={`text-[10px] px-1.5 py-0.5 rounded ${estado?.c_solver_available
          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300'
          : 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300'}`}>
          {solver}
        </span>
      )}
    </button>
  )
}

const enlaceSwagger = (
  <a href="/api/docs" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs text-tenue hover:text-acento transition">
    <span>Swagger API</span>
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  </a>
)

/** Barra superior; con sesión, en el celular las secciones pasan a una barra inferior de pestañas. */
export default function Header({ backendHealth, onRefreshHealth }: { backendHealth: EstadoServidor | null; onRefreshHealth: () => void }) {
  const { usuario, cargando } = useSesion()
  const { enCurso, terminadas } = useSimulacionesEnCurso()
  // En el celular no entra el indicador: un punto sobre la pestaña Simular avisa que hay algo
  const novedades = enCurso.length + terminadas.length > 0

  return (
    <>
      <header className="sticky top-0 z-40 bg-fondo border-b border-linea">
        <div className="max-w-7xl mx-auto px-4 md:px-8 h-14 md:h-16 flex items-center gap-4 md:gap-8">
          <Link to="/" className="flex items-center gap-2 shrink-0 text-tinta">
            <Icono nombre="marca" tamano={22} className="text-acento shrink-0" />
            <span className="font-semibold tracking-tight">regelabo</span>
          </Link>

          {usuario && (
            <nav aria-label="Secciones"
              className="fixed md:static inset-x-0 bottom-0 z-40 grid grid-cols-4 md:flex md:gap-1 md:flex-1 bg-panel md:bg-transparent border-t border-linea md:border-0 pb-[env(safe-area-inset-bottom)] md:pb-0">
              {SECCIONES.map(({ a, texto, icono }) => (
                // NavLink marca activa también /casos/:id y /simulaciones/:id; "/" solo en la raíz
                <NavLink key={a} to={a}
                  className={({ isActive }) => `flex flex-col md:flex-row items-center justify-center gap-1 min-h-[56px] md:min-h-[40px] md:px-3 md:rounded-lg text-xs md:text-sm ${
                    isActive ? 'text-acento md:text-tinta md:bg-acento-suave' : 'text-tenue hover:text-tinta'
                  }`}>
                  <span className="relative md:hidden">
                    <Icono nombre={icono} tamano={22} />
                    {a === '/simular' && novedades && (
                      <span className="absolute -top-0.5 -right-1 w-2.5 h-2.5 rounded-full bg-acento ring-2 ring-panel" aria-hidden="true" />
                    )}
                  </span>
                  {texto}
                  {a === '/simular' && novedades && <span className="sr-only"> (hay simulaciones en curso o terminadas)</span>}
                </NavLink>
              ))}
            </nav>
          )}

          <div className="ml-auto flex items-center gap-2 md:gap-3 shrink-0">
            {usuario && <IndicadorSimulaciones />}
            {/* Información técnica: solo para administradores (decisión 024) */}
            {usuario?.es_admin && (
              <>
                <div className="hidden xl:flex items-center gap-3">
                  <EstadoServidorChip estado={backendHealth} onRefrescar={onRefreshHealth} />
                  {enlaceSwagger}
                </div>
                <div className="xl:hidden">
                  <EstadoServidorChip estado={backendHealth} onRefrescar={onRefreshHealth} compacto />
                </div>
              </>
            )}
            {!cargando && !usuario && (
              <>
                <Link to="/login" className={`${botonTexto} hidden sm:inline-flex`}>Iniciar sesión</Link>
                <Link to="/registro" className={botonPrimario}>Registrarse</Link>
              </>
            )}
            {(!usuario || cargando) && <BotonTema />}
            <MenuUsuario />
          </div>
        </div>
      </header>
      {/* En el celular sin sesión, Iniciar sesión va debajo de la barra */}
      {!cargando && !usuario && (
        <div className="sm:hidden px-4 py-2 border-b border-linea">
          <Link to="/login" className="text-sm text-acento font-medium">Iniciar sesión</Link>
        </div>
      )}
    </>
  )
}
