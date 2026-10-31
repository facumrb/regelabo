import CurvasPerfil from './CurvasPerfil'
import { panel } from './estilos'
import type { PerfilAuditivo } from '../services/tiposSimulacion'

/** Aviso final (Q21): con qué perfil se simuló, la curva pedida y la simulada, y el recorte si lo hubo. */
export default function PerfilSimulado({ perfil }: { perfil: PerfilAuditivo }) {
  return (
    <div className={`${panel} p-5 space-y-3`}>
      <div>
        <h3 className="font-semibold text-tinta">Perfil simulado</h3>
        <p className="text-sm text-tenue">{perfil.etiqueta}</p>
      </div>
      <CurvasPerfil perfil={perfil} alto={220} conAviso />
    </div>
  )
}
