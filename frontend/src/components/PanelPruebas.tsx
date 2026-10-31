import { useState, useSyncExternalStore } from 'react'
import { useSesion } from '../context/SesionContext'
import { limpiarPedidos, obtenerPedidos, suscribir, type Pedido } from '../services/registroPedidos'
import { botonSecundario } from './estilos'

const SIGNIFICADO: Record<number, string> = {
  200: 'Todo bien',
  201: 'Creado',
  204: 'Todo bien, sin contenido',
  400: 'Se incumplió una regla de negocio',
  401: 'Sin sesión, o email/contraseña incorrectos',
  403: 'Sin permiso',
  409: 'Conflicto (por ejemplo, email ya registrado)',
  422: 'Datos mal formados (formato)',
  429: 'Demasiados intentos o pedidos',
}

function Estado({ pedido }: { pedido: Pedido }) {
  const { estado, ms } = pedido
  if (estado === undefined) {
    return ms === undefined
      ? <span className="text-tenue">…</span>
      : <span className="px-1.5 rounded bg-rose-500/20 text-rose-300">sin respuesta</span>
  }
  const color = estado < 300 ? 'bg-emerald-500/20 text-emerald-300'
    : estado < 500 ? 'bg-amber-500/20 text-amber-300' : 'bg-rose-500/20 text-rose-300'
  return (
    <span className={`px-1.5 rounded font-semibold ${color}`} title={SIGNIFICADO[estado] ?? ''}>
      {estado}
    </span>
  )
}

function Bloque({ titulo, valor }: { titulo: string; valor: unknown }) {
  return (
    <div>
      <div className="text-tenue mb-1">{titulo}</div>
      <pre className="bg-fondo rounded p-2 overflow-x-auto text-tinta">
        {valor === undefined || valor === '' ? '—' : JSON.stringify(valor, null, 2)}
      </pre>
    </div>
  )
}

function Panel() {
  const { usuario, verificarSesion } = useSesion()
  const pedidos = useSyncExternalStore(suscribir, obtenerPedidos)
  const [abierto, setAbierto] = useState(false)

  return (
    <>
      <div className={abierto ? 'h-[45vh]' : 'h-10'} /> {/* para que el panel no tape el pie de página */}
      <div className={`fixed inset-x-0 z-50 bg-panel border-t border-linea text-xs text-tinta ${usuario ? 'bottom-[calc(56px+env(safe-area-inset-bottom))] md:bottom-0' : 'bottom-0'}`}>
        <button onClick={() => setAbierto(!abierto)} className="w-full h-10 px-4 flex items-center justify-between">
          <span className="font-semibold">Panel de pruebas (solo desarrollo) · {pedidos.length} pedidos</span>
          <span>
            Sesión: {usuario ? `${usuario.email} (${usuario.tipo_perfil}${usuario.es_admin ? ', admin' : ''})` : 'sin sesión'}
            {' '}{abierto ? '▼' : '▲'}
          </span>
        </button>

        {abierto && (
          <div className="h-[calc(45vh-2.5rem)] overflow-y-auto px-4 pb-4 space-y-3">
            <div className="flex items-center space-x-2">
              <button onClick={verificarSesion} className={botonSecundario}>Probar sesión (GET /auth/yo)</button>
              <button onClick={limpiarPedidos} className={botonSecundario}>Limpiar</button>
            </div>

            <details className="border border-linea rounded-lg p-3 space-y-2">
              <summary className="cursor-pointer font-semibold">¿Qué es este panel y cómo se lee?</summary>
              <ul className="list-disc pl-5 space-y-1 text-tenue">
                <li>Registra cada pedido que esta página le hace al servidor en <code>/api/auth/*</code> y <code>/api/casos</code>: qué envió,
                  qué respondió y cuánto tardó. Los más nuevos van arriba; hacé clic en uno para ver el detalle.</li>
                <li>Las contraseñas se ocultan. Y no existe en producción: es una ayuda para desarrollar.</li>
                <li>Al cargar la página se hace solo un <code>GET /auth/yo</code> para recuperar la sesión: si hay una
                  vigente responde 200 con tu usuario, y si no, 401. El botón de arriba repite esa prueba a mano.</li>
                <li>No muestra la cookie de sesión: es <code>httpOnly</code>, JavaScript no puede leerla (ese es su
                  propósito). Para verla: DevTools → Aplicación → Cookies.</li>
                <li>Pasá el mouse sobre el número de estado para ver qué significa: 200/201 bien, 400 regla de negocio,
                  401 sin sesión o credenciales incorrectas, 409 email repetido, 422 datos mal formados,
                  429 demasiados intentos.</li>
                <li>Los formularios no validan nada en el navegador a propósito: todo llega al servidor, así se
                  pueden probar sus reglas desde acá.</li>
              </ul>
            </details>

            {pedidos.length === 0 && <p className="text-tenue">Todavía no hubo pedidos.</p>}
            {pedidos.map((pedido) => (
              <details key={pedido.id} className="border border-linea rounded-lg">
                <summary className="flex items-center gap-3 px-3 py-1.5 cursor-pointer">
                  <span className="text-tenue">{pedido.hora}</span>
                  <span className="font-semibold">{pedido.metodo}</span>
                  <span className="text-tenue">{pedido.url}</span>
                  <Estado pedido={pedido} />
                  {pedido.ms !== undefined && <span className="text-tenue">{pedido.ms} ms</span>}
                </summary>
                <div className="grid sm:grid-cols-2 gap-3 p-3">
                  <Bloque titulo="Se envió" valor={pedido.envio} />
                  <Bloque titulo="Respondió" valor={pedido.respuesta} />
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

export default function PanelPruebas() {
  const { usuario } = useSesion()
  return import.meta.env.DEV && usuario?.es_admin ? <Panel /> : null
}
