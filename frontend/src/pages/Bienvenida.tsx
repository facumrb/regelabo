import { Link } from 'react-router-dom'
import { botonPrimario, botonSecundario } from '../components/estilos'

const FUNCIONES = [
  {
    titulo: 'Cargá un audiograma',
    texto: 'Ingresá los umbrales a mano o subí un archivo CSV. El sistema calcula el promedio tonal, clasifica la pérdida y arma un perfil coclear.',
    pronto: false,
  },
  {
    titulo: 'Simulá la respuesta neural',
    texto: 'Ejecutá el modelo de Verhulst et al. (2018) y mirá las ondas I, III y V del ABR, la respuesta EFR y su espectro, con gráficos interactivos.',
    pronto: false,
  },
  {
    titulo: 'Organizá tu trabajo en casos',
    texto: 'Cada caso reúne sus audiogramas y simulaciones, y es solo tuyo. No guardamos nombres ni datos que identifiquen a nadie.',
    pronto: false,
  },
  {
    titulo: 'Compará con arquetipos',
    texto: 'Contrastá un ABR con una biblioteca de patrones conocidos y registrá tu hipótesis de estudio.',
    pronto: true,
  },
]

/** Pantalla de inicio para quien no inició sesión: cuenta qué se puede hacer y invita a entrar. */
export default function Bienvenida() {
  return (
    <div className="max-w-4xl mx-auto space-y-10">
      <section className="text-center space-y-4 pt-4">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Laboratorio Virtual Auditivo
        </h2>
        <p className="text-slate-300 max-w-2xl mx-auto">
          Simulá cómo responde el sistema auditivo ante distintas pérdidas de audición, sin necesidad de
          programar ni de contar con una computadora potente.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link to="/registro" className={botonPrimario}>Crear una cuenta</Link>
          <Link to="/login" className={botonSecundario}>Ya tengo cuenta: iniciar sesión</Link>
        </div>
      </section>

      <section>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Qué podés hacer
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {FUNCIONES.map((f) => (
            <div key={f.titulo} className="bg-dark-800/80 border border-slate-800 rounded-2xl p-5 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-white">{f.titulo}</h4>
                {f.pronto && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Próximamente
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{f.texto}</p>
            </div>
          ))}
        </div>
      </section>

      <p className="text-center text-xs text-slate-500 max-w-2xl mx-auto">
        Herramienta de estudio y experimentación. No es de uso profesional y sus resultados no constituyen
        un diagnóstico clínico.
      </p>
    </div>
  )
}
