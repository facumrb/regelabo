import { useEffect, useState, type FormEvent } from 'react'
import { Aviso } from '../../components/ui'
import { avisoAtencion, botonPrimario, botonSecundario, botonTexto, entrada, etiqueta, panel, vacio } from '../../components/estilos'
import { mensajeDeError, type TipoPerfil } from '../../services/auth'
import { usuariosAdminApi, type UsuarioAdmin } from '../../services/admin'
import { avisarPendientes } from '../../services/comentarios'
import { TIPOS } from './ComentariosAdmin'

const hora = (fecha: string) => new Date(fecha).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
const fechaYHora = (fecha: string) => `${new Date(fecha).toLocaleDateString('es-AR')} a las ${hora(fecha)}`
const bloqueado = (u: UsuarioAdmin) => u.bloqueado_hasta !== null && new Date(u.bloqueado_hasta) > new Date()

/** Mail ya escrito, al email registrado de la cuenta: solo lo recibe su dueño (decisión 028). */
function enlaceDeMail(u: UsuarioAdmin, contrasena: string): string {
  const asunto = 'regelabo: tu contraseña temporal'
  const cuerpo = `Hola ${u.nombre}:\n\n` +
    'Recibimos tu pedido para restablecer la contraseña de regelabo. Tu contraseña temporal es:\n\n' +
    `${contrasena}\n\n` +
    `Entrá con ella y cambiala en Mi cuenta: ${window.location.origin}/cuenta\n\n` +
    'Si no lo pediste vos, respondé este mail para avisarnos.'
  return `mailto:${u.email}?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`
}

