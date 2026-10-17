import { useState, useEffect, useRef } from 'react'
import Header from './components/Header'
import SimulationControls from './components/SimulationControls'
import ResultsSummary from './components/ResultsSummary'
import PlotsPanel from './components/PlotsPanel'
import AudiogramManager from './components/AudiogramManager'
import { Route, Routes } from 'react-router-dom'
import PanelPruebas from './components/PanelPruebas'
import Login from './pages/Login'
import Registro from './pages/Registro'
import RequiereSesion from './components/RequiereSesion'
import MisCasos from './pages/casos/MisCasos'
import NuevoCaso from './pages/casos/NuevoCaso'
import FichaCaso from './pages/casos/FichaCaso'
import MiCuenta from './pages/MiCuenta'
import Bienvenida from './pages/Bienvenida'
import { useSesion } from './context/SesionContext'
import { api } from './services/api'
import { mensajeDeError } from './services/auth'
import type { EstadoServidor, ParametrosSimulacion, ResultadoSimulacion } from './services/tiposSimulacion'

export default function App() {
  const { usuario, cargando } = useSesion()
  const [currentView, setCurrentView] = useState<'simulation' | 'audiogram'>('simulation')
  const [backendHealth, setBackendHealth] = useState<EstadoServidor | null>(null)
  const [profiles, setProfiles] = useState<string[]>([])
  const [params, setParams] = useState<ParametrosSimulacion>({
    carrier_freq: 4000,
    poles_profile: 'Flat00',
    spl_level: 70,
    f_mod: 110,
    nH: 13,
    nM: 3,
    nL: 3,
  })

  const [isLoading, setIsLoading] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [result, setResult] = useState<ResultadoSimulacion | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successToast, setSuccessToast] = useState<string | null>(null)

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

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
      if (availableProfiles.length > 0 && !availableProfiles.includes(params.poles_profile)) {
        setParams(prev => ({ ...prev, poles_profile: availableProfiles[0] }))
      }
    } catch (err) {
      console.warn('No se pudieron cargar los perfiles:', mensajeDeError(err))
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

  // 3. Ejecutar simulación
  const handleRunSimulation = async () => {
    setIsLoading(true)
    setError(null)
    setSuccessToast(null)
    try {
      const data = await api.runSimulation(params)
      setResult(data)
    } catch (err) {
      console.error('Error en simulación:', err)
      setError(mensajeDeError(err))
    } finally {
      setIsLoading(false)
    }
  }

  // 4. Vincular perfil generado desde un audiograma
  const handleSelectProfileFromAudiogram = async (profileName: string) => {
    setParams(prev => ({ ...prev, poles_profile: profileName }))
    await fetchInitialData()
    setCurrentView('simulation')
    setSuccessToast(`Perfil coclear "${profileName}" asignado a la simulación.`)
    setTimeout(() => setSuccessToast(null), 5000)
  }

  return (
    <div className="min-h-screen bg-dark-900 scientific-grid flex flex-col text-slate-100">
      
      {/* Header superior */}
      <Header 
        backendHealth={backendHealth} 
        onRefreshHealth={fetchInitialData} 
      />

      {/* Contenido Principal */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/cuenta" element={<RequiereSesion><MiCuenta /></RequiereSesion>} />
          <Route path="/casos" element={<RequiereSesion><MisCasos /></RequiereSesion>} />
          <Route path="/casos/nuevo" element={<RequiereSesion><NuevoCaso /></RequiereSesion>} />
          <Route path="/casos/:id" element={<RequiereSesion><FichaCaso /></RequiereSesion>} />
          <Route path="*" element={
            cargando ? null : !usuario ? <Bienvenida /> : (
            <>
              {/* Barra de navegación de pestañas principales */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                <div className="flex space-x-2 bg-dark-800 p-1.5 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setCurrentView('simulation')}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
                      currentView === 'simulation'
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span>Simulación Biológica (EFR / ABR)</span>
                  </button>

                  <button
                    onClick={() => setCurrentView('audiogram')}
                    className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
                      currentView === 'audiogram'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span>Carga de Audiogramas (FilePond)</span>
                  </button>
                </div>

                <div className="text-xs text-slate-400 flex items-center space-x-2">
                  <span>Perfil activo:</span>
                  <span className="font-mono text-cyan-400 font-semibold px-2 py-0.5 rounded bg-dark-800 border border-slate-700">
                    {params.poles_profile}
                  </span>
                </div>
              </div>

              {/* Notificación Toast de éxito */}
              {successToast && (
                <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs flex items-center space-x-2 animate-fadeIn">
                  <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>{successToast}</span>
                </div>
              )}

              {/* Banner de error si ocurrió alguno */}
              {error && (
                <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-200 text-xs flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-rose-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{error}</span>
                  </div>
                  <button 
                    onClick={() => setError(null)}
                    className="text-rose-400 hover:text-rose-100 font-bold ml-4"
                  >
                    ✕
                  </button>
                </div>
              )}

              {/* Vista 1: Panel de Simulación */}
              {currentView === 'simulation' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
                  {/* Columna Izquierda: Parámetros (4 columnas de 12) */}
                  <div className="lg:col-span-4 sticky top-24">
                    <SimulationControls
                      profiles={profiles}
                      params={params}
                      setParams={setParams}
                      onRunSimulation={handleRunSimulation}
                      isLoading={isLoading}
                      elapsedTime={elapsedTime}
                    />
                  </div>

                  {/* Columna Derecha: Métricas y Gráficos (8 columnas de 12) */}
                  <div className="lg:col-span-8 space-y-6">
                    <ResultsSummary result={result} />
                    <PlotsPanel result={result} />
                  </div>

                </div>
              )}

              {/* Vista 2: Gestor de Audiogramas con FilePond */}
              {currentView === 'audiogram' && (
                <div className="max-w-4xl mx-auto">
                  <AudiogramManager
                    onSelectProfile={handleSelectProfileFromAudiogram}
                    onRefreshProfiles={fetchInitialData}
                  />
                </div>
              )}
            </>
            )
          } />
        </Routes>

      </main>

      {/* Footer científico */}
      <footer className="border-t border-slate-800/80 py-6 bg-dark-900/60 text-center text-xs text-slate-500">
        <p>
          Laboratorio Virtual Auditivo — Implementación basada en el modelo coclear no-lineal y de tronco encefálico de <strong>Verhulst et al. (2018)</strong>.
        </p>
      </footer>

      <PanelPruebas />
    </div>
  )
}
