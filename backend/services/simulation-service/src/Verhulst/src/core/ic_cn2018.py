import numpy as np
from scipy import signal

# =============================================================================
# MÓDULO: NÚCLEOS DEL TRONCO ENCEFÁLICO (Cochlear Nuclei e Inferior Colliculus)
# =============================================================================
# Este archivo modela las dos estaciones neurales principales del tronco
# encefálico que procesan la información proveniente del nervio auditivo:
#   1) Núcleo Coclear (CN) — primera estación de relevo tras el nervio auditivo.
#   2) Colículo Inferior (IC) — estación superior que integra información
#      excitatoria e inhibitoria para refinar la codificación temporal.
#
# Biológicamente, estas estructuras reciben los potenciales de acción del
# nervio auditivo, los filtran temporalmente (excitación vs. inhibición con
# retardo) y generan las respuestas poblacionales que, al sumarse, producen
# las ondas del ABR (Auditory Brainstem Response):
#   - Onda I  (W1): generada por el nervio auditivo (AN sumado).
#   - Onda III (W3): generada por el núcleo coclear (CN).
#   - Onda V  (W5): generada por el colículo inferior (IC).
#
# Los factores de escala M1, M3, M5 convierten las tasas de disparo
# poblacionales (spikes/s) en amplitudes de voltaje (Voltios) medibles
# en el cuero cabelludo, calibrados para reproducir amplitudes típicas
# de potenciales evocados auditivos humanos (~0.1–0.5 µV).
# =============================================================================

# Factores de escala para convertir actividad neural en amplitud de onda ABR
# Estos valores fueron calibrados empíricamente para reproducir las amplitudes
# típicas de las ondas I, III y V del ABR humano medido con electrodos de superficie.
M1=4.2767e-14 
M3=5.1435e-14 
M5=13.3093e-14 

def cochlearNuclei(anfH,anfM,anfL,numH,numM,numL,fs):
    """
    Simula la respuesta del Núcleo Coclear (CN).
    
    Biología: El CN recibe aferencias directas del nervio auditivo.
    Cada célula ciliada interna (IHC) está inervada por fibras de alta (HSR),
    media (MSR) y baja (LSR) tasa de descarga espontánea. El CN suma estas
    contribuciones ponderadas por el número de fibras de cada tipo, y aplica
    un esquema de excitación-inhibición con retardo temporal, modelando
    las propiedades de "onset" y "chopper" de las neuronas del CN.
    
    Parámetros:
    -----------
    anfH, anfM, anfL : arrays con tasas de disparo de fibras HSR, MSR y LSR
    numH, numM, numL : número de fibras de cada tipo por IHC
    fs : frecuencia de muestreo (Hz)
    
    Retorna:
    --------
    cn : respuesta del núcleo coclear (spikes/s por sección coclear)
    summedAN : suma ponderada de todas las fibras del nervio auditivo
    """
    size=len(anfH[0,:])
    

    TF=19; #total no of fibers on each IHC
    # HSnormal=13;
    # MSnormal=3;
    # LSnormal=3;

    # Parámetros del modelo excitación-inhibición del CN:
    # Acn: ganancia excitatoria del CN (amplifica la señal AN entrante)
    # Scn: peso de la inhibición lateral (modula la respuesta para mejorar
    #      la codificación temporal, simulando interneuronas inhibitorias)
    Acn=1.5;
    Scn=0.6;
    # Retardo de inhibición: 1 ms. Biológicamente representa el tiempo extra
    # que tarda la señal al pasar por una interneurona inhibitoria antes de
    # llegar a la neurona principal del CN (vía polisináptica).
    inhibition_delay=int(round(1e-3*fs));
    # Constantes de tiempo de los filtros sinápticos:
    # Tex (0.5 ms): constante excitatoria rápida (sinapsis glutamatérgica directa)
    # Tin (2 ms): constante inhibitoria más lenta (sinapsis glicinérgica/GABAérgica)
    Tex=0.5e-3;
    Tin=2e-3;

    # Suma ponderada de las fibras del nervio auditivo (AN):
    # Cada IHC envía numH fibras HSR + numM fibras MSR + numL fibras LSR.
    # Esta suma representa la actividad total del nervio auditivo por sección coclear.
    summedAN=numL*anfL+numM*anfM+numH*anfH;

    summedAN=summedAN;
    # La inhibición opera sobre una versión retardada de la señal AN,
    # simulando el circuito neural polisináptico inhibitorio del CN.
    delayed_inhibition=np.zeros_like(summedAN)
    delayed_inhibition[inhibition_delay:,:]=summedAN[0:len(summedAN)-inhibition_delay,:]

    # Filtros de segundo orden obtenidos por transformada bilineal:
    # Estos filtros pasa-bajo modelan la dinámica temporal de las sinapsis.
    # # Filtro Excitatorio (rápido, Tex = 0.5 ms):
    m = (2*Tex*fs)
    a = (m-1)/(m+1)
    bEx = 1.0/(m+1)**2*np.array([1,2,1]); #numerator
    aEx = np.array([1, -2*a, a**2]); #denominator

    # # Filtro Inhibitorio (más lento, Tin = 2 ms):
    m = (2*Tin*fs)
    a = (m-1)/(m+1)
    bIncn = 1.0/(m+1)**2*np.array([1, 2, 1]); # numerator
    aIncn = np.array([1, -2*a, a**2]); # denominator

    # Respuesta del CN = Excitación directa - Inhibición retardada.
    # Esto implementa un modelo "chopper" simplificado donde la inhibición
    # lateral con retardo temporal refina la precisión de la codificación.
    cn=Acn*(signal.lfilter(bEx,aEx,summedAN,axis=0)-Scn*signal.lfilter(bIncn,aIncn,delayed_inhibition,axis=0))
    return cn,summedAN
             
