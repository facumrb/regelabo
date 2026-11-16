import { useSearchParams } from 'react-router-dom'
import { Encabezado, Pestanas, Volver } from '../../components/ui'
import ComentariosAdmin from './ComentariosAdmin'
import UsuariosAdmin from './UsuariosAdmin'

type Seccion = 'comentarios' | 'usuarios'

/** Panel de administración (decisión 028). La pestaña va en la dirección (`?seccion=usuarios`). */
export default function Administracion() {
  const [parametros, setParametros] = useSearchParams()
  const seccion: Seccion = parametros.get('seccion') === 'usuarios' ? 'usuarios' : 'comentarios'

  return (
    <div className="space-y-6">
      <Volver a="/" texto="Volver" />
      <Encabezado titulo="Administración" bajada="Solo la ven los admin." />
      <Pestanas nombre="Secciones del panel" valor={seccion}
        opciones={[['comentarios', 'Comentarios'], ['usuarios', 'Usuarios']]}
        onCambio={(v) => setParametros(v === 'comentarios' ? {} : { seccion: v }, { replace: true })} />
      {seccion === 'comentarios' ? <ComentariosAdmin /> : <UsuariosAdmin />}
    </div>
  )
}
