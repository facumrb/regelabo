import React, { useState } from 'react'
import { FilePond } from 'react-filepond'
import 'filepond/dist/filepond.min.css'
import Plot from 'react-plotly.js'
import { api } from '../services/api'

export default function AudiogramManager({ onSelectProfile, onRefreshProfiles }) {
  const [activeTab, setActiveTab] = useState('interactive') // 'interactive' | 'filepond'
  const [patientName, setPatientName] = useState('Paciente 01')
  const [files, setFiles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState(null)

  // Puntos audiométricos por defecto (Audición típica)
  const [points, setPoints] = useState([
    { frequency: 250, hearing_loss_db: 15 },
    { frequency: 500, hearing_loss_db: 15 },
    { frequency: 1000, hearing_loss_db: 20 },
    { frequency: 2000, hearing_loss_db: 35 },
    { frequency: 4000, hearing_loss_db: 50 },
    { frequency: 8000, hearing_loss_db: 60 },
  ])

  // Presets clínicos para carga rápida
  const presets = {
    normal: {
      name: 'Audición Normal',
      data: [
        { frequency: 250, hearing_loss_db: 10 },
        { frequency: 500, hearing_loss_db: 10 },
        { frequency: 1000, hearing_loss_db: 10 },
        { frequency: 2000, hearing_loss_db: 15 },
        { frequency: 4000, hearing_loss_db: 10 },
        { frequency: 8000, hearing_loss_db: 15 },
      ]
    },
    presbycusis: {
      name: 'Presbiacusia (Pérdida en Agudos)',
      data: [
        { frequency: 250, hearing_loss_db: 15 },
        { frequency: 500, hearing_loss_db: 20 },
        { frequency: 1000, hearing_loss_db: 25 },
        { frequency: 2000, hearing_loss_db: 45 },
        { frequency: 4000, hearing_loss_db: 65 },
        { frequency: 8000, hearing_loss_db: 75 },
      ]
    },
    trauma: {
      name: 'Trauma Acústico (Caída en 4 kHz)',
      data: [
        { frequency: 250, hearing_loss_db: 10 },
        { frequency: 500, hearing_loss_db: 15 },
        { frequency: 1000, hearing_loss_db: 15 },
        { frequency: 2000, hearing_loss_db: 25 },
        { frequency: 4000, hearing_loss_db: 60 },
        { frequency: 8000, hearing_loss_db: 30 },
      ]
    },
    flat_moderate: {
      name: 'Hipoacusia Plana Moderada',
      data: [
        { frequency: 250, hearing_loss_db: 40 },
        { frequency: 500, hearing_loss_db: 40 },
        { frequency: 1000, hearing_loss_db: 45 },
        { frequency: 2000, hearing_loss_db: 45 },
        { frequency: 4000, hearing_loss_db: 50 },
        { frequency: 8000, hearing_loss_db: 45 },
      ]
    }
  }

  const applyPreset = (key) => {
    setPoints(presets[key].data)
    setPatientName(presets[key].name)
    setAnalysisResult(null)
  }

  const handlePointChange = (freq, newDb) => {
    setPoints(prev =>
      prev.map(p => (p.frequency === freq ? { ...p, hearing_loss_db: parseFloat(newDb) } : p))
    )
    setAnalysisResult(null)
  }

  // 1. Enviar audiograma interactivo
  const handleProcessManual = async () => {
    setIsProcessing(true)
    setError(null)
    try {
      const res = await api.submitManualAudiogram(patientName, points)
      setAnalysisResult(res)
      if (onRefreshProfiles) onRefreshProfiles()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  // 2. Procesar archivo subido con FilePond
  const handleProcessFile = async () => {
    if (files.length === 0) return
    setIsProcessing(true)
    setError(null)
    try {
      const fileItem = files[0].file
      const res = await api.uploadAudiogram(fileItem, patientName)
      setAnalysisResult(res)
      setPoints(res.points)
      if (onRefreshProfiles) onRefreshProfiles()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  // Descargar CSV de plantilla
  const downloadTemplate = () => {
    const csvContent = "data:text/csv;charset=utf-8,frecuencia_hz,perdida_db\n250,15\n500,20\n1000,25\n2000,35\n4000,50\n8000,60"
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", "plantilla_audiograma.csv")
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  // Configuración del gráfico audiométrico estándar (Plotly)
  const audiogramPlotData = [
    {
      x: points.map(p => p.frequency),
      y: points.map(p => p.hearing_loss_db),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Umbral Auditivo (dB HL)',
      line: { color: '#ef4444', width: 2.5 },
      marker: { color: '#ef4444', size: 9, symbol: 'circle-open', line: { width: 2.5 } },
      hovertemplate: '%{x} Hz: %{y} dB HL<extra></extra>',
    }
  ]

  const audiogramPlotLayout = {
    title: {
      text: '<b>Audiograma Clínico (Escala Invertida dB HL)</b>',
      font: { color: '#f1f5f9', size: 13 }
    },
    autosize: true,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'rgba(17, 24, 39, 0.6)',
    font: { color: '#94a3b8', family: 'Inter, sans-serif' },
    xaxis: {
      title: 'Frecuencia (Hz)',
      type: 'log',
      tickvals: [250, 500, 1000, 2000, 4000, 8000],
      ticktext: ['250', '500', '1k', '2k', '4k', '8k'],
      gridcolor: 'rgba(255, 255, 255, 0.08)',
    },
    yaxis: {
      title: 'Nivel de Audición (dB HL)',
      autorange: 'reversed', // Invertido: 0 dB arriba, 100 dB abajo
      range: [-10, 100],
      dtick: 20,
      gridcolor: 'rgba(255, 255, 255, 0.08)',
    },
    margin: { l: 45, r: 20, t: 40, b: 40 },
    showlegend: false
  }

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-xl space-y-6">
      
      {/* Encabezado del Módulo */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            <span>Carga de Audiogramas (FilePond + OHC)</span>
          </h2>
          <p className="text-xs text-slate-400">
            Cargá audiometrías de pacientes reales para sintetizar perfiles cocleares personalizados
          </p>
        </div>

        {/* Selector de Pestaña */}
        <div className="flex space-x-1.5 bg-dark-800 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('interactive')}
            className={`px-3 py-1.5 text-xs rounded-lg transition ${
              activeTab === 'interactive'
                ? 'bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Curva Interactiva
          </button>
          <button
            onClick={() => setActiveTab('filepond')}
            className={`px-3 py-1.5 text-xs rounded-lg transition ${
              activeTab === 'filepond'
                ? 'bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Subir Archivo (FilePond)
          </button>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-200 text-xs">
          {error}
        </div>
      )}

      {/* Input de Nombre del Paciente */}
      <div>
        <label className="text-xs font-medium text-slate-300 block mb-1">
          Identificador o Nombre del Paciente / Caso:
        </label>
        <input
          type="text"
          value={patientName}
          onChange={(e) => setPatientName(e.target.value)}
          placeholder="Ej: Juan Perez"
          className="w-full sm:w-72 bg-dark-800 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-rose-500/50"
        />
      </div>

      {/* Pestaña 1: Curva Interactiva */}
      {activeTab === 'interactive' && (
        <div className="space-y-5">
          
          {/* Presets clínicos */}
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Casos Clínicos Frecuentes:
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {Object.keys(presets).map(key => (
                <button
                  key={key}
                  type="button"
                  onClick={() => applyPreset(key)}
                  className="px-2.5 py-2 rounded-lg bg-dark-800 border border-slate-800 hover:border-rose-500/40 text-xs text-slate-300 hover:text-rose-300 transition text-left"
                >
                  <div className="font-semibold truncate">{presets[key].name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Gráfico y Sliders lado a lado */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            
            {/* Gráfico audiométrico (7 columnas) */}
            <div className="lg:col-span-7 h-72">
              <Plot
                data={audiogramPlotData}
                layout={audiogramPlotLayout}
                config={{ responsive: true, displayModeBar: false }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>

            {/* Sliders de dB por frecuencia (5 columnas) */}
            <div className="lg:col-span-5 space-y-3 bg-dark-800/60 p-4 rounded-xl border border-slate-800">
              <div className="text-xs font-semibold text-slate-300 mb-2">
                Ajuste por Frecuencia (dB HL):
              </div>
              {points.map(p => (
                <div key={p.frequency} className="flex items-center space-x-3 text-xs">
                  <span className="w-12 font-mono text-slate-400">{p.frequency >= 1000 ? `${p.frequency/1000}k` : p.frequency} Hz</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={p.hearing_loss_db}
                    onChange={(e) => handlePointChange(p.frequency, e.target.value)}
                    className="flex-1 accent-rose-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                  />
                  <span className="w-10 text-right font-mono text-rose-400 font-bold">{p.hearing_loss_db} dB</span>
                </div>
              ))}
            </div>

          </div>

          <button
            type="button"
            onClick={handleProcessManual}
            disabled={isProcessing}
            className="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-400 hover:to-pink-500 text-white shadow-lg shadow-rose-500/20 active:scale-[0.99] transition flex items-center justify-center space-x-2"
          >
            {isProcessing ? 'Sintetizando perfil coclear...' : 'Analizar Audiograma y Crear Perfil Coclear'}
          </button>

        </div>
      )}

      {/* Pestaña 2: Subida de archivo con FilePond */}
      {activeTab === 'filepond' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-400">
              Subí un archivo CSV con las columnas <code className="text-rose-300">frecuencia, perdida_db</code>
            </span>
            <button
              onClick={downloadTemplate}
              className="text-xs text-cyan-400 hover:underline flex items-center space-x-1"
            >
              <span>Descargar plantilla CSV</span>
            </button>
          </div>

          <FilePond
            files={files}
            onupdatefiles={setFiles}
            allowMultiple={false}
            maxFiles={1}
            name="audiogramFile"
            labelIdle='Arrastrá tu audiograma CSV o <span class="filepond--label-action">Explorá tu equipo</span>'
          />

          <button
            type="button"
            onClick={handleProcessFile}
            disabled={files.length === 0 || isProcessing}
            className={`w-full py-3 px-4 rounded-xl font-semibold text-sm transition ${
              files.length > 0 && !isProcessing
                ? 'bg-gradient-to-r from-rose-500 to-pink-600 text-white hover:from-rose-400 hover:to-pink-500 shadow-lg shadow-rose-500/20'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            {isProcessing ? 'Procesando archivo...' : 'Procesar Archivo Subido'}
          </button>
        </div>
      )}

      {/* Tarjeta de Resultado del Análisis */}
      {analysisResult && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-rose-950/40 to-dark-800 border border-rose-500/30 space-y-3 animate-fadeIn">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-rose-500/20 pb-3">
            <div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-rose-300">
                Diagnóstico Audiológico Generado
              </span>
              <div className="text-sm font-bold text-white mt-0.5">
                {analysisResult.clinical_classification}
              </div>
            </div>
            <div className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/30">
              Perfil: {analysisResult.matched_profile}
            </div>
          </div>

          <p className="text-xs text-slate-300">
            {analysisResult.notes}
          </p>

          <button
            type="button"
            onClick={() => onSelectProfile(analysisResult.matched_profile)}
            className="w-full py-2.5 px-3 rounded-lg bg-cyan-500/20 border border-cyan-500/40 hover:bg-cyan-500/30 text-cyan-300 font-semibold text-xs flex items-center justify-center space-x-2 transition"
          >
            <span>👉 Vincular "{analysisResult.matched_profile}" al Panel de Simulación</span>
          </button>
        </div>
      )}

    </div>
  )
}
