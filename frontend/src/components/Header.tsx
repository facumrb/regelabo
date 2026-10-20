import { Link } from 'react-router-dom'
import BotonesSesion from './BotonesSesion'
import type { EstadoServidor } from '../services/tiposSimulacion'

interface Props {
  backendHealth: EstadoServidor | null
  onRefreshHealth: () => void
}

export default function Header({ backendHealth, onRefreshHealth }: Props) {
  const isOnline = backendHealth?.status === 'online'
  const hasCSolver = backendHealth?.c_solver_available

  return (
    <header className="border-b border-slate-800/80 bg-dark-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-tight">Laboratorio Virtual Auditivo</h1>
              <span className="px-2 py-0.5 text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-full">
                Verhulst 2018
              </span>
            </div>
            <p className="text-xs text-slate-400">Simulación biofísica de la vía auditiva y cálculo de EFR / ABR</p>
          </div>
        </Link>

        {/* Server Status Indicators */}
        <div className="flex items-center space-x-4">
          <div 
            onClick={onRefreshHealth}
            title="Hacer clic para reconectar con el backend"
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-dark-800 border border-slate-800 text-xs cursor-pointer hover:border-slate-700 transition"
          >
            <span className={`w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
            <span className="text-slate-300">
              {isOnline ? 'Backend Online' : 'Backend Desconectado'}
            </span>
            {isOnline && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${hasCSolver ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>
                {hasCSolver ? 'Solver C Activo' : 'Solver Python'}
              </span>
            )}
          </div>

          <a 
            href="/api/docs" 
            target="_blank" 
            rel="noreferrer"
            className="text-xs text-slate-400 hover:text-cyan-400 transition flex items-center space-x-1"
          >
            <span>Swagger API</span>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>

          <BotonesSesion />
        </div>

      </div>
    </header>
  )
}
