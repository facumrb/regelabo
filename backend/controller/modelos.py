"""
Objetos de negocio (Pydantic): usuarios, simulación y audiogramas.
"""

from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, computed_field

TipoPerfil = Literal["estudiante", "investigador", "fonoaudiologo"]


class Usuario(BaseModel):
    """Usuario del sistema tal como lo ve la capa de negocio (incluye datos de seguridad)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    nombre: str
    tipo_perfil: TipoPerfil
    es_admin: bool
    # exclude=True: nunca sale en un model_dump, así no se filtra por una respuesta de la API
    password_hash: str = Field(exclude=True)
    intentos_fallidos: int
    bloqueado_hasta: Optional[datetime]
    email_verificado_en: Optional[datetime] = None
    restablecimiento_pedido_en: Optional[datetime] = None
    debe_cambiar_contrasena: bool = False

    @computed_field  # sale en model_dump: así llega a UsuarioPublico
    @property
    def email_verificado(self) -> bool:
        return self.email_verificado_en is not None


class UsuarioPublico(BaseModel):
    """Lo que la API muestra de un usuario."""

    id: UUID
    email: str
    nombre: str
    tipo_perfil: TipoPerfil
    es_admin: bool
    email_verificado: bool
    debe_cambiar_contrasena: bool = False


class RegistroInput(BaseModel):
    email: EmailStr
    password: str
    nombre: str = Field(min_length=1, max_length=100)
    tipo_perfil: TipoPerfil
    acepta_aviso: bool = Field(description="Aceptación del aviso de uso no profesional (RN9)")


class LoginInput(BaseModel):
    email: str
    password: str


class ContrasenaNuevaInput(BaseModel):
    """Para elegir la contraseña después de entrar con una temporal: no pide la actual."""

    nueva: str


class CambioContrasenaInput(BaseModel):
    actual: str
    nueva: str


class OlvideInput(BaseModel):
    email: str


class TokenInput(BaseModel):
    token: str = Field(max_length=100)


class RecuperarInput(BaseModel):
    token: str = Field(max_length=100)
    nueva: str


Sexo = Literal["femenino", "masculino", "otro"]


class CasoInput(BaseModel):
    """Datos de un caso al crearlo o editarlo. Nada que identifique a una persona (decisión 008)."""

    alias: str = Field(min_length=1, max_length=100)
    edad: Optional[int] = Field(default=None, ge=0, le=120)
    sexo: Optional[Sexo] = None
    notas: Optional[str] = Field(default=None, max_length=2000)


class Caso(CasoInput):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creado_en: datetime


class PaginaDeCasos(BaseModel):
    casos: List[Caso]
    siguiente: Optional[UUID] = Field(description="Pasarlo como `despues_de` para pedir la página siguiente; "
                                                  "null si no hay más")


class ParametrosSimulacion(BaseModel):
    """
    Parámetros de entrada de una simulación del modelo auditivo.
    Los rangos válidos (RN3) los verifica `controller.simulaciones.validar_parametros`.
    """

    carrier_freq: float = Field(
        default=4000.0,
        description="Frecuencia portadora del estímulo en Hz (típicamente 500, 1000, 2000, 4000)."
    )
    poles_profile: str = Field(
        default="Flat00",
        # Solo estos caracteres: el nombre se usa para armar una ruta de archivo
        pattern=r"^[A-Za-z0-9_-]+$",
        max_length=100,
        description="Perfil de polos de Shera para modelar pérdida auditiva (ej: Flat00, Flat20, Slope20)."
    )
    spl_level: float = Field(default=70.0, description="Nivel de presión sonora del estímulo en dB SPL.")
    f_mod: float = Field(
        default=110.0,
        description="Frecuencia de modulación del estímulo RAM en Hz (default: 110 Hz)."
    )
    nH: int = Field(
        default=13,
        description="Fibras HSR (alta tasa espontánea) por IHC. Reducir para simular sinaptopatía."
    )
    nM: int = Field(default=3, description="Fibras MSR (media tasa espontánea) por IHC.")
    nL: int = Field(default=3, description="Fibras LSR (baja tasa espontánea) por IHC.")


class SimulacionInput(ParametrosSimulacion):
    caso_id: Optional[UUID] = Field(default=None, description="Caso asociado a la simulación (opcional)")


class SpectrumData(BaseModel):
    """Datos de espectro de frecuencia (FFT) para graficar en Plotly."""
    frequencies: List[float] = Field(description="Frecuencias en Hz (0 a 1000 Hz)")
    amplitudes: List[float] = Field(description="Amplitud de potencia en µV")


class ABRWavesData(BaseModel):
    """Ondas ABR y respuesta temporal para graficar en Plotly."""
    time_ms: List[float] = Field(description="Eje temporal en milisegundos")
    w1: List[float] = Field(description="Onda I: Nervio Auditivo (µV)")
    w3: List[float] = Field(description="Onda III: Núcleo Coclear (µV)")
    w5: List[float] = Field(description="Onda V: Colículo Inferior (µV)")
    efr_wave: List[float] = Field(description="Suma total de ondas ABR (W1+W3+W5) (µV)")


class HarmonicPeak(BaseModel):
    """Detalle de cada armónico analizado para el EFR."""
    harmonic_order: int
    frequency_hz: float
    amplitude_uv: float


# ---- Estados internos (decisión 023) ----
# Las series son matrices [muestra][canal]; `canales` indica qué entradas de `EstadosInternos.canales` usa.

class CanalInterno(BaseModel):
    """Canal coclear graficado: la frecuencia pedida y la característica del canal más cercano."""
    frecuencia_solicitada_hz: float
    frecuencia_caracteristica_hz: float


class PoloShera(BaseModel):
    """Figura 1: polo de Shera (control de ganancia OHC) por tiempo y frecuencia característica."""
    fs_hz: float
    frecuencia_caracteristica_hz: List[float]
    valores: List[List[float]] = Field(description="[muestra][canal], adimensional")


class CorrientesIHC(BaseModel):
    """Figura 2: corrientes (nA) y potencial de membrana (mV) de la IHC."""
    fs_hz: float
    ventana_ms: List[float]
    canales: List[int]
    imet_na: List[List[float]]
    ikf_na: List[List[float]]
    iks_na: List[List[float]]
    vm_mv: List[List[float]]


class EstadosFibra(BaseModel):
    """Vesículas disponibles q(t), reserva w(t) y fracción fuera del período refractario A(t)."""
    q: List[List[float]]
    w: List[List[float]]
    a: List[List[float]]


class Vesiculas(BaseModel):
    """Figuras 3 a 6: estados sinápticos por tipo de fibra, en los cuatro canales."""
    fs_hz: float
    ventana_ms: List[float]
    hsr: EstadosFibra
    msr: EstadosFibra
    lsr: EstadosFibra


class TroncoCNIC(BaseModel):
    """Figura 7: componentes excitatoria e inhibitoria (spikes/s) de CN e IC; la neta es su resta."""
    fs_hz: float
    ventana_ms: List[float]
    canales: List[int]
    cn_exc: List[List[float]]
    cn_inh: List[List[float]]
    ic_exc: List[List[float]]
    ic_inh: List[List[float]]


class EstadosInternos(BaseModel):
    """Datos de las siete figuras de estados internos de una simulación."""
    canales: List[CanalInterno]
    polo_shera: PoloShera
    ihc: CorrientesIHC
    vesiculas: Vesiculas
    cn_ic: TroncoCNIC


class SimulationResponse(BaseModel):
    """Resultados calculados de la simulación biológica."""
    status: str = "success"
    execution_time_seconds: float
    efr_value_uv: float = Field(description="Valor total del biomarcador EFR en microvoltios (µV)")
    harmonics: List[HarmonicPeak]
    fft_spectrum: SpectrumData
    abr_waves: ABRWavesData
    parameters_used: Dict[str, object]
    # Pesan varios MB: no viajan con el resultado, se guardan aparte y tienen su propio endpoint
    estados_internos: Optional[EstadosInternos] = Field(default=None, exclude=True)


class AudiogramPoint(BaseModel):
    """Punto de umbral auditivo en una frecuencia específica."""
    frequency: float = Field(
        ge=100, le=16000, description="Frecuencia en Hz (ej: 250, 500, 1000, 2000, 4000, 8000)"
    )
    hearing_loss_db: float = Field(
        ge=-10, le=120, description="Pérdida auditiva en dB HL (0 = normal, >25 = pérdida)"
    )


class AudiogramInput(BaseModel):
    """Estructura de entrada manual para un audiograma."""
    patient_name: Optional[str] = Field(default="Paciente", description="Identificador o nombre del paciente")
    points: List[AudiogramPoint] = Field(description="Lista de puntos audiométricos")
    caso_id: Optional[UUID] = Field(
        default=None, description="Caso propio donde guardarlo (decisión 032); el perfil toma su alias")


class PerfilAuditivo(BaseModel):
    """Un perfil de polos, descripto para un profesional, con la curva pedida y la que el modelo simula."""
    nombre: str = Field(description="Identificador interno (carpeta); es el que va en poles_profile")
    etiqueta: str = Field(description="Descripción legible, con el grado y el PTA")
    forma: Literal["plana", "descendente", "combinada", "personalizada"]
    grado: Literal["normal", "leve", "moderada", "severa"] = Field(description="RN2, según el PTA pedido")
    patron: Literal["plano", "caida_en_agudos"] = Field(description="RN2, según la curva pedida")
    pta: float = Field(description="PTA de la curva pedida, en dB HL")
    curva_pedida: List[AudiogramPoint]
    curva_simulada: List[AudiogramPoint] = Field(description="La pedida, recortada al techo del modelo")
    frecuencias_recortadas: List[float] = Field(
        description="Frecuencias donde se simulan más de 5 dB menos de lo pedido")


class AudiogramResponse(BaseModel):
    """Resultado del análisis del audiograma y su perfil de polos asociado."""
    status: str = "success"
    patient_name: str
    points: List[AudiogramPoint]
    matched_profile: str = Field(description="Perfil de polos generado para la simulación (nombre interno)")
    mean_hearing_loss: float = Field(description="Pérdida promedio tonal (PTA) en dB HL")
    clinical_classification: str = Field(description="Clasificación del audiograma según RN2 (orientativa)")
    notes: str = Field(description="Cómo se generó el perfil")
    perfil: PerfilAuditivo
    audiograma_id: Optional[UUID] = Field(default=None, description="Si se guardó en un caso (decisión 032)")


EstadoSimulacion = Literal["en_cola", "ejecutando", "completada", "error"]


class Simulacion(BaseModel):
    """Una simulación pedida por un usuario, con su estado y, si terminó, su resultado."""

    id: UUID
    estado: EstadoSimulacion
    caso_id: Optional[UUID]
    parametros: ParametrosSimulacion
    creado_en: datetime
    iniciada_en: Optional[datetime]
    finalizada_en: Optional[datetime]
    mensaje_error: Optional[str]
    reutilizada: bool = Field(description="True si el resultado ya existía (RN10) y no pasó por la cola")
    posicion: Optional[int] = Field(default=None, description="Lugar en la cola; solo si está en_cola")
    resultado: Optional[SimulationResponse] = Field(default=None, description="Solo si está completada")
    # exclude=True: la huella es interna, nunca sale por la API
    huella: str = Field(exclude=True)


class PaginaDeSimulaciones(BaseModel):
    simulaciones: List[Simulacion]
    siguiente: Optional[UUID] = Field(description="Pasarlo como `despues_de` para pedir la página siguiente; "
                                                  "null si no hay más")


EstadoComentario = Literal["nuevo", "leido", "archivado"]


class ComentarioInput(BaseModel):
    """RN13: texto libre, no vacío (sin contar espacios) y de hasta 2000 caracteres."""

    texto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class Comentario(BaseModel):
    """Un comentario tal como lo ve el admin, con los datos de quien lo escribió."""

    id: UUID
    texto: str
    estado: EstadoComentario
    creado_en: datetime
    autor_nombre: str
    autor_email: str
    autor_tipo: TipoPerfil


class PaginaDeComentarios(BaseModel):
    comentarios: List[Comentario]
    siguiente: Optional[UUID] = Field(description="Pasarlo como `despues_de` para pedir la página siguiente; "
                                                  "null si no hay más")


class CambioEstadoComentario(BaseModel):
    estado: EstadoComentario


class Pendientes(BaseModel):
    """Lo que el admin tiene para revisar: alimenta el contador del menú."""

    comentarios_nuevos: int
    restablecimientos: int


class UsuarioAdmin(BaseModel):
    """Un usuario como lo ve el panel de admin: estado de la cuenta y totales, sin contenido (RN4)."""

    id: UUID
    email: str
    nombre: str
    tipo_perfil: TipoPerfil
    es_admin: bool
    creado_en: datetime
    bloqueado_hasta: Optional[datetime]
    email_verificado: bool
    restablecimiento_pedido_en: Optional[datetime]
    casos: int
    simulaciones: int


class PaginaDeUsuarios(BaseModel):
    usuarios: List[UsuarioAdmin]
    siguiente: Optional[UUID] = Field(description="Pasarlo como `despues_de` para pedir la página siguiente; "
                                                  "null si no hay más")


class ContrasenaTemporal(BaseModel):
    """Se muestra una sola vez al admin, que se la pasa al usuario (decisión 028)."""

    contrasena_temporal: str


class SimulacionEnCurso(BaseModel):
    """Una simulación en cola o ejecutando, para el panel: quién y desde cuándo, sin parámetros (RN4)."""

    id: UUID
    usuario_email: str
    estado: Literal["en_cola", "ejecutando"]
    creado_en: datetime
    iniciada_en: Optional[datetime]


class EstadoCola(BaseModel):
    """Estado de la cola para el panel de admin (decisión 028). Los totales de 24 h cuentan por fin."""

    en_cola: int
    ejecutando: int
    tope_cola: int
    completadas_24h: int = Field(description="Ejecutadas por el worker")
    desde_cache_24h: int = Field(description="Resueltas al instante con un resultado ya calculado (RN10)")
    errores_24h: int
    duracion_promedio_s: Optional[float] = Field(description="De las ejecutadas en 24 h; null si no hubo")
    worker_detenido: Optional[bool] = Field(
        description="Deducido: hay simulaciones esperando y ninguna ejecutándose. null si la cola está vacía")
    en_curso: List[SimulacionEnCurso]


class AudiogramaGuardado(BaseModel):
    """Un audiograma guardado en un caso (decisión 032), con la clasificación de RN2."""

    id: UUID
    creado_en: datetime
    origen: Literal["manual", "archivo"]
    pta_db: float
    gravedad: Literal["normal", "leve", "moderada", "severa"]
    patron: Literal["plano", "caida_en_agudos"]
    perfil: str = Field(description="Perfil de polos generado: el que va en poles_profile")
    puntos: List[AudiogramPoint]
