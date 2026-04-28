    # -*- coding: utf-8 -*-
# =============================================================================
# MÓDULO PRINCIPAL: MODELO MECÁNICO DE LA CÓCLEA (Cochlear Model 2018)
# =============================================================================
# Este archivo implementa el corazón del modelo de Verhulst et al. (2018):
# la simulación de la mecánica coclear completa.
#
# La cóclea se modela como una LÍNEA DE TRANSMISIÓN ACOPLADA de 1000
# secciones, donde cada sección representa una porción de ~35 µm de la
# membrana basilar (BM). Cada sección tiene su propia frecuencia de
# resonancia natural, desde ~20 kHz (base) hasta ~20 Hz (ápice),
# siguiendo el mapa tonotópico de Greenwood.
#
# Componentes físicos modelados:
#   1. OÍDO MEDIO: Cadena de huesecillos (martillo, yunque, estribo)
#      que transforma presión acústica en movimiento mecánico.
#   2. MEMBRANA BASILAR: Estructura elástica cuya rigidez varía a lo
#      largo de la cóclea (rígida en la base → flexible en el ápice).
#   3. FLUIDO COCLEAR: Perilinfa incompresible que acopla las secciones.
#   4. AMPLIFICADOR COCLEAR (OHC): Las células ciliadas externas (OHC)
#      aportan energía mecánica al sistema, amplificando las vibraciones
#      débiles y comprimiendo las fuertes (compresión no-lineal).
#   5. IRREGULARIDADES DE ZWEIG: Perturbaciones aleatorias en la BM que
#      generan reflexiones internas → emisiones otoacústicas (OAE).
#
# La ecuación diferencial se resuelve con un integrador Runge-Kutta
# adaptativo (dopri5), y el sistema tridiagonal resultante se resuelve
# con una rutina C optimizada (algoritmo de Thomas).
# =============================================================================
import numpy as np
import time
from scipy.integrate import ode
from scipy import signal
import ctypes
import os
import sys

# ---- Tipos de datos para la interfaz Python ↔ C (ctypes) ----
# Estas definiciones permiten pasar arrays de NumPy directamente a las
# funciones C compiladas, evitando copias de memoria innecesarias.
DOUBLE = ctypes.c_double
INT = ctypes.c_int
PINT = ctypes.POINTER(ctypes.c_int)
PLONG = ctypes.POINTER(ctypes.c_long)
PDOUBLE = ctypes.POINTER(ctypes.c_double)


# Estructura tridiagonal para la interfaz C: representa la matriz dispersa
# del acoplamiento fluídico entre las 1000 secciones cocleares.
class tridiag_matrix(ctypes.Structure):
    _fields_ = [("aa", ctypes.POINTER(ctypes.c_double)),
                ("bb", ctypes.POINTER(ctypes.c_double)),
                ("cc", ctypes.POINTER(ctypes.c_double))]

# Carga de la biblioteca C compilada que contiene los solucionadores numéricos
# optimizados (solve_tridiagonal y delay_line).
libName = 'tridiag.dll' if 'win32' in sys.platform else 'tridiag.so'
libtrisolv = np.ctypeslib.load_library(libName, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'c_lib'))

# Interfaz del solver tridiagonal (algoritmo de Thomas en C):
# Resuelve T·x = r donde T es la matriz de acoplamiento coclear.
libtrisolv.solve_tridiagonal.restype = None
libtrisolv.solve_tridiagonal.argtypes = [ctypes.POINTER(tridiag_matrix),  # aa
                                         PDOUBLE,  # vv
                                         PDOUBLE,  # solution
                                         INT,  # nrows
                                         ]

# Interfaz de la línea de retardo de Zweig (en C):
# Implementa las reflexiones cocleares internas con interpolación cúbica.
libtrisolv.delay_line.restype = None  # TODO SPEEDUP W POINTERS!
libtrisolv.delay_line.argtypes = [PDOUBLE,  # in_matrix
                                  PINT,  # delay1
                                  PINT,  # delay2
                                  PINT,  # delay1
                                  PINT,  # delay1
                                  PDOUBLE,  # dev
                                  PDOUBLE,  # YZweig
                                  INT,  # delay_buffer_length
                                  INT  # n
                                  ]

# =============================================================================
# FUNCIÓN PRINCIPAL DE LA ODE: TLsolver (Transmission Line Solver)
# =============================================================================
# Esta función calcula las derivadas temporales del sistema coclear.
# Es llamada repetidamente por el integrador ODE (dopri5/Runge-Kutta)
# en cada sub-paso temporal.
#
# El estado del sistema tiene 2*(N+1) variables:
#   y[0:N+1]   = V (velocidad de cada sección de la membrana basilar)
#   y[N+1:2N+2] = Y (desplazamiento de cada sección de la BM)
#
# La ecuación fundamental es la de una línea de transmisión:
#   dV/dt = Q - g    (aceleración = presión neta - amortiguamiento)
#   dY/dt = V        (desplazamiento = integral de velocidad)
#
# donde Q se obtiene resolviendo el sistema tridiagonal que acopla todas
# las secciones a través del fluido coclear, y g contiene las fuerzas
# de amortiguamiento y rigidez (incluyendo la amplificación de las OHC).
# =============================================================================


