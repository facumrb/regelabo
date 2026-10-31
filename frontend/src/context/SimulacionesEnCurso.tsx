import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useSesion } from './SesionContext'
import { enCurso as estaEnCurso, INTERVALO_CONSULTA_MS, simulacionesApi } from '../services/simulaciones'
import type { Simulacion } from '../services/tiposSimulacion'

interface ValorEnCurso {
  /** En cola o ejecutando, pedidas desde esta pestaña o recuperadas al cargar */
  enCurso: Simulacion[]
  /** Terminadas (completadas o con error) cuyo detalle todavía no se abrió */
  terminadas: Simulacion[]
  /** La que se espera desde el formulario de Simular: al terminar, Simular pasa a su detalle */
  esperada: string | null
  esperar: (simulacion: Simulacion) => void
  dejarDeEsperar: () => void
  marcarVista: (id: string) => void
  marcarTodasVistas: () => void
}

const SimulacionesEnCursoContext = createContext<ValorEnCurso | null>(null)

/**
 * Sigue las simulaciones en curso desde cualquier pantalla (decisión 024): así la barra puede avisar que
 * terminaron sin sacar a nadie de donde está.
 */
export function SimulacionesEnCursoProvider({ children }: { children: ReactNode }) {
  const { usuario } = useSesion()
  const [enCurso, setEnCurso] = useState<Simulacion[]>([])
  const [terminadas, setTerminadas] = useState<Simulacion[]>([])
  const [esperada, setEsperada] = useState<string | null>(null)

  // Al iniciar sesión (o recargar) se recuperan las que siguen en curso; al cerrarla se olvida todo
  useEffect(() => {
    setEnCurso([])
    setTerminadas([])
    setEsperada(null)
    if (!usuario) return
    let activo = true
    // shortcut: busca solo entre las últimas 20; alcanza mientras el cupo en curso (RN5a) sea de 1 a 3
    simulacionesApi.listar(null, null, 20)
      .then((pagina) => { if (activo) setEnCurso(pagina.simulaciones.filter((s) => estaEnCurso(s.estado))) })
      .catch(() => {})
    return () => { activo = false }
  }, [usuario])

  // Mientras haya alguna en curso, se consulta su estado cada pocos segundos
  useEffect(() => {
    if (enCurso.length === 0) return
    let activo = true
    const temporizador = setTimeout(async () => {
      const actuales = await Promise.all(enCurso.map((s) => simulacionesApi.ver(s.id).catch(() => s)))
      if (!activo) return
      const porId = new Map(actuales.map((s) => [s.id, s]))
      const listas = actuales.filter((s) => !estaEnCurso(s.estado))
      // Con actualización funcional: una pedida mientras se consultaba no se pierde
      setEnCurso((previas) => previas.map((s) => porId.get(s.id) ?? s).filter((s) => estaEnCurso(s.estado)))
      setTerminadas((previas) => [...previas.filter((s) => !porId.has(s.id)), ...listas])
    }, INTERVALO_CONSULTA_MS)
    return () => {
      activo = false
      clearTimeout(temporizador)
    }
  }, [enCurso])

  const valor = useMemo<ValorEnCurso>(() => ({
    enCurso,
    terminadas,
    esperada,
    esperar: (simulacion) => {
      setEnCurso((previas) => [...previas.filter((s) => s.id !== simulacion.id), simulacion])
      setEsperada(simulacion.id)
    },
    dejarDeEsperar: () => setEsperada(null),
    marcarVista: (id) => setTerminadas((previas) => previas.filter((s) => s.id !== id)),
    marcarTodasVistas: () => setTerminadas([]),
  }), [enCurso, terminadas, esperada])

  return <SimulacionesEnCursoContext.Provider value={valor}>{children}</SimulacionesEnCursoContext.Provider>
}

export function useSimulacionesEnCurso(): ValorEnCurso {
  const valor = useContext(SimulacionesEnCursoContext)
  if (!valor) throw new Error('useSimulacionesEnCurso se usa dentro de <SimulacionesEnCursoProvider>')
  return valor
}
