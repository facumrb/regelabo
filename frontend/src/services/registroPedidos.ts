/**
 * Registro de los pedidos a /api/auth/* y /api/casos* para el Panel de pruebas. Solo existe en desarrollo.
 * Las contraseñas se ocultan antes de guardar nada.
 */
import type { InternalAxiosRequestConfig } from 'axios'
import { apiClient } from './api'

export interface Pedido {
  id: number
  hora: string
  metodo: string
  url: string
  envio?: unknown
  estado?: number // undefined = el servidor no respondió
  respuesta?: unknown
  ms?: number
}

let pedidos: Pedido[] = []
let siguienteId = 1
const oyentes = new Set<() => void>()
const enCurso = new WeakMap<InternalAxiosRequestConfig, { pedido: Pedido; inicio: number }>()

const notificar = () => oyentes.forEach((oyente) => oyente())

export const suscribir = (oyente: () => void) => {
  oyentes.add(oyente)
  return () => {
    oyentes.delete(oyente)
  }
}
export const obtenerPedidos = () => pedidos
export const limpiarPedidos = () => {
  pedidos = []
  notificar()
}

const CAMPOS_SECRETOS = ['password', 'actual', 'nueva']

function ocultarContrasenas(datos: unknown): unknown {
  if (datos && typeof datos === 'object') {
    return Object.fromEntries(
      Object.entries(datos).map(([clave, valor]) => [clave, CAMPOS_SECRETOS.includes(clave) ? '••••••••' : valor]),
    )
  }
  return datos
}

function actualizar(config: InternalAxiosRequestConfig | undefined, cambios: Partial<Pedido>) {
  const registro = config && enCurso.get(config)
  if (!registro) return
  pedidos = pedidos.map((p) =>
    p.id === registro.pedido.id ? { ...p, ...cambios, ms: Math.round(performance.now() - registro.inicio) } : p,
  )
  notificar()
}

if (import.meta.env.DEV) {
  apiClient.interceptors.request.use((config) => {
    if (config.url?.startsWith('/auth') || config.url?.startsWith('/casos')) {
      const pedido: Pedido = {
        id: siguienteId++,
        hora: new Date().toLocaleTimeString('es-AR'),
        metodo: (config.method ?? 'get').toUpperCase(),
        url: `${config.baseURL ?? ''}${config.url}`,
        envio: ocultarContrasenas(config.data),
      }
      enCurso.set(config, { pedido, inicio: performance.now() })
      pedidos = [pedido, ...pedidos]
      notificar()
    }
    return config
  })

  apiClient.interceptors.response.use(
    (respuesta) => {
      actualizar(respuesta.config, { estado: respuesta.status, respuesta: respuesta.data })
      return respuesta
    },
    (error) => {
      actualizar(error.config, { estado: error.response?.status, respuesta: error.response?.data })
      return Promise.reject(error)
    },
  )
}