def TLsolver(t, y, model):  # y''=dv/dt y'=v
    n = model.n + 1
    # Fracción de interpolación temporal (para sub-pasos del integrador RK)
    frac = (t - model.lastT) / model.dt
    a = model.interplPoint1
    b = model.interplPoint2
    c = model.interplPoint3
    d = model.interplPoint4
    cminusb = c - b
    # Interpolación cúbica rápida del estímulo (presión sonora filtrada
    # por el oído medio) para obtener la fuerza F0 en el instante exacto
    # solicitado por el integrador adaptativo.
    F0 = b + frac * \
        (cminusb - 0.1666667 * (1. - frac) *
         ((d - a - 3.0 * cminusb) * frac + (d + 2.0 * a - 3.0 * b)))
    # Extraer velocidad (V) y desplazamiento (Y) de cada sección coclear
    model.Vtmp = y[0:n]
    model.Ytmp = y[n:2 * n]
    if(model.non_linearity):  # non-linearities here
        # ---- No-linealidad del amplificador coclear (OHC) ----
        # Cuando la vibración de la BM es intensa, las OHC saturan y
        # dejan de amplificar. Esto se modela desplazando los polos de
        # Shera hacia valores más altos (menos ganancia), implementando
        # la COMPRESIÓN COCLEAR (~0.2-0.4 dB/dB).
        # La función sigmoidal (hipérbola rotada) transforma la velocidad
        # BM instantánea en un ajuste del polo: a mayor vibración,
        # mayor polo → menor amplificación → compresión no-lineal.
        factor = 100
        Vvect = np.abs(model.Vtmp) / model.RthV1
        Sxp = (Vvect - 1.) * model.const_nl1
        Syp = model.Sb * np.sqrt(1 + (Sxp / model.Sa) ** 2)
        Sy = Sxp * model.sinTheta + Syp * model.cosTheta
        SheraP = model.PoleS + Sy / factor
        SheraP = np.fmin(SheraP, model.PoleE)
        # Optimización: solo recalcular los parámetros de Shera si el
        # cambio de polo supera el 1% (evita cálculos innecesarios).
        if(np.max(abs(SheraP[1:n] - model.SheraP[1:n]) /
           abs(model.SheraP[1:n])) > 0.01):
            model.SheraP = SheraP
            model.SheraParameters()
            model.ZweigImpedance()
            model.current_t = t
    # ---- Línea de retardo de Zweig (reflexiones cocleares → OAE) ----
    # Obtiene el desplazamiento BM retardado (YZweig) del buffer circular.
    # Este valor retardado se retroalimenta a la ecuación de la BM,
    # simulando las reflexiones internas que producen emisiones otoacústicas.
    model.Dev[0:n] = model.Dev[0:n] + frac
    libtrisolv.delay_line(
        model.Ybuffer_pointer, model.Zrp_pointer, model.Zrp1_pointer,
        model.Zrp2_pointer, model.Zrp3_pointer, model.Dev_pointer,
        model.YZweig_pointer, ctypes.c_int(model.YbufferLgt),
        ctypes.c_int(model.n + 1))
    model.Dev[0:n] = model.Dev[0:n] - frac
    # Calcular fuerzas de amortiguamiento+rigidez sobre cada sección BM
    model.calculate_g()
    # Ensamblar lado derecho del sistema tridiagonal
    model.calculate_right(F0)
    # ---- Resolver sistema tridiagonal T·Q = right ----
    # Q[i] = presión diferencial neta que actúa sobre la sección i de la BM.
    # Este es el paso más costoso computacionalmente y se ejecuta en C.
    libtrisolv.solve_tridiagonal(
        ctypes.byref(model.tridata), model.r_pointer, model.Qpointer,
        ctypes.c_int(n))
    # Condición de contorno en la base (estribo): la aceleración de la
    # sección 0 depende de la presión del fluido y la fuerza del estímulo.
    zero_val = (model.RK4_0*model.Qsol[0] + model.RK4G_0*(model.g[0] + model.p0x * F0))

    # Vector de derivadas: dV/dt = Q - g (aceleración = presión - amortiguamiento)
    Vderivative = (model.Qsol - model.g)
    Vderivative[0] = zero_val;
    # El vector solución tiene 2N componentes: [dV/dt, dY/dt] = [dV/dt, V]
    solution = np.concatenate([Vderivative, model.Vtmp])
    return solution


