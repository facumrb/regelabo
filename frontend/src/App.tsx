import { useState, useEffect, useRef } from 'react'
import Header from './components/Header'
import CurvasPerfil from './components/CurvasPerfil'
import { avisoError, avisoOk } from './components/estilos'
import { Volver } from './components/ui'
import SimulationControls from './components/SimulationControls'
import AudiogramManager from './components/AudiogramManager'
import { AvisoSimulacionTerminada } from './components/AvisosSimulacion'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import PanelPruebas from './components/PanelPruebas'
import Login from './pages/Login'
import Registro from './pages/Registro'
import RequiereSesion from './components/RequiereSesion'
import MisCasos from './pages/casos/MisCasos'
import NuevoCaso from './pages/casos/NuevoCaso'
import FichaCaso from './pages/casos/FichaCaso'
import MiCuenta from './pages/MiCuenta'
import Historial from './pages/simulaciones/Historial'
import DetalleSimulacion from './pages/simulaciones/DetalleSimulacion'
import Bienvenida from './pages/Bienvenida'
import Inicio from './pages/Inicio'
import { useSesion } from './context/SesionContext'
import { useSimulacionesEnCurso } from './context/SimulacionesEnCurso'
import { api } from './services/api'
import { mensajeDeError } from './services/auth'
import { casosApi, type Caso } from './services/casos'
import { simulacionesApi } from './services/simulaciones'
import type { EstadoServidor, ParametrosSimulacion, PerfilAuditivo } from './services/tiposSimulacion'

const PARAMETROS_INICIALES: ParametrosSimulacion = {
  carrier_freq: 4000,
  poles_profile: 'Flat00',
  spl_level: 70,
  f_mod: 110,
  nH: 13,
  nM: 3,
  nL: 3,
}

/** Lo que el detalle le pasa a Simular: "Nueva simulación" (vacío) o "con estos parámetros" */
export interface EstadoNuevaSimulacion {
  parametros?: ParametrosSimulacion
  casoId?: string | null
  perfil?: PerfilAuditivo | null
}

// Tiempo para ver "✓ Simulación lista" antes de pasar al detalle (decisión 024)
const PAUSA_ANTES_DEL_DETALLE_MS = 1500

