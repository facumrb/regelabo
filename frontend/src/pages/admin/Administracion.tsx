import { useSearchParams } from 'react-router-dom'
import { Encabezado, Pestanas, Volver } from '../../components/ui'
import ComentariosAdmin from './ComentariosAdmin'
import UsuariosAdmin from './UsuariosAdmin'
import ColaAdmin from './ColaAdmin'

type Seccion = 'comentarios' | 'usuarios' | 'cola'
const SECCIONES: Seccion[] = ['comentarios', 'usuarios', 'cola']

/** Panel de administración (decisión 028). La pestaña va en la dirección (`?seccion=usuarios`). */
export default function Administracion() {
  const [parametros, setParametros] = useSearchParams()
  const pedida = parametros.get('seccion') as Seccion
  const seccion: Seccion = SECCIONES.includes(pedida) ? pedida : 'comentarios'

  return (
    <div className="space-y-6">
      <Volver a="/" texto="Volver" />
      <Encabezado titulo="Administración" bajada="Solo la ven los admin." />
      <Pestanas nombre="Secciones del panel" valor={seccion}
        opciones={[['comentarios', 'Comentarios'], ['usuarios', 'Usuarios'], ['cola', 'Cola']]}
        onCambio={(v) => setParametros(v === 'comentarios' ? {} : { seccion: v }, { replace: true })} />
      {seccion === 'comentarios' && <ComentariosAdmin />}
      {seccion === 'usuarios' && <UsuariosAdmin />}
      {seccion === 'cola' && <ColaAdmin />}
    </div>
  )
}
