import { Link } from 'react-router-dom'
import { botonPrimario, botonTexto, etiqueta, panel } from '../components/estilos'

const PASOS = [
  ['1 · Cargá un audiograma', 'Ingresá los umbrales o subí un CSV y generá un perfil.'],
  ['2 · Simulá', 'El modelo corre en segundo plano, unos 80 segundos.'],
  ['3 · Interpretá', 'EFR, ABR y espectro, y los estados internos de la cóclea.'],
]

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
    <div className="space-y-12 md:space-y-16">
      <section className="max-w-3xl pt-4 md:pt-12">
        <h1 className="text-4xl md:text-6xl font-semibold tracking-tight leading-[1.05] text-tinta">
          Laboratorio Virtual Auditivo
        </h1>
        <p className="mt-6 text-lg md:text-xl text-tenue max-w-2xl">
          Simulá cómo responde el sistema auditivo ante distintas pérdidas de audición, sin necesidad de
          programar ni de contar con una computadora potente.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row gap-3">
          <Link to="/registro" className={`${botonPrimario} min-h-[52px] px-6 text-base`}>Crear una cuenta</Link>
          <Link to="/login" className={`${botonTexto} min-h-[52px] px-6 text-base`}>Ya tengo cuenta: iniciar sesión</Link>
        </div>
      </section>

      <ol className="grid md:grid-cols-3 gap-5 md:gap-12 pt-8 border-t border-linea">
        {PASOS.map(([titulo, texto]) => (
          <li key={titulo}>
            <b className="block font-semibold text-tinta mb-1">{titulo}</b>
            <span className="text-sm text-tenue">{texto}</span>
          </li>
        ))}
      </ol>

      <section className="space-y-3">
        <h2 className={etiqueta}>Qué podés hacer</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {FUNCIONES.map((f) => (
            <div key={f.titulo} className={`${panel} p-5 space-y-2`}>
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-semibold text-tinta">{f.titulo}</h3>
                {f.pronto && (
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-acento-suave text-tinta">Próximamente</span>
                )}
              </div>
              <p className="text-sm text-tenue leading-relaxed">{f.texto}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Aviso obligatorio (RN9) */}
      <p className="text-sm text-tenue max-w-2xl">
        Herramienta de estudio y experimentación. No es de uso profesional y sus resultados no constituyen
        un diagnóstico clínico.
      </p>
    </div>
  )
}