export default function App() {
  const { usuario, cargando } = useSesion()
  const navigate = useNavigate()
  const location = useLocation()
  const { enCurso: pendientes, terminadas, esperada, esperar, dejarDeEsperar, marcarVista } = useSimulacionesEnCurso()
  const [backendHealth, setBackendHealth] = useState<EstadoServidor | null>(null)
  const [profiles, setProfiles] = useState<PerfilAuditivo[]>([])
  // El generado desde un audiograma: no viene en /profiles (sería visible para todos, RN4)
  const [perfilPersonalizado, setPerfilPersonalizado] = useState<PerfilAuditivo | null>(null)
  // Los últimos parámetros usados quedan en el formulario al volver a Simular
  const [params, setParams] = useState<ParametrosSimulacion>(PARAMETROS_INICIALES)

  const [enviando, setEnviando] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [casos, setCasos] = useState<Caso[]>([])
  const [casoId, setCasoId] = useState('') // '' = sin caso
  // La que se espera desde el formulario: sigue en el contexto aunque se navegue a otra pantalla
  const simulacion = pendientes.find(s => s.id === esperada) ?? null
  const terminada = terminadas.find(s => s.id === esperada) ?? null
  const isLoading = enviando || esperada !== null
  const [error, setError] = useState<string | null>(null)
  const [successToast, setSuccessToast] = useState<string | null>(null)

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const perfilActivo = profiles.find(p => p.nombre === params.poles_profile)
    ?? (perfilPersonalizado?.nombre === params.poles_profile ? perfilPersonalizado : null)

  // 1. Cargar salud del backend y lista de perfiles al montar
  const fetchInitialData = async () => {
    try {
      const health = await api.getHealth()
      setBackendHealth(health)
    } catch (err) {
      console.warn('Backend no disponible:', mensajeDeError(err))
      setBackendHealth({ status: 'offline', c_solver_available: false })
    }

    if (!usuario) return // los perfiles piden sesión

    try {
      const availableProfiles = await api.getProfiles()
      setProfiles(availableProfiles)
      if (availableProfiles.length > 0 && !availableProfiles.some(p => p.nombre === params.poles_profile)
          && perfilPersonalizado?.nombre !== params.poles_profile) {
        setParams(prev => ({ ...prev, poles_profile: availableProfiles[0].nombre }))
      }
    } catch (err) {
      console.warn('No se pudieron cargar los perfiles:', mensajeDeError(err))
    }

    try {
      // shortcut: el selector ofrece solo los 100 casos más nuevos; si hace falta más, paginar o buscar
      setCasos((await casosApi.listar(null, 100)).casos)
    } catch (err) {
      console.warn('No se pudieron cargar los casos:', mensajeDeError(err))
    }
  }

  // Se repite al iniciar o cerrar sesión: los perfiles solo se piden con sesión
  useEffect(() => {
    fetchInitialData()
  }, [usuario])

  // 2. Timer durante la ejecución de la simulación
  useEffect(() => {
    if (isLoading) {
      setElapsedTime(0)
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isLoading])

  // 3. Ejecutar simulación: el pedido solo la deja en cola; el contexto consulta su estado
  const handleRunSimulation = async () => {
    setEnviando(true)
    setError(null)
    setSuccessToast(null)
    try {
      const actual = await simulacionesApi.crear(params, casoId || null)
      // Resultado reutilizado (RN10): no hay nada que esperar
      if (actual.estado === 'completada') navigate(`/simulaciones/${actual.id}`)
      else esperar(actual)
    } catch (err) {
      console.error('Error en simulación:', err)
      setError(mensajeDeError(err))
    } finally {
      setEnviando(false)
    }
  }

  // Al terminar la esperada: si se la mira desde Simular, pasa al detalle tras una pausa; si no, avisa la barra
  useEffect(() => {
    if (!terminada) return
    const enSimular = location.pathname === '/simular'
    if (terminada.estado === 'error') {
      setError(terminada.mensaje_error ?? 'La simulación no se pudo completar.')
      if (enSimular) marcarVista(terminada.id)
      dejarDeEsperar()
      return
    }
    if (!enSimular) {
      dejarDeEsperar()
      return
    }
    const temporizador = setTimeout(() => {
      dejarDeEsperar()
      navigate(`/simulaciones/${terminada.id}`)
    }, PAUSA_ANTES_DEL_DETALLE_MS)
    return () => clearTimeout(temporizador)
  }, [terminada, location.pathname])

  // Desde el detalle: "Nueva simulación" llega sin parámetros (formulario inicial) o "con estos parámetros"
  useEffect(() => {
    const estado = location.state as EstadoNuevaSimulacion | null
    if (location.pathname !== '/simular' || !estado) return
    setParams(estado.parametros ?? PARAMETROS_INICIALES)
    setCasoId(estado.casoId ?? '')
    // Personalizados y perfiles fuera del catálogo (decisión 026) no están en el selector: se suman
    if (estado.perfil) setPerfilPersonalizado(estado.perfil)
    navigate('/simular', { replace: true, state: null }) // se aplica una sola vez
  }, [location.key])

  // 4. Usar el perfil generado desde un audiograma: lleva directo a la simulación con el perfil elegido
  const handleSelectProfileFromAudiogram = (perfil: PerfilAuditivo) => {
    setPerfilPersonalizado(perfil)
    setParams(prev => ({ ...prev, poles_profile: perfil.nombre }))
    navigate('/simular')
    setSuccessToast(`Perfil "${perfil.etiqueta}" listo para simular.`)
    setTimeout(() => setSuccessToast(null), 5000)
  }

  const simulador = (
    <div className="space-y-6">
      {/* Notificación de éxito */}
      {successToast && (
        <div role="status" className={`px-4 py-3 rounded-xl border text-sm ${avisoOk}`}>{successToast}</div>
      )}

      {/* Banner de error si ocurrió alguno */}
      {error && (
        <div role="alert" className={`px-4 py-3 rounded-xl border text-sm flex items-center justify-between gap-4 ${avisoError}`}>
          <span>{error}</span>
          <button onClick={() => setError(null)} aria-label="Cerrar el aviso"
            className="grid place-items-center w-11 h-11 -my-2 -mr-2 shrink-0 opacity-70 hover:opacity-100">✕</button>
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-tinta">Nueva simulación</h1>
          <p className="mt-1.5 text-tenue">Configuración del estímulo acústico y perfil coclear</p>
        </div>
        <span title="Estímulo de amplitud modulada rectangular" className="shrink-0 mt-1 font-mono text-xs text-tenue border border-linea rounded px-2 py-1">RAM Stimulus</span>
      </div>

      {/* El resultado no se muestra acá: al terminar se pasa a su detalle */}
      <SimulationControls
        profiles={profiles}
        perfilActivo={perfilActivo}
        params={params}
        setParams={setParams}
        onRunSimulation={handleRunSimulation}
        isLoading={isLoading}
        elapsedTime={elapsedTime}
        simulacion={simulacion ?? terminada}
        lista={terminada?.estado === 'completada'}
        casos={casos}
        casoId={casoId}
        setCasoId={setCasoId}
        vistaPrevia={
          <section aria-label="Vista previa del audiograma" className="pt-4 border-t border-linea">
            <h3 className="text-sm font-medium text-tinta">Vista previa del audiograma</h3>
            <p className="text-sm text-tenue">
              {perfilActivo?.etiqueta ?? params.poles_profile}
              {perfilActivo && <> · PTA {perfilActivo.pta} dB HL</>}
            </p>
            {perfilActivo && (
              <div className="mt-2">
                <div className="lg:hidden"><CurvasPerfil perfil={perfilActivo} alto={170} /></div>
                <div className="hidden lg:block"><CurvasPerfil perfil={perfilActivo} alto={260} /></div>
              </div>
            )}
          </section>
        }
      />
    </div>
  )

  return (
    <div className={`min-h-screen flex flex-col ${usuario ? 'pb-[calc(56px+env(safe-area-inset-bottom))] md:pb-0' : ''}`}>
      {/* Para teclado y lectores de pantalla: evita recorrer toda la barra en cada página */}
      <a href="#contenido" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:rounded-lg focus:bg-panel focus:text-tinta focus:border focus:border-acento">
        Saltar al contenido
      </a>
      <Header backendHealth={backendHealth} onRefreshHealth={fetchInitialData} />

      <main id="contenido" tabIndex={-1} className="flex-1 outline-none max-w-7xl w-full mx-auto px-4 md:px-8 py-6 md:py-12">
        <Routes>
          <Route path="/" element={cargando ? null : usuario ? <Inicio /> : <Bienvenida />} />
          <Route path="/simular" element={<RequiereSesion>{simulador}</RequiereSesion>} />
          {/* Paso previo de la simulación: genera un perfil y vuelve a /simular con él elegido (decisión 024) */}
          <Route path="/simular/audiograma" element={
            <RequiereSesion>
              <div className="max-w-5xl mx-auto space-y-4">
                <Volver a="/simular" texto="Volver" />
                <AudiogramManager onSelectProfile={handleSelectProfileFromAudiogram} />
              </div>
            </RequiereSesion>
          } />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/cuenta" element={<RequiereSesion><MiCuenta /></RequiereSesion>} />
          <Route path="/simulaciones" element={<RequiereSesion><Historial /></RequiereSesion>} />
          <Route path="/simulaciones/:id" element={<RequiereSesion><DetalleSimulacion /></RequiereSesion>} />
          <Route path="/casos" element={<RequiereSesion><MisCasos /></RequiereSesion>} />
          <Route path="/casos/nuevo" element={<RequiereSesion><NuevoCaso /></RequiereSesion>} />
          <Route path="/casos/:id" element={<RequiereSesion><FichaCaso /></RequiereSesion>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="border-t border-linea py-6 px-4 text-center text-sm text-tenue">
        Laboratorio Virtual Auditivo — Implementación basada en el modelo coclear no-lineal y de tronco encefálico de{' '}
        <strong className="font-semibold text-tinta">Verhulst et al. (2018)</strong>.
      </footer>

      <AvisoSimulacionTerminada />
      <PanelPruebas />
    </div>
  )
}
