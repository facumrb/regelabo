from numpy import *
from inner_hair_cell2018 import resting_potential, peak_potential

# =============================================================================
# MÓDULO: FIBRA DEL NERVIO AUDITIVO (Auditory Nerve Fiber — ANF)
# =============================================================================
# Este archivo modela la transducción sináptica entre la célula ciliada
# interna (IHC) y las fibras del nervio auditivo (AN). Simula cómo el
# potencial de membrana de la IHC (Vm) se convierte en tasas de disparo
# neurales (spikes/segundo) a través de un modelo de vesículas sinápticas.
#
# Biología de la sinapsis IHC → AN:
# ----------------------------------
# En la base de cada IHC existen ~19 sinapsis activas (ribbon synapses).
# Cada sinapsis libera vesículas de neurotransmisor (glutamato) hacia una
# fibra del nervio auditivo. La tasa de liberación depende de:
#   1. La concentración de Ca²⁺ intracelular (controlada por canales de Ca²⁺
#      activados por voltaje en la membrana basolateral de la IHC).
#   2. La disponibilidad de vesículas en el pool de liberación rápida (RRP).
#   3. La refractariedad de la fibra nerviosa tras cada potencial de acción.
#
# Tipos de fibras del nervio auditivo:
# -------------------------------------
# Cada IHC está inervada por tres tipos de fibras, clasificadas por su tasa
# de descarga espontánea (cuando no hay sonido):
#   - HSR (High Spontaneous Rate, ~68.5 spikes/s): fibras de umbral bajo,
#     las primeras en responder. Representan ~60% de las fibras (~13 por IHC).
#   - MSR (Medium Spontaneous Rate, ~10 spikes/s): umbral intermedio (~3/IHC).
#   - LSR (Low Spontaneous Rate, ~1 spike/s): umbral alto, responden solo
#     a sonidos intensos. Importantes para codificar en ruido (~3 por IHC).
#
# La pérdida selectiva de fibras LSR y MSR (sin afectar el audiograma) es
# la base de la "Sordera Oculta" (Hidden Hearing Loss / Cochlear Synaptopathy).
# =============================================================================

#parameters
# ---- Parámetros del modelo de vesículas sinápticas ----

# r1: tasa máxima de reposición del pool de reserva (vesículas/s).
# Representa la velocidad a la que el citoplasma de la IHC fabrica y
# transporta nuevas vesículas hacia la zona activa de la sinapsis.
r1=220. #reserve pool max. replenishment rate

# x: tasa de reposición del RRP (Ready Releasable Pool) desde el pool
# de reserva. Basado en datos de Pangršič 2010 y Chapochnikov 2014,
# que midieron la cinética de reciclaje vesicular en sinapsis ribbon.
x=700 #RRP replenishment rate (Pangrisc 2010,Chapocnikov 2014)

# M: número máximo de vesículas en el RRP (sitios de liberación activos).
# Cada sitio puede contener una vesícula lista para fusionarse con la membrana
# y liberar su contenido de glutamato al espacio sináptico.
M=14 # Max. vesicles in the ready release pool or release sites (reasonable, ref?)

# M2: número máximo de vesículas en el pool de reserva. Este pool actúa
# como "almacén" que alimenta al RRP cuando este se agota durante
# estimulación sostenida (adaptación sináptica).
M2=60 # Max. vesicles in the second pool, fitted parameter

# with the paramaters is 250 release/s, because of refractoriness the steady state spike rate goes around 200 spike/s

# ---- Parámetros de refractariedad neural ----
# Después de disparar un potencial de acción, la fibra nerviosa entra en
# un período refractario donde no puede volver a disparar:

# refr_tail: período refractario relativo (0.6 ms). Durante este tiempo,
# la fibra puede disparar pero con probabilidad reducida (umbral elevado).
# Basado en Peterson & Heil 2014.
refr_tail=0.6e-3 # relative refreactory period (from Peterson and Heil 2014)

# abs_refractoriness: período refractario absoluto (0.6 ms). Durante este
# tiempo, la fibra NO puede disparar bajo ninguna circunstancia, sin importar
# la intensidad del estímulo. Basado en Peterson & Heil 2014.
abs_refractoriness=0.6e-3 # absolute refractory period (from Peterson and Heil 2014)

# ss: sensibilidad de la tasa de liberación al potencial de la IHC (V).
# Controla la pendiente de la función sigmoidal que relaciona Vm con
# la tasa de exocitosis. Un valor pequeño = transición más abrupta.
ss=1.5e-3 #sensitivity of release rate on IHC potential, fitted paramter

# tCa: constante de tiempo del canal de Ca²⁺ (0.2 ms).
# Modela la dinámica temporal de apertura/cierre de los canales de calcio
# voltage-dependientes en la membrana basolateral de la IHC. El Ca²⁺ que
# entra a través de estos canales es el trigger directo para la fusión
# de vesículas y liberación de neurotransmisor.
tCa=0.2e-3 #time constant of the Ca2 channel

