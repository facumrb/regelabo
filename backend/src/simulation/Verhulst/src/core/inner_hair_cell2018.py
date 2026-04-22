from numpy import *
from scipy import signal

# =============================================================================
# MÓDULO: CÉLULA CILIADA INTERNA (Inner Hair Cell — IHC)
# =============================================================================
# Este archivo modela la transducción mecano-eléctrica que ocurre en las
# células ciliadas internas (IHC) de la cóclea.
#
# Biología de la IHC:
# --------------------
# Las IHC son los verdaderos receptores sensoriales del oído interno.
# Cuando la membrana basilar vibra (por efecto del sonido), los estereocilios
# de la IHC se deflectan, abriendo canales iónicos mecanosensibles (MET)
# en sus puntas. Esto permite la entrada de iones K⁺ y Ca²⁺, generando
# una corriente de transducción (Imet) que despolariza la célula.
#
# El potencial de membrana resultante (Vm) es la "señal eléctrica" que
# la IHC produce en respuesta al sonido. Este Vm controla la liberación
# de neurotransmisor en las sinapsis ribbon de la base de la IHC, que a
# su vez activa las fibras del nervio auditivo.
#
# El modelo implementa un circuito eléctrico equivalente de la IHC con:
#   - Canal MET (mecanotransducción): corriente Imet controlada por la
#     deflexión de los estereocilios (proporcional a velocidad de la BM).
#   - Canales de K⁺ (rápido y lento): corrientes Ikf e Iks que repolarizan
#     la célula, actuando como un "freno" que limita la despolarización.
#   - Corriente de fuga (Ileak): conductancia pasiva de la membrana.
#   - Capacitancia de membrana (Cm): determina la velocidad de cambio del Vm.
#
# La ecuación fundamental es: Cm * dVm/dt = -(Imet + Ikf + Iks + Ileak)
# =============================================================================

# ---- Parámetros biofísicos de la IHC ----

# Cm: Capacitancia de la membrana celular de la IHC (12.5 pF).
# Representa la capacidad de la membrana lipídica para almacenar carga.
# Un valor pequeño significa que pequeñas corrientes cambian rápidamente el Vm.
Cm=12.5e-12;

# ---- Parámetros del canal MET (Mechano-Electrical Transduction) ----
# Gmet: Conductancia máxima del canal MET (30 nS).
# Es la conductancia total cuando todos los canales MET están abiertos.
Gmet=30e-9;
# s1, s0: Parámetros de sensibilidad de la función de activación Boltzmann
# del canal MET. Controlan cuánta deflexión de estereocilios se necesita
# para abrir los canales. s0 y s1 definen las pendientes de la función
# sigmoidal de doble Boltzmann que modela la probabilidad de apertura.
s1=16e-9;
s0=s1*3;
# x0: Punto de operación en reposo de la deflexión de estereocilios (20 nm).
# En reposo, los estereocilios tienen una deflexión basal que mantiene
# algunos canales MET parcialmente abiertos (corriente de reposo).
x0=20e-9;
#x0=34e-9
# tauMet: Constante de tiempo del canal MET (50 µs).
# Modela la velocidad de apertura/cierre del canal mecanosensible.
# Es extremadamente rápida porque la transducción mecánica directa
# no requiere segundos mensajeros (a diferencia de la fototransducción).
tauMet=50e-6;

# ---- Parámetros de la corriente de fuga ----
# Gleak: Conductancia de fuga (0 nS, desactivada en este modelo).
# Representaría canales iónicos pasivos siempre abiertos en la membrana.
Gleak=00.0e-9;

# ---- Potenciales electroquímicos ----
# EP: Potencial endococlear (+90 mV). Es el potencial positivo que existe
# en la endolinfa (líquido que baña los estereocilios de las IHC).
# Este potencial es generado por la estría vascular y actúa como una
# "batería biológica" que amplifica la corriente de transducción.
# La diferencia de potencial entre la endolinfa (+90 mV) y el interior
# de la IHC (-57 mV en reposo) crea una fuerza electromotriz de ~147 mV
# que impulsa los iones K⁺ hacia dentro de la célula.
EP=90e-3;
# Ekf: Potencial de equilibrio del canal de K⁺ rápido (-71 mV).
Ekf=-71e-3;
# Eks: Potencial de equilibrio del canal de K⁺ lento (-78 mV).
Eks=-78e-3;

