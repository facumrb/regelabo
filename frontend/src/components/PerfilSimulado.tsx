import CurvasPerfil from './CurvasPerfil'
import type { PerfilAuditivo } from '../services/tiposSimulacion'

/** Aviso final (Q21): con qué perfil se simuló, la curva pedida y la simulada, y el recorte si lo hubo. */
export default function PerfilSimulado({ perfil }: { perfil: PerfilAuditivo }) {
  return (
    <div className="glass-panel rounded-2xl p-5 space-y-3">
      <div>
        <h3 className="text-sm font-semibold text-white">Perfil simulado</h3>
        <p className="text-xs text-slate-400">{perfil.etiqueta}</p>
      </div>
      <CurvasPerfil perfil={perfil} alto={220} conAviso />
    </div>
  )
}