class cochlea_model ():
    """
    Modelo computacional completo de la cóclea humana.
    
    Simula la propagación de ondas viajeras a lo largo de la membrana
    basilar, incluyendo la amplificación activa por las células ciliadas
    externas (OHC), las irregularidades de Zweig, y la emisión otoacústica.
    """

    # ---- Constantes anatómicas y físicas de la cóclea humana ----
    def __init__(self):
        self.ttridiag = 0
        self.calling_function = 0
        # Longitud total de la cóclea humana: 35 mm (desenrollada)
        self.cochleaLength = .035
        # Masa por unidad de área de la membrana basilar (kg/m²)
        self.bmMass = 0.5
        self.bmImpedanceFactor = 1
        # Dimensiones de la scala (compartimentos llenos de perilinfa):
        # Ancho y alto de aproximadamente 1 mm cada uno.
        self.scalaWidth = 0.001
        self.scalaHeight = 0.001
        # Helicotrema: abertura en el ápice que conecta scala vestibuli
        # con scala tympani. Permite el paso de fluido a baja frecuencia.
        self.helicotremaWidth = 0.001
        # Densidad del fluido coclear (perilinfa ≈ agua, 1000 kg/m³)
        self.rho = float(1e3)
        # Factor de calidad Q normal de la sintonización coclear
        self.Normal_Q = 20
        # Parámetros del mapa tonotópico de Greenwood (1990):
        # f(x) = A * 10^(-alpha*x) - B
        # Relaciona la posición x en la cóclea con la frecuencia
        # característica (CF). A=20682, alpha=61.765, B=140.6 para humanos.
        self.Greenwood_A = 20682
        self.Greenwood_alpha = 61.765
        self.Greenwood_B = 140.6
        # Área de la platina del estribo: 3 mm² (interfaz oído medio → cóclea)
        self.stapesArea = float(3e-6)
        # Área del tímpano: 60 mm² (captura la presión sonora del canal auditivo)
        self.EardrumArea = float(60e-6)
        # Frecuencia de resonancia del oído medio: ~2 kHz
        self.MiddleEarResonanceFrequency = float(2e3)
        # Factor de calidad del oído medio (amortiguado, Q=0.4)
        self.MiddleEarQualityFactor = 0.4
        # Impedancia acústica específica del aire (415 Pa·s/m)
        self.SpecificAcousticImpedanceOfAir = 415
        # Relación de transformación del oído medio (ganancia de presión)
        self.middleEarTransformer = 30
        # Parámetros del acoplador acústico del canal auditivo
        self.damping_coupler = float(140e5)
        self.mass_coupler = float(43.2e2)
        self.stiffness_coupler = 1. / float(2.28e-11)
        # Presión de referencia audiológica: 20 µPa (umbral de audición)
        self.p0 = float(2e-5)
        # Parámetros de Zweig para el mecanismo de reflexión coclear:
        # ZweigQ: factor de calidad del resonador de Zweig
        # ZweigMuMax: retardo máximo (en ciclos) de la retroalimentación
        self.ZweigQ = 1 / 0.0606
        self.ZweigFactor = 1.7435
        self.ZweigQAtBoundaries = 20
        self.ZweigBeta = 10000
        self.ZweigGamma = 6200
        self.ZweigN = 1.5
        self.SheraMuMax = 3
        self.RMSref = 0.6124
        # Resistencia del oído medio (impedancia mecánica)
        self.Rme = float(0.3045192500000000e12)  # TODO setRme function
        #variable to check if the model is intialize before calling the solver
        self._is_init = 0
        # Puntos de interpolación para el estímulo (interpolación cúbica)
        self.interplPoint1 = 0
        self.interplPoint2 = 0
        self.interplPoint3 = 0
        self.interplPoint4 = 0

    # ---- Inicialización completa del modelo coclear ----
    # Configura todos los parámetros y subsistemas antes de la simulación:
    #   1. Polos de Shera (sheraPo): determinan el Q de cada sección coclear.
    #      Biológicamente representan la ganancia del amplificador coclear (OHC).
    #      Un polo mayor = mayor ganancia = mejor sintonización frecuencial.
    #   2. No-linealidad: tipo de compresión coclear (vel=velocidad, disp=desplazamiento).
    #   3. Irregularidades de Zweig: perturbaciones aleatorias que generan OAE.
    def init_model(self, stim, samplerate, sections, probe_freq, sheraPo,
                   compression_slope=0.4, Zweig_irregularities=1,
                   non_linearity_type='vel', KneeVar=1.,
                   low_freq_irregularities=1, subject=1,IrrPct=0.05):
        self.low_freq_irregularities = low_freq_irregularities
        # Polos de Shera: parte real de los polos del filtro coclear.
        # Controlan el factor de calidad (Q) y por tanto la selectividad
        # frecuencial de cada sección. Valores más altos = cóclea más sana.
        # La pérdida auditiva se modela aumentando estos polos (menos ganancia OHC).
        self.SheraPo = np.zeros(sections+1)
        self.SheraPo = self.SheraPo+sheraPo  # can be vector or single value, line changed so it can work with both single and vector
        self.KneeVar = (KneeVar)
        # IrrPct: magnitud de las irregularidades aleatorias en la BM (5% por defecto).
        # Estas micro-variaciones son las que generan emisiones otoacústicas.
        self.IrrPct = IrrPct
        # Tipo de no-linealidad del amplificador coclear (OHC):
        #   0 = lineal (sin amplificación activa, como una cóclea muerta)
        #   1 = basada en desplazamiento de la BM
        #   2 = basada en velocidad de la BM (modelo por defecto)
        self.non_linearity = 0
        self.use_Zweig = 1
        if(Zweig_irregularities == 0):
            self.use_Zweig = 0
        if(non_linearity_type == 'disp'):
            self.non_linearity = 1
        elif(non_linearity_type == 'vel'):
            self.non_linearity = 2
        else:
            self.non_linearity = 0  # linear model
        self.n = sections
        self.fs = samplerate
        self.dt = 1. / self.fs
        self.probe_freq = probe_freq
        # Secuencia de inicialización de los subsistemas cocleares:
        self.initCochlea()              # Geometría y discretización espacial
        self.initMiddleEar()            # Parámetros del oído medio
        self.SetDampingAndStiffness()    # Mapa tonotópico y polos de Shera
        self.initZweig()                # Buffer de retardo para reflexiones
        self.initGaussianElimination()   # Matriz tridiagonal del acoplamiento
        self.compression_slope_param(compression_slope)  # Curva de compresión
        self.is_init = 1
        self.lastT = 0
        self.seed = subject  # change here the seed
        np.random.RandomState(self.seed)
        np.random.seed(self.seed)
        self.Rth = 2 * (np.random.random(self.n + 1) - 0.5)
        self.Rth_norm = 10 ** (self.Rth / 20. / self.KneeVar)
        lf_limit = self.ctr
        if(self.use_Zweig==0):
            lf_limit=0
            print('No irregularities')
        factor = 100
        n = self.n + 1
        Rth = self.Rth
        Rth_norm = self.Rth_norm
        #Normalized RTH, so save a bit of computation
        self.RthY1 = self.Yknee1 * Rth_norm
        self.RthY2 = self.Yknee2 * Rth_norm
        self.RthV1 = self.Vknee1 * Rth_norm
        self.RthV2 = self.Vknee2 * Rth_norm

        Rndm = self.IrrPct * Rth / 2.
        self.PoleS = (1 + Rndm) * self.SheraPo

        self.RthY1[lf_limit:n] = self.Yknee1
        self.RthY2[lf_limit:n] = self.Yknee2
        self.RthV1[lf_limit:n] = self.Vknee1
        self.RthV2[lf_limit:n] = self.Vknee2
        self.PoleS[lf_limit:n] = self.SheraPo[lf_limit:n]
        Theta0 = np.arctan(
            ((self.PoleE - self.PoleS) * factor) /
            ((self.RthV2 / self.RthV1) - 1.))
        Theta = Theta0 / 2.
        Sfoc = (self.PoleS * factor) / (self.RthV2 / self.RthV1)
        Se = np.cos((np.pi - Theta0) * 0.5)
        self.Sb = Sfoc * Se
        self.Sa = Sfoc * np.sqrt(1. - ((Se ** 2)))
        self.const_nl1 = np.cos(Theta) / np.cos(2 * Theta)
        self.cosTheta = np.cos(Theta)
        self.sinTheta = np.sin(Theta)

        #
        # PURIAM1 FILTER             ###
        #
        puria_gain = 10 ** (18. / 20.)
