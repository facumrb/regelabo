import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useSesion } from '../context/SesionContext'

/** Envuelve las páginas que necesitan sesión: sin sesión, manda al login. */
export default function RequiereSesion({ children }: { children: ReactNode }) {
  const { usuario, cargando } = useSesion()
  if (cargando) return null
  if (!usuario) return <Navigate to="/login" replace />
  return <>{children}</>
}
