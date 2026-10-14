import React, { useState } from 'react'

export default function SimulationControls({
  profiles,
  params,
  setParams,
  onRunSimulation,
  isLoading,
  elapsedTime
}) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const quickFrequencies = [500, 1000, 2000, 4000]

  const handleChange = (field, value) => {
    setParams(prev => ({ ...prev, [field]: value }))
  }

  // Ayudante de descripción del perfil
  const getProfileDescription = (profile) => {
    if (profile === 'Flat00' || profile === 'Normal') return 'Audición Normal (control)'
    if (profile?.startsWith('Flat')) return 'Pérdida Sensorineural Plana (todas las frecs.)'
    if (profile?.startsWith('Slope')) return 'Pérdida en Pendiente (frecuencias agudas)'
    return 'Perfil patológico coclear'
  }

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl space-y-6">
      
      {/* Header del panel */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span>Parámetros de Simulación</span>
          </h2>
          <p className="text-xs text-slate-400">Configuración del estímulo acústico y perfil coclear</p>
        </div>
        <span className="text-xs font-mono text-cyan-400/80 bg-cyan-950/40 px-2 py-1 rounded border border-cyan-800/40">
          RAM Stimulus
        </span>
      </div>

      <div className="space-y-5">
        
        {/* 1. Perfil Auditivo (Polos de Shera) */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-medium text-slate-300">
              Perfil Auditivo (Audiograma)
            </label>
            <span className="text-[11px] text-cyan-400 font-mono">
              {getProfileDescription(params.poles_profile)}
            </span>
          </div>
          <select
            value={params.poles_profile}
            onChange={(e) => handleChange('poles_profile', e.target.value)}
            disabled={isLoading}
            className="w-full bg-dark-800 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition cursor-pointer"
          >
            {profiles.length > 0 ? (
              profiles.map(p => (
                <option key={p} value={p}>
                  {p} — {getProfileDescription(p)}
                </option>
              ))
            ) : (
              <option value="Flat00">Flat00 (Audición Normal)</option>
            )}
          </select>
        </div>

        {/* 2. Frecuencia Portadora (Carrier Frequency) */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-medium text-slate-300">
              Frecuencia Portadora (Hz)
            </label>
            <span className="text-xs font-mono font-bold text-cyan-400">
              {params.carrier_freq} Hz
            </span>
          </div>

          {/* Quick buttons */}
          <div className="grid grid-cols-4 gap-2 mb-2">
            {quickFrequencies.map(f => (
              <button
                key={f}
                type="button"
                disabled={isLoading}
                onClick={() => handleChange('carrier_freq', f)}
                className={`py-1.5 text-xs font-medium rounded-lg border transition ${
                  params.carrier_freq === f
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-semibold'
                    : 'bg-dark-800 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                {f} Hz
              </button>
            ))}
          </div>

          <input
            type="range"
            min="250"
            max="8000"
            step="250"
            value={params.carrier_freq}
            onChange={(e) => handleChange('carrier_freq', parseFloat(e.target.value))}
            disabled={isLoading}
            className="w-full accent-cyan-400 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* 3. Nivel de Intensidad (dB SPL) */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-medium text-slate-300">
              Intensidad del Estímulo (dB SPL)
            </label>
            <span className="text-xs font-mono font-bold text-cyan-400">
              {params.spl_level} dB SPL
            </span>
          </div>
          <input
            type="range"
            min="20"
            max="95"
            step="5"
            value={params.spl_level}
            onChange={(e) => handleChange('spl_level', parseFloat(e.target.value))}
            disabled={isLoading}
            className="w-full accent-cyan-400 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>20 dB (Muy bajo)</span>
            <span>70 dB (Estándar clínico)</span>
            <span>95 dB (Elevado)</span>
          </div>
        </div>

        {/* 4. Frecuencia de Modulación */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-medium text-slate-300">
              Frecuencia de Modulación ($f_{'{mod}'}$)
            </label>
            <span className="text-xs font-mono font-bold text-cyan-400">
              {params.f_mod} Hz
            </span>
          </div>
          <input
            type="range"
            min="50"
            max="250"
            step="10"
            value={params.f_mod}
            onChange={(e) => handleChange('f_mod', parseFloat(e.target.value))}
            disabled={isLoading}
            className="w-full accent-cyan-400 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* 5. Parámetros Biológicos Avanzados (Sinaptopatía) */}
        <div className="pt-2 border-t border-slate-800/80">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-cyan-400 transition py-1"
          >
            <span className="flex items-center space-x-1.5">
              <span>Fibras del Nervio Auditivo (Sinaptopatía)</span>
            </span>
            <span>{showAdvanced ? '▲ Ocultar' : '▼ Configurar'}</span>
          </button>

          {showAdvanced && (
            <div className="mt-3 p-3.5 rounded-xl bg-dark-800/80 border border-slate-800 space-y-3 animate-fadeIn">
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Modulá las fibras por célula ciliada interna para simular pérdida sináptica coclear (sordera oculta).
              </p>
              
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Fibras HSR (Alta tasa, nH):</span>
                  <span className="font-mono text-cyan-400 font-bold">{params.nH}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="20"
                  value={params.nH}
                  onChange={(e) => handleChange('nH', parseInt(e.target.value))}
                  disabled={isLoading}
                  className="w-full accent-cyan-400 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Fibras MSR (Media tasa, nM):</span>
                  <span className="font-mono text-cyan-400 font-bold">{params.nM}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={params.nM}
                  onChange={(e) => handleChange('nM', parseInt(e.target.value))}
                  disabled={isLoading}
                  className="w-full accent-cyan-400 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Fibras LSR (Baja tasa, nL):</span>
                  <span className="font-mono text-cyan-400 font-bold">{params.nL}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={params.nL}
                  onChange={(e) => handleChange('nL', parseInt(e.target.value))}
                  disabled={isLoading}
                  className="w-full accent-cyan-400 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Botón de Ejecución Principal */}
      <button
        type="button"
        onClick={onRunSimulation}
        disabled={isLoading}
        className={`w-full py-3.5 px-4 rounded-xl font-semibold text-sm flex items-center justify-center space-x-2 transition shadow-lg ${
          isLoading
            ? 'bg-cyan-600/50 text-cyan-100 cursor-not-allowed shadow-none'
            : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/25 active:scale-[0.98]'
        }`}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Simulando modelo biológico... ({elapsedTime}s)</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Ejecutar Simulación Biológica</span>
          </>
        )}
      </button>

    </div>
  )
}