#         was the orignal Puria in 2012
#        second order butterworth
#        b, a = signal.butter(
#           1, [100. / (samplerate / 2.), 3000. / (samplerate / 2)],
#            'bandpass')
#         self.stim = signal.lfilter(b * puria_gain, a, stim)


        b, a = signal.butter(1, [600 / (samplerate / 2.), 4000. / (samplerate / 2)],'bandpass')
        self.stim = signal.lfilter(b * puria_gain, a, stim)

    # ---- Inicialización de la geometría coclear ----
    # Discretiza la cóclea en N+1 secciones equiespaciadas y calcula
    # los parámetros geométricos de la línea de transmisión.
    def initCochlea(self):
        # Longitud efectiva de la membrana basilar (excluyendo helicotrema)
        self.bm_length = self.cochleaLength - self.helicotremaWidth
        self.bm_width = self.scalaWidth
        self.bm_mass = self.bmMass * self.bmImpedanceFactor
        # ZweigMso: masa acústica serie del fluido coclear por unidad de longitud.
        # Depende de la densidad del fluido y las dimensiones de la scala.
        self.ZweigMso = 2. * self.rho / (self.bm_width * self.scalaHeight)
        # ZweigL: constante espacial derivada del mapa de Greenwood
        self.ZweigL = 1. / (2.3030 * self.Greenwood_alpha)
        # Frecuencia angular de corte (frecuencia máxima en la base coclear)
        self.ZweigOmega_co = 2.0 * np.pi * self.Greenwood_A-self.Greenwood_B
        # ZweigMpo: masa acústica paralelo de la partición coclear
        self.ZweigMpo = (
            self.ZweigMso * (self.ZweigL ** 2)) / ((4 * self.ZweigN) ** 2)
        # Ko: rigidez de la BM en la base (máxima rigidez)
        self.Ko = self.ZweigMpo * (self.ZweigOmega_co ** 2)
        # x: posiciones a lo largo de la membrana basilar (0=base, bm_length=ápice)
        self.x =np.array(np.linspace(0, self.bm_length, self.n+1), order='C') #Old
        # dx: separación entre secciones cocleares (~35 µm para 1000 secciones)
        self.dx = self.bm_length / (1. * self.n)
        # Vectores de estado para cada sección coclear:
        self.g = np.zeros_like(self.x)      # fuerzas de amortiguamiento+rigidez
        self.Vtmp = np.zeros_like(self.x)    # velocidad BM temporal
        self.Ytmp = np.zeros_like(self.x)    # desplazamiento BM temporal
        self.Atmp= np.zeros_like(self.x)     # aceleración BM temporal
        self.right = np.zeros_like(self.x)   # lado derecho del sistema tridiagonal
        self.r_pointer = self.right.ctypes.data_as(PDOUBLE)
        self.zerosdummy = np.zeros_like(self.x)
        self.gamma = np.zeros_like(self.x)
        self.Qsol = np.zeros_like(self.x)    # solución del sistema tridiagonal (presión)
        self.Qpointer = self.Qsol.ctypes.data_as(PDOUBLE)

    # ---- Inicialización del oído medio ----
    # Calcula los factores de acoplamiento entre el oído medio y la cóclea.
    # El oído medio actúa como un transformador de impedancia que convierte
    # la presión sonora del aire (baja impedancia) en presión del fluido
    # coclear (alta impedancia), maximizando la transferencia de energía.
    def initMiddleEar(self):
        self.q0_factor = self.ZweigMpo * self.bm_width
        # p0x: factor de acoplamiento presión-fluido entre secciones
        self.p0x = self.ZweigMso * self.dx/(1. * self.ZweigMpo * self.bm_width)
        # d_m_factor: factor de amortiguamiento del oído medio
        self.d_m_factor = -self.p0x * self.stapesArea * self.Rme
        # RK4_0 y RK4G_0: factores para la condición de contorno en la base
        # (interfaz estribo-cóclea). Acoplan el movimiento del estribo con
        # la presión del fluido coclear en la sección 0.
        self.RK4_0 = -(self.bm_width * self.ZweigMpo) / (self.stapesArea)
        self.RK4G_0 = (self.ZweigMpo * self.bm_width) / (
            self.ZweigMso * self.stapesArea * self.dx)

    # ---- Mapa Tonotópico y Parámetros de Amortiguamiento ----
    # Calcula la frecuencia de resonancia natural de cada sección coclear
    # usando la función de Greenwood: f(x) = A*10^(-αx) - B.
    # Biológicamente, la rigidez de la membrana basilar decrece exponencialmente
    # desde la base (rígida, altas frecuencias) al ápice (flexible, bajas freq).
    # También inicializa los parámetros de Shera que controlan el Q de cada
    # sección (la agudeza de sintonización proporcionada por las OHC).
    def SetDampingAndStiffness(self):
        # Mapa de Greenwood: frecuencia característica (CF) de cada sección
        self.f_resonance = self.Greenwood_A * \
            10 ** (-self.Greenwood_alpha * self.x) - self.Greenwood_B
        # ctr: sección por debajo de la cual no hay irregularidades (100 Hz)
        self.ctr = np.argmin(np.abs(self.f_resonance - 100.))
        if(self.low_freq_irregularities):
            self.ctr = self.n + 1
        # onek: índice de la sección con CF = 1 kHz (referencia para normalización)
        self.onek = np.argmin(np.abs(self.f_resonance - 1000.))
        # Frecuencias angulares de resonancia para cada sección
        self.omega = 2. * np.pi * self.f_resonance
        self.omega[0]=self.ZweigOmega_co
        self.omega2 = self.omega ** 2
        # Parámetros de Shera: controlan el amortiguamiento (D), retardo (µ),
        # y retroalimentación (ρ) del amplificador coclear en cada sección.
        self.Sherad_factor = np.array(self.omega)
        self.SheraP = np.zeros_like(self.x)    # polo actual (parte real)
        self.SheraD = np.zeros_like(self.x)    # amortiguamiento derivado del polo
        self.SheraRho = np.zeros_like(self.x)  # ganancia de retroalimentación de Zweig
        self.SheraMu = np.zeros_like(self.x)   # retardo de Zweig (en ciclos)
        self.SheraP = self.SheraPo + self.SheraP
        self.c = 120.8998691636393

        #
        # PROBE POINTS               ##
        #
        if(self.probe_freq=='all'):
            self.probe_points=np.zeros(len(self.f_resonance)-1)
            for i in range(len(self.f_resonance)-1):
                self.probe_points[i]=i+1
            self.probe_points=(self.probe_points)
            self.cf=(self.f_resonance[1:len(self.f_resonance)])
        elif(self.probe_freq=='half'):
            self.probe_points=np.zeros((len(self.f_resonance)-1)/2)
            for i in range((len(self.f_resonance)-1)/2):
                self.probe_points[i]=i+1
            self.probe_points=(self.probe_points)
            self.cf=(self.f_resonance[range(1,len(self.f_resonance),2)])
        elif(self.probe_freq=='abr'):
            #            self.probe_points=np.zeros([401,1])
            self.probe_points=np.array(range(110,911,2))
            self.cf=(self.f_resonance[range(110,911,2)])