/** Usuarios (decisión 028, etapa 3): totales sin contenido (RN4) y acciones sobre cuentas que no son admin. */
export default function UsuariosAdmin() {
  const [texto, setTexto] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [tipo, setTipo] = useState<TipoPerfil | ''>('')
  const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([])
  const [pedidos, setPedidos] = useState<UsuarioAdmin[]>([])
  const [siguiente, setSiguiente] = useState<string | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  // La temporal no se muestra en pantalla: solo va dentro del mail. Al recargar la página se pierde.
  const [temporal, setTemporal] = useState<{ usuario: UsuarioAdmin; contrasena: string } | null>(null)

  const cargarPedidos = async () => {
    try {
      setPedidos((await usuariosAdminApi.listar({ con_pedido: true }, null)).usuarios)
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  const cargar = async (despuesDe: string | null) => {
    setCargando(true)
    setError(null)
    try {
      const pagina = await usuariosAdminApi.listar({ busqueda: busqueda || undefined, tipo: tipo || undefined }, despuesDe)
      setUsuarios((anteriores) => (despuesDe ? [...anteriores, ...pagina.usuarios] : pagina.usuarios))
      setSiguiente(pagina.siguiente)
    } catch (e) {
      setError(mensajeDeError(e))
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarPedidos()
  }, [])

  useEffect(() => {
    cargar(null)
  }, [busqueda, tipo])

  const buscar = (evento: FormEvent) => {
    evento.preventDefault()
    setBusqueda(texto.trim())
  }

  const reemplazar = (cambiado: UsuarioAdmin) => {
    const cambiar = (lista: UsuarioAdmin[]) => lista.map((u) => (u.id === cambiado.id ? cambiado : u))
    setUsuarios(cambiar)
    setPedidos(cambiar)
  }

  const actuar = async (accion: () => Promise<UsuarioAdmin>) => {
    setError(null)
    try {
      reemplazar(await accion())
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  const resetear = async (u: UsuarioAdmin) => {
    if (!window.confirm(`¿Generar una contraseña temporal para ${u.email}? Se cierran todas sus sesiones.`)) return
    setError(null)
    try {
      setTemporal({ usuario: u, contrasena: await usuariosAdminApi.resetearContrasena(u.id) })
      avisarPendientes()
      // El pedido queda atendido y la cuenta, desbloqueada
      setPedidos((lista) => lista.filter((x) => x.id !== u.id))
      setUsuarios((lista) => lista.map((x) => (x.id === u.id
        ? { ...x, bloqueado_hasta: null, restablecimiento_pedido_en: null } : x)))
    } catch (e) {
      setError(mensajeDeError(e))
    }
  }

  const tarjeta = (u: UsuarioAdmin) => (
    <li key={u.id} className={`${panel} p-4 md:p-5 space-y-3`}>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        <span className="font-medium text-tinta">{u.nombre}</span>
        <span className="text-tenue break-all">{u.email}</span>
        <span className="text-tenue">{TIPOS[u.tipo_perfil]}</span>
        {u.es_admin && <span className="text-[11px] px-1.5 rounded-full border border-linea text-tenue">admin</span>}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-tenue">
        <span>Alta: {new Date(u.creado_en).toLocaleDateString('es-AR')}</span>
        <span>{u.casos} {u.casos === 1 ? 'caso' : 'casos'}</span>
        <span>{u.simulaciones} {u.simulaciones === 1 ? 'simulación' : 'simulaciones'}</span>
        {!u.email_verificado && <span className="text-tinta">Email sin verificar</span>}
        {bloqueado(u) && <span className="text-tinta">Bloqueada hasta las {hora(u.bloqueado_hasta!)}</span>}
      </div>

      {u.restablecimiento_pedido_en && (
        <p className={`px-3 py-2 rounded-lg border text-sm ${avisoAtencion}`}>
          Pidió restablecer la contraseña el {fechaYHora(u.restablecimiento_pedido_en)}.
        </p>
      )}

      {u.es_admin ? (
        <p className="text-xs text-tenue">Las cuentas de admin se manejan por comando.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {u.restablecimiento_pedido_en && (
            <button type="button" className={botonPrimario} onClick={() => resetear(u)}>Contraseña temporal</button>
          )}
          {bloqueado(u) && (
            <button type="button" className={botonTexto} onClick={() => actuar(() => usuariosAdminApi.desbloquear(u.id))}>
              Desbloquear
            </button>
          )}
          {!u.email_verificado && (
            <button type="button" className={botonTexto} onClick={() => actuar(() => usuariosAdminApi.verificarEmail(u.id))}>
              Verificar email
            </button>
          )}
        </div>
      )}
    </li>
  )

  return (
    <div className="space-y-6">
      {temporal && (
        <div role="status" className={`px-4 py-3 rounded-xl border text-sm space-y-2 ${avisoAtencion}`}>
          <p>
            Se generó la contraseña temporal de <strong>{temporal.usuario.email}</strong>. Mandásela por mail: el botón
            abre tu programa de correo con el mail ya escrito, dirigido al email registrado de la cuenta.
          </p>
          <div className="flex flex-wrap gap-2">
            <a href={enlaceDeMail(temporal.usuario, temporal.contrasena)} className={botonPrimario}>Enviar por mail</a>
            <button type="button" className={botonTexto} onClick={() => setTemporal(null)}>Listo, ya lo mandé</button>
          </div>
        </div>
      )}

      {pedidos.length > 0 && (
        <section className="space-y-3" aria-labelledby="titulo-pedidos">
          <h2 id="titulo-pedidos" className={etiqueta}>Pedidos de restablecimiento ({pedidos.length})</h2>
          <ul className="space-y-3">{pedidos.map(tarjeta)}</ul>
        </section>
      )}

      <div className="flex flex-col sm:flex-row sm:items-end gap-3">
        <form onSubmit={buscar} role="search" className="flex gap-2 sm:w-96">
          <label className="flex-1 space-y-1.5">
            <span className="text-sm text-tenue">Buscar por email o nombre</span>
            <input className={entrada} type="search" value={texto} maxLength={254} onChange={(e) => setTexto(e.target.value)} />
          </label>
          <button type="submit" className={`${botonSecundario} self-end`}>Buscar</button>
        </form>
        <label className="sm:w-56 space-y-1.5">
          <span className="text-sm text-tenue">Tipo de usuario</span>
          <select className={entrada} value={tipo} onChange={(e) => setTipo(e.target.value as TipoPerfil | '')}>
            <option value="">Todos</option>
            {Object.entries(TIPOS).map(([v, t]) => <option key={v} value={v}>{t}</option>)}
          </select>
        </label>
      </div>

      {error && <Aviso tipo="error">{error}</Aviso>}

      {!cargando && !error && usuarios.length === 0 && <p className={vacio}>No hay usuarios con esos filtros.</p>}

      <ul className="space-y-3">{usuarios.map(tarjeta)}</ul>

      {siguiente && (
        <div className="text-center">
          <button onClick={() => cargar(siguiente)} disabled={cargando} className={botonSecundario}>
            {cargando ? 'Cargando…' : 'Cargar más'}
          </button>
        </div>
      )}
    </div>
  )
}
