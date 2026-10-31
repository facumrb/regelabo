import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { PerfilAuditivo } from '../services/tiposSimulacion'
import { detalle, tituloDelTipo } from './perfiles'

// Una consulta por perfil mientras dure la página: en el historial se repiten mucho
const cache = new Map<string, Promise<PerfilAuditivo | null>>()

function perfilDe(nombre: string): Promise<PerfilAuditivo | null> {
  if (!cache.has(nombre)) {
    // Los personalizados viejos no guardaron su audiograma (404): se muestra el nombre del modelo
    cache.set(nombre, api.getProfile(nombre).catch(() => null))
  }
  return cache.get(nombre)!
}

/**
 * El perfil con su etiqueta clínica en lugar del nombre del modelo de Verhulst (decisión 026).
 * `parte`: la etiqueta completa, solo el tipo de caso o solo el perfil dentro del tipo.
 */
export default function EtiquetaPerfil({ nombre, parte = 'completa' }: {
  nombre: string; parte?: 'completa' | 'tipo' | 'perfil'
}) {
  const [perfil, setPerfil] = useState<PerfilAuditivo | null>(null)
  useEffect(() => {
    let activo = true
    perfilDe(nombre).then((p) => { if (activo) setPerfil(p) })
    return () => { activo = false }
  }, [nombre])
  if (!perfil) return <>{parte === 'tipo' ? '—' : nombre}</>
  return <>{parte === 'tipo' ? tituloDelTipo(perfil) : parte === 'perfil' ? detalle(perfil) : perfil.etiqueta}</>
}
