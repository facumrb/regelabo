import numpy as np
from scipy import signal

def get_RAM_stims(fs, fRAM):
    """
    Genera estímulos RAM (Rectangular Amplitude Modulation) para simulaciones
    auditivas y mediciones clínicas de EFR.
    
    Biología y contexto clínico:
    ----------------------------
    Los estímulos RAM son tonos portadores cuya amplitud es modulada por
    una onda cuadrada (rectangular) con ciclo de trabajo del 25%.
    
    ¿Por qué usar modulación de amplitud?
    Cuando el volumen de un sonido sube y baja periódicamente (a 110 Hz
    en este caso), las neuronas del sistema auditivo se sincronizan con
    ese ritmo y "disparan" impulsos al mismo compas. Esta sincronización
    genera una señal eléctrica detectable en el cuero cabelludo llamada
    EFR (Envelope Following Response).
    
    ¿Por qué rectangular (RAM) en vez de sinusoidal (SAM)?
    La modulación rectangular tiene flancos abruptos (subidas y bajadas
    instantáneas) que activan más neuronas simultáneamente, produciendo
    un EFR más robusto y fácil de medir clínicamente.
    
    Parámetros:
    -----------
    fs : float
        Frecuencia de muestreo [Hz]
    fRAM : array_like
        [Mx1] vector de frecuencias portadoras [Hz]
        M - número de estímulos a generar
    
    Retorna:
    --------
    stim : numpy.ndarray
        [MxN] matriz de los estímulos generados
        N - número de muestras en los estímulos
    
    Basado en: Sarineh Keshishzadeh 10.11.2021
    Adaptado por: Brent Nissens, Octubre 2025
    """
    
    # ---- Parámetros de referencia SAM ----
    # SAM (Sinusoidal Amplitude Modulation): tono de referencia para
    # calibrar la intensidad de los estímulos RAM.
    level = 70                    # Intensidad del estímulo [dB SPL]
    p0 = 20e-6                    # Presión de referencia audiológica [Pa] (20 µPa)
    fSAM = 4000                   # Frecuencia portadora del SAM de referencia [Hz]
    
    # ---- Parámetros del estímulo RAM ----
    fMod = 110                    # Frecuencia de modulación [Hz]: ritmo al que las
                                  # neuronas deberán sincronizarse (genera el EFR)
    md = 1                        # Profundidad de modulación (1 = 100%: silencio completo
                                  # entre los pulsos, máxima activación neural)
    phi = 3 * np.pi / 2           # Fase de la portadora [rad]
    dur = 0.4                     # Duración del estímulo [s]
    
    # Vector temporal
    n = round(dur * fs)
    tVec = np.arange(n) / fs
    
    # ---- Generación del tono SAM de referencia ----
    # Se usa para calibrar la amplitud: el RAM debe tener el mismo
    # nivel de presión sonora que este SAM de referencia.
    carrierSAM = np.sin(2 * np.pi * fSAM * tVec)
    modSAM = np.sin(2 * np.pi * fMod * tVec + phi)
    SAM = carrierSAM * (1 + md * modSAM)
    
    # Normalización por RMS para ajustar al nivel deseado en dB SPL
    SAM_rms = np.sqrt(np.mean(SAM**2))
    SAM = p0 * 10**(level/20) * SAM / SAM_rms
    
    # ---- Generación de estímulos RAM ----
    # La modulación rectangular (onda cuadrada al 25% de ciclo de trabajo)
    # produce pulsos breves de sonido seguidos de silencios, lo que genera
    # respuestas neurales más sincronizadas que la modulación sinusoidal.
    modRAM = signal.square(2 * np.pi * fMod * tVec + phi, duty=0.25)
    
    stim = np.zeros((len(fRAM), n))
    
    # Generar un estímulo RAM por cada frecuencia portadora solicitada
    for i in range(len(fRAM)):
        carrierRAM = np.sin(2 * np.pi * fRAM[i] * tVec)
        RAM = carrierRAM * (1 + md * modRAM)
        
        # Escalar el RAM para que tenga la misma amplitud pico que el SAM
        stim[i, :] = np.max(SAM) / np.max(RAM) * RAM
    
    return stim


if __name__ == "__main__":
    # Ejemplo de uso
    fs = 44100  # Frecuencia de muestreo
    fRAM = np.array([4000])  # Carrier frequencies
    
    stim = get_RAM_stims(fs, fRAM)
    print(f"Generated {stim.shape[0]} RAM stimuli with {stim.shape[1]} samples each")
    print(f"Sampling frequency: {fs} Hz")
    print(f"Carrier frequencies: {fRAM} Hz")