#            print(np.shape(self.probe_points))
#            print('abr')
        else:
            self.probe_points=np.zeros(self.probe_freq.size,dtype=int)
            for i in range(len(self.probe_freq)):
                idx_help=abs((self.f_resonance)-np.float(self.probe_freq[i]))
                self.probe_points[i]=np.argmin(idx_help)
            self.cf=self.f_resonance[self.probe_points]
        self.probe_points=np.array(self.probe_points)
#        print(np.shape(self.probe_points))


    # ---- Inicialización del mecanismo de Zweig (reflexiones cocleares) ----
    # El modelo de Zweig simula cómo las irregularidades microscópicas en la
    # membrana basilar generan reflexiones parciales de la onda viajera.
    # Estas reflexiones viajan de vuelta a la base y se emiten como
    # EMISIONES OTOACÚTICAS (OAE) a través del oído medio.
    # Implementado como un buffer circular con interpolación cúbica.
    def initZweig(self):
        n = self.n + 1
        # Retardo exacto de Zweig: número de muestras que tarda la onda
        # reflejada en completar su recorrido de ida y vuelta.
        self.exact_delay = self.SheraMuMax / (self.f_resonance * self.dt)
        self.delay = np.floor(self.exact_delay) + 1
        # Buffer circular: almacena el historial de desplazamientos BM
        # necesario para calcular la retroalimentación retardada.
        self.YbufferLgt = int(np.amax(self.delay)) #quick fix, maybe can be shorter but it works so better not touch
        self.Ybuffer = np.zeros([n, self.YbufferLgt])
                                # Ybuffer implemented here as a dense matrix
                                # (python for cycles are slow...)
        self.Ybuffer = np.array(self.Ybuffer, order='C', ndmin=2, dtype=float)
        self.Ybuffer_pointer = self.Ybuffer.ctypes.data_as(PDOUBLE)
        self.ZweigSample1 = np.zeros_like(self.exact_delay)
        self.Zwp = int(0)  # puntero circular del buffer
        self.ZweigSample1[0] = 1.
        self.ZweigSample2 = self.ZweigSample1 + 1
        # Vectores auxiliares para la interpolación cúbica en la línea de retardo:
        # Dev: fracción sub-muestral del retardo
        # YZweig: desplazamiento BM retardado (salida de la línea de retardo)
        # Zrp0-3: índices de los 4 puntos para interpolación cúbica
        self.Dev = np.zeros_like(self.x)
        self.Dev_pointer = self.Dev.ctypes.data_as(PDOUBLE)
        self.YZweig = np.zeros_like(self.x)
        self.YZweig_pointer = self.YZweig.ctypes.data_as(PDOUBLE)
        self.Zrp = np.array(np.zeros(n), dtype=np.int32, order='C')
        self.Zrp_pointer = self.Zrp.ctypes.data_as(PINT)
        self.Zrp1 = np.array(np.zeros(n), dtype=np.int32, order='C')
        self.Zrp1_pointer = self.Zrp1.ctypes.data_as(PINT)
        self.Zrp2 = np.array(np.zeros(n), dtype=np.int32, order='C')
        self.Zrp2_pointer = self.Zrp2.ctypes.data_as(PINT)
        self.Zrp3 = np.array(np.zeros(n), dtype=np.int32, order='C')
        self.Zrp3_pointer = self.Zrp3.ctypes.data_as(PINT)

    # ---- Construcción de la Matriz Tridiagonal ----
    # Ensambla los coeficientes de la matriz tridiagonal que representa
    # el acoplamiento fluídico entre secciones cocleares adyacentes.
    # Esta matriz se resuelve en cada paso temporal con el algoritmo de Thomas.
    # Los coeficientes ZAL (sub-diagonal), ZASC (diagonal), ZAH (super-diagonal)
    # dependen de las masas acústicas serie (ZweigMs) y la geometría coclear.
    def initGaussianElimination(self):
        n = self.n + 1
        self.ZweigMs = (self.ZweigMso * self.ZweigOmega_co) / self.omega # TAPERING self.omega*
        self.ZweigMp = self.Ko / (self.ZweigOmega_co * self.omega)
        #self.ZweigMs = self.ZweigMs/ self.omega[1]
        #self.ZweigMp = self.ZweigMp/self.omega[1]
        self.ZASQ = np.zeros_like(self.x)
        self.ZASC = np.zeros_like(self.x)
        self.ZAL = np.zeros_like(self.x)
        self.ZAH = np.zeros_like(self.x)
        # init values of transimission line
        self.ZASQ[0] = 1.
        self.ZASC[0] = 1 + self.ZweigMso * self.dx
        self.ZAH[0] = -1*self.ZweigOmega_co/self.omega[1]
        self.ZAL[1:n] = -self.ZweigMs[1:n]*self.omega[1:n]/self.omega[0:n-1]
        self.ZAH[1:n-1] =-self.ZweigMs[0:n-2]*self.omega[1:n-1]/self.omega[2:n]
