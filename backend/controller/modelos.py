"""
Objetos de negocio (Pydantic): usuarios, simulación y audiogramas.
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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


class UsuarioPublico(BaseModel):
    """Lo que la API muestra de un usuario."""

    id: UUID
    email: str
    nombre: str
    tipo_perfil: TipoPerfil
    es_admin: bool


class RegistroInput(BaseModel):
    email: EmailStr
    password: str
    nombre: str = Field(min_length=1, max_length=100)
    tipo_perfil: TipoPerfil
    acepta_aviso: bool = Field(description="Aceptación del aviso de uso no profesional (RN9)")


class LoginInput(BaseModel):
    email: str
    password: str


class CambioContrasenaInput(BaseModel):
    actual: str
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