#driven exocytosis rate is a boltzmann version of Vm, low-pass filter with the time constant of the Ca2+ channels. This is a shortcut to tune the nonlinear relationship between Vm and exocytosis rate based on AF data. Ca2+ signaling varies substantialy between synapses of the same IHC (Frank 2009,Ohn 2016). We use a shortcut Vm->Exocytosis rate, otherwise Vm->Ca2+ (at individual synapse)->exocytosis rate would require the tuning of too many parameters (here one free parameter ss, and 2 fitted parameters sp,psr)

def auditory_nerve_fiber(Vm,fs,spont):
    """
    Simula la respuesta de una fibra del nervio auditivo (ANF).
    
    Convierte el potencial receptor de la IHC (Vm) en una tasa de disparo
    neural (spikes/s) mediante un modelo biofísico de:
      1. Activación de canales de Ca²⁺ → tasa de exocitosis vesicular
      2. Dinámica de dos pools de vesículas (RRP + reserva)
      3. Refractariedad absoluta y relativa de la fibra nerviosa
    
    Parámetros:
    -----------
    Vm : array [tiempo x secciones_cocleares]
        Potencial receptor de la IHC (Voltios)
    fs : float
        Frecuencia de muestreo (Hz)
    spont : int
        Tipo de fibra: 0=LSR, 1=MSR, 2=HSR
    
    Retorna:
    --------
    solution : array [tiempo x secciones_cocleares]
        Probabilidad de disparo por paso temporal (se multiplica por fs
        externamente para obtener spikes/s)
    """
    size=len(Vm[0,:])
    dt=1.0/fs
    # Configuración del tipo de fibra según tasa espontánea:
    # Cada tipo tiene diferente tasa espontánea (sp) y tasa pico (psr).
    # Biológicamente, estas diferencias surgen de variaciones en:
    #   - El número/tamaño de los canales de Ca²⁺ en cada sinapsis
    #   - La distancia entre el canal de Ca²⁺ y el sensor de Ca²⁺ vesicular
    #   - La sensibilidad del sensor de Ca²⁺ de la vesícula
    if(spont==0):
        # LSR: Tasa espontánea baja (1 spike/s), pico moderado (800 sp/s).
        # Fibras con umbral alto, activas solo con sonidos intensos.
        # Cruciales para codificar sonidos en ambientes ruidosos.
        sp=1 #spont rate
        psr=800 #peak spike rate, based upon  Taberner and Liberman 2005
    elif(spont==1):
        # MSR: Tasa espontánea media (10 spikes/s), pico de 1000 sp/s.
        sp=10.0
        psr=1.0e3
    else:
        # HSR: Tasa espontánea alta (68.5 spikes/s), pico de 3000 sp/s.
        # Fibras más sensibles, primeras en saturar con sonidos moderados.
        sp=68.5
        psr=3.0e3
    # parámetros para el tráfico de vesículas
    #    psr=2.7e3
    #    psr=psr*4;

    # ---- Dinámica de vesículas sinápticas (modelo de dos pools) ----
    # El modelo simula el ciclo de vida de las vesículas de neurotransmisor:
    #   Pool de reserva (wt, capacidad M2) → RRP (qt, capacidad M) → exocitosis
    # Las vesículas se mueven del pool de reserva al RRP, y del RRP se liberan
    # al espacio sináptico cuando el Ca²⁺ activa la maquinaria de fusión.
    r=r1/M2 # replenishment rate per vesicle location
    M2_steady=M2-sp/r # estado estacionario del pool de reserva (en reposo)
    Msteady=M*(M2_steady/M2-sp/x) # estado estacionario del RRP (en reposo)
    wt=M2_steady+zeros([1,size]) # pool de reserva inicializado en estado estacionario
    qt=Msteady+zeros([1,size]) # RRP inicializado en estado estacionario
    xdt=x*dt
    rdt=r*dt

    # ---- Inicialización de la refractariedad ----
    # La refractariedad modela el período post-disparo durante el cual
    # la fibra nerviosa no puede (absoluto) o tiene menor probabilidad
    # (relativo) de generar un nuevo potencial de acción.
    alpha_ref=exp(-dt/refr_tail)
    relRefFraction=zeros([1,size]) # fracción de reducción por refractariedad relativa
    available=1.0+zeros([1,size]) # proporción de fibras disponibles (no refractarias)
    buf_lgt=int(round(abs_refractoriness*fs)) # longitud del buffer de historial de disparos
    buf_ref=zeros([buf_lgt,size],dtype=float) # buffer circular para rastrear disparos recientes
    buf_pointer=0

    # ---- Función de transferencia Vm → tasa de exocitosis ----
    # Se modela como una función sigmoidal (tipo Boltzmann) que relaciona
    # el potencial de membrana de la IHC con la probabilidad de liberación
    # vesicular, mediada por la dinámica de los canales de Ca²⁺.
    pp=psr/Msteady # multiplicador que escala la activación a tasa de disparo real

    # Cálculo del voltaje de semi-activación (vh):
    # Se encuentra el punto donde la función sigmoidal produce exactamente
    # la tasa espontánea deseada en reposo y la tasa pico a máxima estimulación.
    rat=log((psr-sp)/sp) # find half activation voltage of exocytosis rate based on peak and spontaneous rate
    vh=rat*ss+resting_potential
    # k0: variable de activación de Ca²⁺ en reposo.
    # Se toma la raíz cuadrada porque se usa un modelo de activación de
    # segundo orden: se filtra sqrt(activación) y luego se eleva al cuadrado,
    # emulando la cooperatividad del Ca²⁺ en la exocitosis vesicular.
    k0=sqrt(1/(1+exp(-(resting_potential-vh)/ss)))+zeros([1,size])  #driven exocytosis rate at rest
    #take the square root, filter it with a first order filter and then square it. This is equivalent to a second order activation of the ion channels
    alphaCa=exp(-dt/tCa)
 

    # ---- Fase de estabilización (50 ms sin estímulo) ----
    # Se ejecutan 50 ms de simulación con el potencial en reposo para
    # que todos los pools de vesículas y variables de refractariedad
    # alcancen un estado estacionario fisiológico antes de aplicar el estímulo.
    zero_time=int(50e-3*fs)
    for i in range(zero_time):
        vesicleReleaseRate=pp*(k0**2)
        releaseProb=vesicleReleaseRate*dt
        qt[qt>M]=M
        wt[wt>M2]=M2
        ejected=releaseProb*qt
        replenishReserve= rdt*(M2-wt)
        replenishRRP=xdt*fmax(wt/M2-qt/M,0)
        qt= qt + replenishRRP - ejected
        wt= wt - replenishRRP + replenishReserve
        firing=(available-relRefFraction)*ejected
        recovered=buf_ref[buf_pointer,:]
        relRefFraction=alpha_ref*relRefFraction+(1-alpha_ref)*recovered
        available=available-firing+recovered
        buf_ref[buf_pointer,:]=firing
        buf_pointer=mod(buf_pointer+1,buf_lgt)

    # ---- Simulación principal con estímulo ----
    # Aquí se procesa cada muestra temporal del potencial Vm de la IHC:
    k=k0
    # Función de activación sigmoidal aplicada a cada muestra de Vm:
    # Convierte el potencial de la IHC en una variable de activación de Ca²⁺.
    kin=sqrt(1/(1+exp(-(Vm-vh)/ss)))
    solution=zeros_like(Vm)
    for i in range(len(kin[:,0])):
        # Filtrado paso bajo de la activación de Ca²⁺ (constante tCa):
        # Modela la inercia de apertura/cierre de los canales iónicos de calcio.
        k=alphaCa*k+(1-alphaCa)*kin[i,:]
        # Tasa de liberación vesicular: proporcional al cuadrado de la activación
        # de Ca²⁺ (cooperatividad de segundo orden del sensor de Ca²⁺).
        vesicleReleaseRate=pp*(k**2)
        releaseProb=vesicleReleaseRate*dt
        # Restricciones fisiológicas: los pools no pueden tener valores negativos
        # ni exceder su capacidad máxima.
        qt[qt<0]=0
        wt[wt<0]=0
        qt[qt>M]=M
        wt[wt>M2]=M2
        # Vesículas liberadas: proporción del RRP que se fusiona con la membrana.
        ejected=releaseProb*qt
        # Reposición del pool de reserva: tasa proporcional al espacio disponible.
        replenishReserve= rdt*(M2-wt)
        # Reposición del RRP desde el pool de reserva: solo ocurre si el ratio
        # de llenado del reserva supera al del RRP (flujo unidireccional).
        replenishRRP=xdt*fmax(wt/M2-qt/M,0)
        # Actualización de ambos pools de vesículas:
        qt= qt + replenishRRP - ejected
        wt= wt - replenishRRP + replenishReserve
        # Probabilidad de disparo final: modulada por la refractariedad.
        # Solo las fibras "disponibles" (no refractarias) pueden disparar.
        firing=(available-relRefFraction)*ejected
        # Recuperación de fibras del período refractario absoluto:
        recovered=buf_ref[buf_pointer,:]
        # Actualización de la refractariedad relativa (decae exponencialmente):
        relRefFraction=alpha_ref*relRefFraction+(1-alpha_ref)*recovered
        # Actualización de fibras disponibles:
        available=available-firing+recovered
        # Registro del disparo actual en el buffer circular (para refractariedad absoluta):
        buf_ref[buf_pointer,:]=firing
        buf_pointer=mod(buf_pointer+1,buf_lgt)
        # Almacenamiento de la tasa de disparo instantánea:
        solution[i,:]=firing
    return solution




