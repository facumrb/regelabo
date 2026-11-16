import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useSesion } from '../context/SesionContext'

/** Envuelve las páginas que necesitan sesión: sin sesión, manda al login; con `admin`, si no lo es, al inicio. */
export default function RequiereSesion({ children, admin }: { children: ReactNode; admin?: boolean }) {
  const { usuario, cargando } = useSesion()
  if (cargando) return null
  if (!usuario) return <Navigate to="/login" replace />
  if (admin && !usuario.es_admin) return <Navigate to="/" replace />
  return <>{children}</>
}
