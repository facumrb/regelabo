import { useNavigate } from 'react-router-dom'
import { Tarjeta } from '../../components/ui'
import { casosApi } from '../../services/casos'
import FormularioCaso from './FormularioCaso'

export default function NuevoCaso() {
  const navigate = useNavigate()
  return (
    <Tarjeta titulo="Nuevo caso">
      <FormularioCaso
        alGuardar={async (datos) => {
          const caso = await casosApi.crear(datos)
          navigate(`/casos/${caso.id}`, { replace: true })
        }}
        alCancelar={() => navigate('/casos')}
      />
    </Tarjeta>
  )
}
