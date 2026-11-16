import { useState } from 'react'
import { avisoAtencion } from './estilos'
import { useSesion } from '../context/SesionContext'
import { authApi, mensajeDeError } from '../services/auth'

/** RN15: mientras el email no esté confirmado, recuerda que hace falta para simular. */
export default function AvisoEmailSinVerificar() {
  const { usuario } = useSesion()
  const [estado, setEstado] = useState<'inicial' | 'enviando' | 'enviado' | string>('inicial')

  if (!usuario || usuario.email_verificado) return null

  const reenviar = async () => {
    setEstado('enviando')
    try {
      await authApi.reenviarVerificacion()
      setEstado('enviado')
    } catch (e) {
      setEstado(mensajeDeError(e))
    }
  }

  return (
    <div role="status" className={`mb-6 px-4 py-3 rounded-lg border text-sm ${avisoAtencion}`}>
      Confirmá tu email para poder pedir simulaciones: te mandamos un enlace a <strong>{usuario.email}</strong>.{' '}
      {estado === 'enviado' ? (
        'Te mandamos uno nuevo (revisá también el spam).'
      ) : estado === 'inicial' || estado === 'enviando' ? (
        <button type="button" onClick={reenviar} disabled={estado === 'enviando'}
          className="font-medium underline hover:no-underline">
          {estado === 'enviando' ? 'Enviando…' : 'Reenviar el mail'}
        </button>
      ) : (
        estado
      )}
    </div>
  )
}