#        self.ZAH[0] = -1.
#        self.ZAL[1:n] = -self.ZweigMs[1:n]
#        self.ZAH[1:n - 1] = -self.ZweigMs[0:n - 2]
        self.ZASQ[1:n] = self.omega[1:n] * self.ZweigMs[1:n] * self.ZweigMs[0:n - 1] * (self.dx ** 2) / (self.ZweigOmega_co *self.ZweigMpo)
        self.ZASC[1:n] = self.ZASQ[1:n] +self.ZweigMs[1:n] + self.ZweigMs[0:n - 1]
        self.tridata = tridiag_matrix()
        self.tridata.aa = self.ZAL.ctypes.data_as(PDOUBLE)
        self.tridata.bb = self.ZASC.ctypes.data_as(PDOUBLE)
        self.tridata.cc = self.ZAH.ctypes.data_as(PDOUBLE)

    # ---- Cálculo de fuerzas sobre la membrana basilar ----
    # g[i] = amortiguamiento * velocidad + rigidez * desplazamiento
    # g[0] = fuerza del oído medio sobre el estribo (condición de contorno)
    # El término SheraRho * YZweig incorpora la retroalimentación de Zweig
    # (onda reflejada que vuelve a excitar la sección coclear).
    def calculate_g(self):  # same as in fortran
        n = self.n + 1
        self.g[0] = self.d_m_factor * self.Vtmp[0]
        dtot = self.Sherad_factor * self.SheraD
        stot = (self.omega2) * (self.Ytmp + (self.SheraRho * self.YZweig))
        self.g[1:n] = (dtot[1:n] * self.Vtmp[1:n]) + stot[1:n]

    # Ensambla el lado derecho del sistema tridiagonal T·Q = right
    def calculate_right(self, F0):  # same as in fortran
        n = self.n + 1
        self.right[0] = self.g[0] + self.p0x * F0
        self.right[1:n] = self.ZASQ[1:n] * self.g[1:n]

    # ---- Parámetros de Shera (amplificador coclear OHC) ----
    # Convierte el polo de Shera (SheraP) en los parámetros físicos:
    #   SheraD: amortiguamiento (negativo = amplificación activa por OHC)
    #   SheraMu: retardo de la retroalimentación (en ciclos de CF)
    #   SheraRho: ganancia de la onda reflejada de Zweig
    # Estos parámetros controlan la amplificación coclear y la selectividad
    # frecuencial. Un polo pequeño = más amplificación = mejor Q.
    def SheraParameters(self):  # same as in fortran
        a = (self.SheraP + np.sqrt((self.SheraP ** 2.) +
             self.c * (1.0 - self.SheraP ** 2))) / self.c
        self.SheraD = 2.0 * (self.SheraP - a)
        self.SheraMu = 1. / (2.*np.pi*a)
        self.SheraRho = 2. * a * \
            np.sqrt(1. - (self.SheraD / 2.) ** 2.) * np.exp(-self.SheraP / a)

    # ---- Impedancia de Zweig (actualiza índices de la línea de retardo) ----
    # Recalcula los índices del buffer circular para la interpolación cúbica
    # basándose en el retardo actual de Zweig (SheraMu).
    def ZweigImpedance(self):
        n = self.n + 1
        MudelayExact =(2*np.pi)*self.SheraMu / (self.omega * self.dt)
        Mudelay = np.floor(MudelayExact) + 1.
        self.Dev[:] = Mudelay - MudelayExact
        self.Zrp1[0:n] = (
            (self.Zwp + self.YbufferLgt) - Mudelay[0:n]) % self.YbufferLgt
        const = self.YbufferLgt - 1
        self.Zrp[0:n] = (self.Zrp1[0:n] + const) % self.YbufferLgt
        self.Zrp2[0:n] = (self.Zrp1[0:n] + 1) % self.YbufferLgt
        self.Zrp3[0:n] = (self.Zrp2[0:n] + 1) % self.YbufferLgt

    def compression_slope_param(self, slope):
        self.Yknee1 = float(1.0*(6.9183e-10))