# ---- Parámetros de los canales de K⁺ (repolarización) ----
# Gk: Conductancia máxima de los canales de K⁺ (230 nS).
# Los canales de K⁺ se activan cuando la IHC se despolariza, permitiendo
# la salida de K⁺ y devolviendo el Vm hacia el potencial de reposo.
# Son el principal mecanismo de retroalimentación negativa de la célula.
Gk=230e-9;
# xk: Voltaje de semi-activación del canal de K⁺ (-31 mV).
# Es el Vm al cual el 50% de los canales de K⁺ están abiertos.
xk=-31e-3;
# sk: Pendiente de la función de activación Boltzmann del K⁺ (10.5 mV).
sk=10.5e-3;
# tkf1, tkf2: Constantes de tiempo del canal de K⁺ rápido (0.3 y 0.1 ms).
# El canal rápido permite una repolarización rápida, crucial para que la
# IHC pueda seguir fielmente las oscilaciones de alta frecuencia.
tkf1=0.3e-3;
tkf2=0.1e-3;
# tks1, tks2: Constantes de tiempo del canal de K⁺ lento (8 y 2 ms).
# El canal lento contribuye a la adaptación: reduce gradualmente la
# respuesta durante estimulación sostenida (como un "control de ganancia").
tks1=8e-3;
tks2=2e-3;

# ---- Parámetros del canal de Ca²⁺ (no usado activamente en esta versión) ----
# GcaM: Conductancia máxima del canal de Ca²⁺ de la membrana (4.1 nS).
GcaM=4.1e-9;
tauCa=0.25e-3;
xca=-30.0e-3;
sca=7.5e-3;
# Eca: Potencial de equilibrio del Ca²⁺ (+45 mV).
Eca=45e-3;

# ---- Parámetros de inhibición por Ca²⁺ intracelular (no usado activamente) ----
tauInS=0.5;
tauInF=50e-3;
CaInMax=0.4;
xCaIn=-43e-3;
sCaIn=6e-3;
Ileak=0.0e-9;

# ---- Potenciales de referencia ----
# resting_potential: Potencial de membrana de la IHC en reposo (-57 mV).
# Es el Vm cuando no hay estimulación sonora, resultado del equilibrio
# entre la corriente MET de reposo y las corrientes de K⁺ basales.
resting_potential=-0.05703; #resting_potential at equilibrium
# peak_potential: Potencial máximo de la IHC a 100 dB SPL (-40 mV).
# Es el Vm cuando las fibras del nervio auditivo alcanzan saturación.
# A este voltaje, la tasa de liberación de neurotransmisor es máxima.
peak_potential=-0.04; #peak resting potential at 100 dB 4 kHz (where nerve fibers saturate)

def inner_hair_cell_potential(mu,fs):
    """
    Calcula el potencial de membrana (Vm) de la IHC en respuesta a la
    velocidad de la membrana basilar (mu).
    
    El modelo resuelve la ecuación diferencial del circuito eléctrico
    equivalente de la IHC paso a paso en el tiempo:
        Cm * dVm/dt = -(Imet + Ikf + Iks + Ileak)
    
    donde:
        Imet = Gmet * mt * (Vm - EP)     → corriente de transducción MET
        Ikf  = Gk * mkf * (Vm - Ekf)     → corriente de K⁺ rápida
        Iks  = Gk * mks * (Vm - Eks)     → corriente de K⁺ lenta
    
    Parámetros:
    -----------
    mu : array [tiempo x secciones_cocleares]
        Velocidad de la membrana basilar escalada (m/s × constante mágica).
        Actúa como proxy de la deflexión de estereocilios de la IHC.
    fs : float
        Frecuencia de muestreo (Hz)
    
    Retorna:
    --------
    Vsol : array [tiempo x secciones_cocleares]
        Potencial de membrana de la IHC (Voltios) a lo largo del tiempo
        para cada sección coclear simulada.
    """
    size=len(mu[0,:])
    fs=fs
    dt=1.0/fs
    # Factor de decaimiento exponencial para la dinámica del canal MET.
    # Modela la cinética de apertura/cierre del canal mecanosensible.
    alphaMet=exp(-dt/tauMet);
    a=zeros([size,2]);
    mt=zeros(size)
    # Factor de decaimiento para el canal de K⁺ rápido.
    alphakf1=exp(-dt/tkf1);
    # Factor de decaimiento para el canal de K⁺ lento.
    alphaks1=exp(-dt/tks1);
    # Vm inicializado en el potencial de reposo para todas las secciones.
    Vm=zeros([1,size])+resting_potential
    # mt: probabilidad de apertura del canal MET en reposo.
    # Función de doble Boltzmann evaluada en la deflexión de reposo (x0).
    mt=zeros([1,size])+1/(1+exp(x0/s0)*(1+exp(x0/s1)));
