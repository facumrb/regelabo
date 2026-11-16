import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import CurvasPerfil from '../../components/CurvasPerfil'
import { Aviso } from '../../components/ui'
import { botonPrimario, botonSecundario, etiqueta, panel, vacio } from '../../components/estilos'
import { api } from '../../services/api'
import { mensajeDeError } from '../../services/auth'
import { casosApi } from '../../services/casos'
import { formatearFecha } from '../../services/simulaciones'
import type { AudiogramaGuardado, PerfilAuditivo } from '../../services/tiposSimulacion'
import type { EstadoNuevaSimulacion } from '../../App'

const GRADO = { normal: 'Audición normal', leve: 'Hipoacusia leve', moderada: 'Hipoacusia moderada',
  severa: 'Hipoacusia severa' } as const
const PATRON = { plano: 'patrón plano', caida_en_agudos: 'caída en agudos' } as const

/** Un audiograma con su curva y "Simular con este", que abre Simular con el caso y el perfil elegidos. */
function Audiograma({ audiograma, casoId }: { audiograma: AudiogramaGuardado; casoId: string }) {
  const navigate = useNavigate()
  const [perfil, setPerfil] = useState<PerfilAuditivo | null>(null)
  useEffect(() => {
    let activo = true
    api.getProfile(audiograma.perfil).then((p) => { if (activo) setPerfil(p) }).catch(() => {})
    return () => { activo = false }
  }, [audiograma.perfil])

  return (
    <li className={`${panel} p-4 md:p-5 space-y-3`}>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="font-medium text-tinta">{GRADO[audiograma.gravedad]}, {PATRON[audiograma.patron]}</span>
        <span className="text-sm text-tenue">PTA {audiograma.pta_db} dB HL</span>
        <span className="ml-auto text-sm text-tenue">
          {formatearFecha(audiograma.creado_en)} · {audiograma.origen === 'archivo' ? 'desde archivo' : 'cargado a mano'}
        </span>
      </div>
      {perfil && <CurvasPerfil perfil={perfil} alto={160} />}
      <button type="button" disabled={!perfil} className={botonPrimario}
        onClick={() => navigate('/simular', { state: { casoId, perfil } satisfies EstadoNuevaSimulacion })}>
        Simular con este
      </button>
    </li>
  )
}

/** Audiogramas guardados en el caso, del más nuevo al más viejo (decisión 032). */
export default function AudiogramasDelCaso({ casoId }: { casoId: string }) {
  const [audiogramas, setAudiogramas] = useState<AudiogramaGuardado[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    casosApi.audiogramas(casoId).then(setAudiogramas).catch((e) => setError(mensajeDeError(e)))
  }, [casoId])

  return (
    <section aria-labelledby="titulo-audiogramas" className="max-w-3xl mx-auto space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 id="titulo-audiogramas" className={etiqueta}>Audiogramas</h2>
        <Link to={`/simular/audiograma?caso=${casoId}`} className={botonSecundario}>Cargar audiograma</Link>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {audiogramas?.length === 0 && (
        <p className={vacio}>Este caso todavía no tiene audiogramas. Cargá uno para simular con su forma.</p>
      )}
      {audiogramas && audiogramas.length > 0 && (
        <ul className="space-y-3">
          {audiogramas.map((a) => <Audiograma key={a.id} audiograma={a} casoId={casoId} />)}
        </ul>
      )}
    </section>
  )
}