def inferiorColliculus(cn,fs):
    """
    Simula la respuesta del Colículo Inferior (IC).
    
    Biología: El IC es la estación de integración más importante del tronco
    encefálico auditivo. Recibe la salida del CN y aplica un segundo nivel
    de procesamiento excitación-inhibición con un retardo mayor (2 ms),
    reflejando las vías polisinápticas más largas en esta estructura.
    
    La respuesta del IC genera la Onda V del ABR, que es el pico más robusto
    y clínicamente relevante de los potenciales evocados auditivos. Es el
    marcador más utilizado en audiología para estimar umbrales auditivos.
    
    Parámetros:
    -----------
    cn : salida del núcleo coclear (entrada al IC)
    fs : frecuencia de muestreo (Hz)
    
    Retorna:
    --------
    ic : respuesta del colículo inferior (spikes/s por sección coclear)
    """
    size=len(cn[0,:])
    # Mismas constantes de tiempo sinápticas que el CN
    Tex=0.5e-3;
    Tin=2e-3;
    # Aic: ganancia excitatoria del IC (menor que CN: integración más conservadora)
    # Sic: peso inhibitorio mayor que en CN (1.5 vs 0.6), reflejando la mayor
    #      inhibición lateral presente en el IC para mejorar la selectividad
    Aic=1;
    Sic=1.5;
    # Retardo de inhibición: 2 ms (el doble que el CN), reflejando la mayor
    # complejidad del circuito polisináptico inhibitorio del IC.
    inhibition_delay=int(round(2e-3*fs));

    delayed_inhibition=np.zeros_like(cn)
    delayed_inhibition[inhibition_delay:,:]=cn[0:len(cn)-inhibition_delay,:]

    # # Filtro Excitatorio:
    m = (2*Tex*fs)
    a = (m-1)/(m+1)
    bEx=1.0/(m+1)**2*np.array([1,2,1]); #numerator
    aEx=np.array([1, -2*a, a**2]); #denominator

    # # Filtro Inhibitorio:
    m = (2*Tin*fs)
    a = (m-1)/(m+1)
    bIncn = 1.0/(m+1)**2*np.array([1, 2, 1]); # numerator
    aIncn = np.array([1, -2*a, a**2]); # denominator

    # Respuesta del IC: mismo esquema excitación - inhibición retardada,
    # pero con inhibición más fuerte (Sic=1.5) simulando la convergencia
    # de múltiples vías inhibitorias en el colículo inferior.
    ic=Aic*(signal.lfilter(bEx,aEx,cn,axis=0)-Sic*signal.lfilter(bIncn,aIncn,delayed_inhibition,axis=0))
    return ic