#self.Yknee1 = float(2.0*(6.9183e-10))
        self.Yknee2 = float(1.5488e-8)
    #    #       THdB=10.0 #SARAH's Style
#        THdB=10.0
#        Ax=1
#        Bx=20*np.log10(8.461e-11)
#        Vknee1 = float(1.0*(2.293e-7))
#        self.PoleE = np.zeros_like(self.x)+0.3
#        BoffsetV=-slope*THdB+20*np.log10(Vknee1) #find the offset of the compression curves
#        Vint=(Bx-BoffsetV)/(slope-Ax) #is the intersection in dB on xaxis
#        Vknee2=Ax*Vint+Bx #what it corresponds to in dB on y axis
#        self.Vknee2=10.0 ** (Vknee2/20.0)
#        self.Vknee1=Vknee1

#       Ale Style
        self.PoleE = np.zeros_like(self.x)+0.31 #saturating pole
        v1=0.6807e-08/3/np.sqrt(2); # velocity at -10 dB with starting Pole
        v2=26.490e-11/3/np.sqrt(2); # velocity at -10 dB with saturating pole
        K1dB=20; # Knee point of the first linear regime in dB (you can select it from here now)
        #but it does not work precisely for K1dB<20...?? So, by using v1 and v2 peak velocities at -10 dB it is possible to impose the desired Knee down to 10 dB.
        K1dB=K1dB+20; #fix for the -10 dB of v1 and v2
        K1L=10**(K1dB/20) #knee point in linear scale
        self.Vknee1=K1L*v1
        vst1dB=20*np.log10(v1)+K1dB #velocity with the two poles when the compression starts
        vst2dB=20*np.log10(v2)+K1dB
        K2dB=(vst1dB-vst2dB)/(1-slope) #intersection in dB re Knee 1
        self.Vknee2=v2*10**(K2dB/20)*K1L
    
    def polecalculation(self):  # TODO

        factor = 100.
        # lf_limit = self.ctr
        # n = self.n + 1
        if(self.non_linearity == 1):  # To check
            # non-linearity DISP cost about three times more than in
            # fortran (Not implemented now)
            Yknee1CST = self.RthY1 * self.omega[self.onek]
            Yknee2CST = self.RthY2 * self.omega[self.onek]
            Yknee1F = Yknee1CST / self.omega
            Yknee2F = Yknee2CST / self.omega
            Yvect = np.abs(self.Ytmp / Yknee1F)
            Theta0 = np.arctan(
                ((self.PoleE - self.PoleS) / ((Yknee2F / Yknee1F) - 1.)))
            Theta = Theta0 / 2.
            # save 2 call to trigonometric function on vector by storing
            # some data
            cos_Theta = np.cos(Theta)
            sin_Theta = np.sin(Theta)
            cos_Theta0 = 2 * cos_Theta ** 2 - 1
            Sfoc = self.PoleS * factor * (Yknee2F / Yknee1F)
            Se = sin_Theta
            Sb = Sfoc * Se
            Sa = Sfoc * np.sqrt(1. - (1. * (Se ** 2)))
            Sxp = (Yvect - 1.) * cos_Theta / cos_Theta0
            Syp = Sb * np.sqrt(1 + (Sxp / Sa) ** 2)
            Sy = Sxp * sin_Theta + Syp * cos_Theta
            self.SheraP = self.PoleS + Sy / factor

        elif(self.non_linearity == 2):  # non-linearity VEL
            Vvect = np.abs(self.Vtmp) / self.RthV1
            Sxp = (Vvect - 1.) * self.const_nl1
            Syp = self.Sb * np.sqrt(1 + (Sxp / self.Sa) ** 2)
            Sy = Sxp * self.sinTheta + Syp * self.cosTheta
            self.SheraP = self.PoleS + Sy / factor
        else:
            print('linear')
            self.SheraP = self.PoleS
        self.SheraP = np.fmin(self.SheraP, self.PoleE)

    # ================================================================
    # SOLVER PRINCIPAL: Integración temporal de la mecánica coclear
    # ================================================================
    # Resuelve la ecuación diferencial de la línea de transmisión coclear
    # paso a paso en el tiempo usando un integrador Runge-Kutta adaptativo
    # (dopri5). En cada paso temporal:
    #   1. Interpola el estímulo de entrada (presión sonora filtrada por
    #      el oído medio) con interpolación cúbica para precisión.
    #   2. Llama a TLsolver() que calcula las derivadas del sistema.
    #   3. Actualiza el buffer circular de Zweig con el nuevo desplazamiento.
    #   4. Almacena velocidad (V) y desplazamiento (Y) de la BM en los
    #      puntos de sondeo (probe points) seleccionados.
    #   5. Registra la emisión otoacústica (presión en la sección 0).
    #
    # Al finalizar, filtra la emisión otoacústica con el mismo filtro
    # del oído medio para obtener la presión en el canal auditivo externo.
    # ================================================================
    def solve(self):
        n = self.n + 1
        tstart = time.time()
        if not(self.is_init):
            print("Error: model to be initialized")
        length = np.size(self.stim) - 2
        time_length = length * self.dt
        # Matrices de salida: almacenan V (velocidad) e Y (desplazamiento)
        # de la BM solo en los puntos de sondeo seleccionados (probe_points).
        self.Vsolution = np.zeros([length + 2, len(self.probe_points)])
        self.Ysolution = np.zeros([length + 2, len(self.probe_points)])
        self.Asolution= np.zeros([length + 2, len(self.probe_points)])
        # Emisión otoacústica: presión en la sección 0 (base coclear/estribo)
        self.oto_emission = np.zeros(length + 2)
        self.time_axis = np.linspace(0, time_length, length)
        # Integrador Runge-Kutta adaptativo de 5° orden (Dormand-Prince):
        # Resuelve la ODE del sistema coclear con tolerancias que balancean
        # precisión numérica y velocidad computacional.
        r = ode(TLsolver).set_integrator('dopri5', rtol=1e-2, atol=1e-13)
        r.set_f_params(self)
        # Estado inicial: todo en reposo (V=0, Y=0 para todas las secciones)
        r.set_initial_value(
            np.concatenate([np.zeros_like(self.x), np.zeros_like(self.x)]))
        r.t = 0
        j = 0
        self.last_t = 0.0
        self.current_t = r.t
        # Calcular los polos iniciales de Shera (perfil de no-linealidad)
        self.polecalculation()
        self.SheraParameters()
        self.ZweigImpedance()
        self.V1=np.zeros_like(self.x)
        # ---- Bucle principal de integración temporal ----
        # Avanza la simulación muestra por muestra (~100,000 pasos por segundo).
        while(j < length):
            if(j > 0):
                self.interplPoint1 = self.stim[j - 1]
            # Asignar los 4 puntos del estímulo para interpolación cúbica
            self.interplPoint2 = self.stim[j]
            self.interplPoint3 = self.stim[j + 1]
            self.interplPoint4 = self.stim[j + 2]
            # Integrar un paso temporal (dt) — llama a TLsolver internamente
            r.integrate(r.t + self.dt)
            self.lastT = r.t
            # Extraer velocidad (V1) y desplazamiento (Y1) del resultado
            self.V1 = r.y[0:n]
            self.V1[0]=self.Vtmp[0]
            self.Y1 = r.y[n:2 * n]  # No-linealidades se aplican AQUÍ
            self.Atmp=self.Qsol-self.g
            # Actualizar buffer circular de Zweig con el desplazamiento actual
            self.Zwp = (self.Zwp + 1) % self.YbufferLgt  # update Zweig Buffer
            self.Ybuffer[:, self.Zwp] = self.Y1
            self.ZweigImpedance()
            self.current_t = r.t
            # Almacenar resultados en los probe points seleccionados
            if(self.probe_freq=='all'):
                self.Vsolution[j,:] = self.V1[1:n]  #
                self.Ysolution[j,:] = self.Y1[1:n]
            elif(self.probe_freq=='half'):
                self.Vsolution[j,:]=self.V1[range(1,n,2)]
                self.Ysolution[j,:] = self.Y1[range(1,n,2)]
            elif(self.probe_freq=='abr'):
               self.Vsolution[j,:]=self.V1[range(110,911,2)]
               self.Ysolution[j,:] = self.Y1[range(110,911,2)]
            else:
                self.Vsolution[j,:] = self.V1[self.probe_points]  # almacenar los puntos de sondeo seleccionados
                self.Ysolution[j,:] = self.Y1[self.probe_points]
            # La presión en la sección 0 (Qsol[0]) es la emisión otoacústica
            # antes de ser filtrada por el oído medio.
            self.oto_emission[j] = self.Qsol[0]
            j = j + 1
    # ---- Filtrado de la emisión otoacústica ----
    # La OAE cruda se filtra con el mismo filtro bandpass del oído medio
    # (600-4000 Hz) para obtener la presión que se mediría en el canal
    # auditivo externo con un micrófono real.
        samplerate = self.fs
        b, a = signal.butter(1, [600 / (samplerate / 2.), 4000. / (samplerate / 2)],'bandpass')
        self.oto_emission = signal.lfilter(b * self.q0_factor, a, self.oto_emission)
        elapsed = time.time() - tstart
#        print(elapsed)
# END
