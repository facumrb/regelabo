import { useState } from 'react'
import { FilePond, type FilePondProps } from 'react-filepond'
import type { FilePondFile } from 'filepond'
import 'filepond/dist/filepond.min.css'
import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { api } from '../services/api'
import { mensajeDeError } from '../services/auth'
import CurvasPerfil from './CurvasPerfil'
import { avisoError, botonPrimario, entrada, etiqueta, panel } from './estilos'
import { layoutBase, titulo, useColoresGrafico } from './graficos'
import { Deslizador, Encabezado, Pestanas } from './ui'
import type { PerfilAuditivo, PuntoAudiograma, ResultadoAudiograma } from '../services/tiposSimulacion'

interface Props {
  onSelectProfile: (perfil: PerfilAuditivo) => void
}

export default function AudiogramManager({ onSelectProfile }: Props) {
  const [activeTab, setActiveTab] = useState<'interactive' | 'filepond'>('interactive')
  const [patientName, setPatientName] = useState('Mi perfil')
  const [files, setFiles] = useState<FilePondFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<ResultadoAudiograma | null>(null)
  const [error, setError] = useState<string | null>(null)
  const c = useColoresGrafico()

  // Puntos audiométricos por defecto (Audición típica)
  const [points, setPoints] = useState<PuntoAudiograma[]>([
    { frequency: 250, hearing_loss_db: 15 },
    { frequency: 500, hearing_loss_db: 15 },
    { frequency: 1000, hearing_loss_db: 20 },
    { frequency: 2000, hearing_loss_db: 35 },
    { frequency: 4000, hearing_loss_db: 50 },
    { frequency: 8000, hearing_loss_db: 60 },
  ])

  // Presets clínicos para carga rápida
  const presets: Record<string, { name: string; data: PuntoAudiograma[] }> = {
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

  const applyPreset = (key: string) => {
    setPoints(presets[key].data)
    setPatientName(presets[key].name)
    setAnalysisResult(null)
  }

  const handlePointChange = (freq: number, newDb: number) => {
    setPoints(prev =>
      prev.map(p => (p.frequency === freq ? { ...p, hearing_loss_db: newDb } : p))
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
    } catch (err) {
      setError(mensajeDeError(err))
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
      // FilePond tipa el archivo como ActualFileObject; al subir desde el navegador siempre es un File
      const fileItem = files[0].file as File
      const res = await api.uploadAudiogram(fileItem, patientName)
      setAnalysisResult(res)
      setPoints(res.points)
    } catch (err) {
      setError(mensajeDeError(err))
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

  // Audiograma con la escala invertida: 0 dB HL arriba
  const audiogramPlotData: Data[] = [
    {
      x: points.map(p => p.frequency),
      y: points.map(p => p.hearing_loss_db),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Umbral Auditivo (dB HL)',
      line: { color: c.acento, width: 2.5 },
      marker: { color: c.acento, size: 9, symbol: 'circle-open', line: { width: 2.5 } },
      hovertemplate: '%{x} Hz: %{y} dB HL<extra></extra>',
    }
  ]

  const audiogramPlotLayout = layoutBase(c, {
    title: titulo(c, 'Audiograma Clínico (Escala Invertida dB HL)'),
    xaxis: {
      title: { text: 'Frecuencia (Hz)' },
      type: 'log',
      tickvals: [250, 500, 1000, 2000, 4000, 8000],
      ticktext: ['250', '500', '1k', '2k', '4k', '8k'],
    },
    yaxis: { title: { text: 'Nivel de Audición (dB HL)' }, range: [100, -10], dtick: 20 }, // invertido: 0 dB arriba
    margin: { l: 50, r: 16, t: 40, b: 45 },
    showlegend: false,
  })

  return (
    <div className="space-y-6">
      <Encabezado titulo="Cargar audiograma"
        bajada="Cargá audiometrías de pacientes reales para sintetizar perfiles cocleares personalizados" />

      {error && <div role="alert" className={`px-4 py-3 rounded-xl border text-sm ${avisoError}`}>{error}</div>}

      <div className={`${panel} p-5 md:p-7 space-y-6`}>
        {/* Nombre del perfil (decisión 008: sin datos personales) */}
        <div className="sm:max-w-sm">
          <label htmlFor="nombre-perfil" className="block text-sm text-tenue mb-1.5">Nombre del perfil</label>
          <input id="nombre-perfil" type="text" value={patientName} onChange={(e) => setPatientName(e.target.value)}
            placeholder="Ej: Trauma 4 kHz – caso 12" aria-describedby="nombre-perfil-ayuda" className={entrada} />
          <p id="nombre-perfil-ayuda" className="text-sm text-tenue mt-1">No uses nombres reales de pacientes.</p>
        </div>

        <Pestanas nombre="Forma de carga" valor={activeTab} onCambio={setActiveTab}
          opciones={[['interactive', 'Curva Interactiva'], ['filepond', 'Subir Archivo (FilePond)']]} />

        {activeTab === 'interactive' && (
          <div className="space-y-6">
            <div className="space-y-2">
              <span className={etiqueta}>Casos Clínicos Frecuentes:</span>
              <div className="flex flex-wrap gap-2">
                {Object.keys(presets).map(key => (
                  <button key={key} type="button" onClick={() => applyPreset(key)}
                    className="min-h-[40px] px-3.5 rounded-full border border-linea text-sm text-tinta hover:border-acento transition">
                    {presets[key].name}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6 lg:gap-10 items-start">
              <div className="h-72 lg:h-80">
                <Plot data={audiogramPlotData} layout={audiogramPlotLayout}
                  config={{ responsive: true, displayModeBar: false }} style={{ width: '100%', height: '100%' }} />
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-1 gap-x-6 gap-y-3">
                <span className={`${etiqueta} sm:col-span-2 lg:col-span-1`}>Ajuste por Frecuencia (dB HL):</span>
                {points.map(p => (
                  <Deslizador key={p.frequency} id={`umbral-${p.frequency}`} unidad="dB HL" min={0} max={100} paso={5}
                    etiqueta={`${p.frequency >= 1000 ? `${p.frequency / 1000}k` : p.frequency} Hz`}
                    valor={p.hearing_loss_db} onCambio={(v) => handlePointChange(p.frequency, v)} />
                ))}
              </div>
            </div>

            <button type="button" onClick={handleProcessManual} disabled={isProcessing}
              className={`${botonPrimario} w-full min-h-[52px] text-base`}>
              {isProcessing ? 'Generando perfil...' : 'Analizar audiograma y generar perfil'}
            </button>
          </div>
        )}

        {activeTab === 'filepond' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-sm text-tenue">
              <span>Subí un archivo CSV con las columnas <code className="font-mono text-tinta">frecuencia, perdida_db</code></span>
              <button onClick={downloadTemplate} className="self-start min-h-[44px] text-acento hover:underline">
                Descargar plantilla CSV
              </button>
            </div>

            <FilePond
              // Los tipos de react-filepond esperan archivos de origen, pero acepta los ítems de onupdatefiles (uso documentado)
              files={files as unknown as FilePondProps['files']}
              onupdatefiles={setFiles}
              allowMultiple={false}
              maxFiles={1}
              name="audiogramFile"
              labelIdle='Arrastrá tu audiograma CSV o <span class="filepond--label-action">Explorá tu equipo</span>'
            />

            <button type="button" onClick={handleProcessFile} disabled={files.length === 0 || isProcessing}
              className={`${botonPrimario} w-full min-h-[52px] text-base`}>
              {isProcessing ? 'Procesando archivo...' : 'Procesar Archivo Subido'}
            </button>
          </div>
        )}
      </div>

      {analysisResult && (
        <section aria-label="Perfil generado" className={`${panel} border-acento p-5 md:p-7 space-y-4`}>
          <div>
            <span className={etiqueta}>Clasificación del audiograma</span>
            <h2 className="mt-1 text-lg font-semibold text-tinta">{analysisResult.clinical_classification}</h2>
            <p className="text-sm text-tenue">{analysisResult.perfil.etiqueta}</p>
          </div>
          <p className="text-sm text-tinta">{analysisResult.notes}</p>
          <CurvasPerfil perfil={analysisResult.perfil} alto={220} conAviso />
          <button type="button" onClick={() => onSelectProfile(analysisResult.perfil)}
            className={`${botonPrimario} w-full`}>
            Usar este perfil y simular →
          </button>
        </section>
      )}
    </div>
  )
}