#    mt=zeros([1,size])+1/(1+exp(x0/s1));
    Vsol=zeros_like(mu,dtype=float)
    # mtIn: probabilidad de apertura instantánea del canal MET para cada
    # muestra de deflexión (mu). La deflexión real = x0 - mu (el estímulo
    # desvía los estereocilios desde su posición de reposo x0).
    # La función doble Boltzmann captura la asimetría de la transducción:
    # deflexiones positivas (hacia el kinocilio) abren más canales,
    # deflexiones negativas (opuestas) los cierran.
    mtIn=1/(1+exp((x0-mu)/s0)*(1+exp((x0-mu)/s1)));
    # Variables de activación de K⁺ inicializadas con los valores de reposo.
    mkf1=1/(1+exp(-(Vm-xk)/sk));
    mks1=1/(1+exp(-(Vm-xk)/sk));

    # ---- Fase de estabilización (50 ms sin estímulo) ----
    # Se deja que la IHC alcance un estado estacionario fisiológico
    # antes de aplicar el estímulo, para evitar artefactos transitorios.
    zero_time=int(fs*50e-3);
    for i in range(zero_time):
        # Corriente MET: flujo de iones K⁺/Ca²⁺ a través de los canales
        # mecanosensibles. Es negativa porque (Vm - EP) < 0 siempre
        # (el potencial endococlear es mucho más positivo que Vm).
        Imet=(Gmet*mt)*(Vm-EP);
        Ileak=Gleak*(Vm-Eca);
        # Activación instantánea del canal de K⁺ (función Boltzmann).
        mk=1/(1+exp(-(Vm-xk)/sk));
        # Filtrado temporal de la activación de K⁺:
        # mkf1 sigue a mk con constante de tiempo rápida (0.3 ms).
        mkf1=(1-alphakf1)*mk+alphakf1*mkf1;
        # mks1 sigue a mk con constante de tiempo lenta (8 ms).
        mks1=(1-alphaks1)*mk+alphaks1*mks1;
        Gkf=Gk*mkf1;
        Gks=Gk*mks1;
        # Corrientes de K⁺ repolarizantes (sacan K⁺ de la célula):
        Ikf=Gkf*(Vm-Ekf);
        Iks=Gks*(Vm-Eks);
        # Ecuación fundamental de la membrana: dV/dt = -ΣI / Cm
        dV=-(Ileak+Imet+Ikf+Iks)/Cm;
        # Integración de Euler (actualización del potencial de membrana):
        Vm=Vm+dV*dt;

    # ---- Simulación principal con estímulo ----
    # Aquí se procesa cada muestra temporal de la velocidad BM (mu):
    for i in range(len(mtIn[:,0])):
        # Actualización de la probabilidad de apertura del canal MET:
        # mt se filtra con constante de tiempo tauMet (50 µs) hacia
        # el valor instantáneo mtIn. Esto modela la cinética finita
        # de apertura/cierre del canal mecanosensible.
        mt=(1-alphaMet)*mtIn[i,:]+alphaMet*mt
        # Corriente de transducción MET: la corriente principal que
        # despolariza la IHC en respuesta al sonido.
        Imet=(Gmet*mt)*(Vm-EP);
        Ileak=Gleak*(Vm-Eca);
        # Activación y filtrado temporal de los canales de K⁺:
        mk=1/(1+exp(-(Vm-xk)/sk));
        mkf1=(1-alphakf1)*mk+alphakf1*mkf1;
        mks1=(1-alphaks1)*mk+alphaks1*mks1;
        Gkf=Gk*mkf1;
        Gks=Gk*mks1;
        Ikf=Gkf*(Vm-Ekf);
        Iks=Gks*(Vm-Eks);
        # Actualización del Vm con todas las corrientes del paso actual:
        dV=-(Ileak+Imet+Ikf+Iks)/Cm;
        Vm=Vm+dV*dt;
        # Almacenamiento del potencial de membrana para esta muestra temporal:
        Vsol[i,:]=Vm
    # print(Vsol)
    return Vsol





