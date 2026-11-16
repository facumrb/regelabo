import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Aviso, Centrada } from '../../components/ui'
import { useSesion } from '../../context/SesionContext'
import { authApi, mensajeDeError } from '../../services/auth'

/** Destino del enlace del mail de verificación (RN15): /verificar?token=... */
export default function VerificarEmail() {
  const [parametros] = useSearchParams()
  const { usuario, verificarSesion } = useSesion()
  const [estado, setEstado] = useState<'verificando' | 'ok' | string>('verificando')
  const enviado = useRef(false) // StrictMode corre el efecto dos veces y el enlace sirve una sola vez

  useEffect(() => {
    if (enviado.current) return
    enviado.current = true
    authApi.verificarEmail(parametros.get('token') ?? '')
      .then(() => {
        setEstado('ok')
        verificarSesion() // si hay sesión abierta, que deje de mostrar el aviso
      })
      .catch((e) => setEstado(mensajeDeError(e)))
  }, [parametros, verificarSesion])

  return (
    <Centrada titulo="Confirmar email">
      {estado === 'verificando' && <p className="text-tenue">Confirmando…</p>}
      {estado === 'ok' && <Aviso tipo="ok">Listo: tu email quedó confirmado y ya podés pedir simulaciones.</Aviso>}
      {estado !== 'verificando' && estado !== 'ok' && (
        <Aviso tipo="error">{estado} Podés pedir otro mail desde el aviso de arriba, con la sesión iniciada.</Aviso>
      )}
      <Link to={usuario ? '/' : '/login'} className="block text-sm text-center text-acento font-medium hover:underline">
        {usuario ? 'Ir al inicio' : 'Iniciar sesión'}
      </Link>
    </Centrada>
  )
}
