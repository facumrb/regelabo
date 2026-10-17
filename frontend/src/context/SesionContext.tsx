import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { authApi, type DatosRegistro, type Usuario } from '../services/auth'

interface ValorSesion {
  usuario: Usuario | null
  /** true mientras se averigua si hay una sesión vigente (al cargar la página) */
  cargando: boolean
  iniciarSesion: (email: string, password: string) => Promise<void>
  registrarse: (datos: DatosRegistro) => Promise<void>
  cerrarSesion: () => Promise<void>
  /** Pide GET /auth/yo y actualiza el estado: sirve para recuperar o descartar la sesión */
  verificarSesion: () => Promise<void>
}

const SesionContext = createContext<ValorSesion | null>(null)

export function SesionProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [cargando, setCargando] = useState(true)
  const yaVerificada = useRef(false) // StrictMode ejecuta los efectos dos veces en desarrollo

  const verificarSesion = useCallback(async () => {
    try {
      setUsuario(await authApi.yo())
    } catch {
      setUsuario(null) // 401: no hay sesión (o venció)
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    if (yaVerificada.current) return
    yaVerificada.current = true
    verificarSesion()
  }, [verificarSesion])

  const valor = useMemo<ValorSesion>(
    () => ({
      usuario,
      cargando,
      verificarSesion,
      iniciarSesion: async (email, password) => setUsuario(await authApi.login(email, password)),
      registrarse: async (datos) => {
        await authApi.registro(datos) // no inicia sesión: el backend solo crea la cuenta
      },
      cerrarSesion: async () => {
        try {
          await authApi.logout()
        } finally {
          setUsuario(null) // si el pedido falló, la próxima carga recupera el estado real con /yo
        }
      },
    }),
    [usuario, cargando, verificarSesion],
  )

  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
}

export function useSesion(): ValorSesion {
  const valor = useContext(SesionContext)
  if (!valor) throw new Error('useSesion se usa dentro de <SesionProvider>')
  return valor
}
