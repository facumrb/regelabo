# =============================================================================
# SCRIPT DE ANÁLISIS: Visualización de Resultados de Simulación Auditiva
# =============================================================================
# Este script carga los resultados de una simulación con estímulo click
# (generada por ExampleSimulation.py) y genera 5 paneles de gráficos que
# permiten inspeccionar cada etapa del procesamiento auditivo:
#
#   1. Mapa tonotópico: frecuencias características (CF) de la cóclea
#   2. Emisión otoacústica (OAE): presión en el canal auditivo externo
#   3. Vibración BM y potencial IHC: mecánica coclear y transducción
#   4. Respuestas unitarias: fibras AN (HSR/MSR/LSR), CN e IC
#   5. Ondas poblacionales ABR: W1, W3, W5 y EFR
#
# Contexto clínico:
# Los gráficos de las ondas ABR (W1, W3, W5) son los equivalentes simulados
# de los potenciales evocados auditivos del tronco encefálico (PEATC) que
# se miden clínicamente con electrodos de superficie en el cuero cabelludo.
# =============================================================================
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy import signal
import os

# Carga los resultados de la simulación (archivo .mat generado previamente)
data = sio.loadmat('Simulations.mat')
output = data['output'][0]  # MATLAB struct becomes a structured array

# Condiciones de nivel del estímulo y presión de referencia audiológica
L = [0]
p0 = 2e-5  # 20 µPa: umbral de audición humana
# CF: frecuencias características de cada sección coclear simulada (Hz).
# Sigue el mapa tonotópico de Greenwood: altas freq en la base, bajas en el ápice.
CF = output['cf'].item().flatten()  # Manejar estructura de arrays anidados

# ---- Gráfico 1: Mapa tonotópico ----
# Muestra cómo las frecuencias características disminuyen exponencialmente
# a medida que nos movemos desde la base (sección 1) al ápice (sección N).
plt.figure()
plt.plot(CF)
plt.xlabel('Cochlear Channel Number [-]')
plt.ylabel('Characteristic Frequency [Hz]')
plt.title('Characteristic Frequencies')
plt.grid(True)
plt.show()

# Frecuencias de muestreo
fs_c = output['fs_bm'].item().item()  # Frecuencia de muestreo de BM, OAE e IHC (más alta para evitar errores numéricos)
fs = output['fs_an'].item().item()    # Frecuencia de muestreo de AN, CN, IC y ondas ABR (5 veces menor)

# Vectores temporales
t_c = np.arange(output['v'].item().shape[0]) / fs_c
t = np.arange(output['anfH'].item().shape[0]) / fs

# Vectores de frecuencia
f_c = np.arange(output['v'].item().shape[0]) * fs_c / output['v'].item().shape[0]
f = np.arange(output['anfH'].item().shape[0]) * fs / output['anfH'].item().shape[0]

# Seleccionar un número de canal coclear para graficar
No = 245

# Reorganización de datos para facilitar el procesamiento
num_conditions = len(L)
v_data = output['v'].item()
ihc_data = output['ihc'].item()
e_data = output['e'].item()

oae = np.zeros((e_data.shape[1], num_conditions))
vrms = np.zeros((v_data.shape[1], num_conditions))
ihcrms = np.zeros((ihc_data.shape[1], num_conditions))
v = np.zeros((v_data.shape[0], num_conditions))
ihc = np.zeros((ihc_data.shape[0], num_conditions))

for n in range(num_conditions):
    oae[:, n] = e_data.flatten()
    vrms[:, n] = np.sqrt(np.mean(v_data**2, axis=0))
    ihcrms[:, n] = np.sqrt(np.mean(ihc_data**2, axis=0))
    v[:, n] = v_data[:, No]
    ihc[:, n] = ihc_data[:, No]

# ---- Gráfico 2: Emisión Otoacústica (OAE) ----
# Biología: Las OAE son sonidos generados por la cóclea (principalmente
# por las OHC) que viajan de vuelta a través del oído medio y se pueden
# medir con un micrófono en el canal auditivo externo.
# Clínicamente se usan como prueba de integridad de las OHC (screening
# neonatal de sordera y detección de ototoxicidad).
#
# Panel superior: OAE en dominio temporal (presión vs tiempo)
# Panel inferior: Espectro de la OAE (magnitud vs frecuencia)
#   Para obtener la OAE de reflexión pura: OAE_{irr_on} - OAE_{irr_off}
#   Para la OAE de distorsión: normalizar con una simulación lineal
plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.plot(1000 * t_c, oae)
plt.xlabel('Time [ms]')
plt.ylabel('Ear Canal Pressure [Pa]')
plt.xlim([0, 20])
plt.ylim([-0.02, 0.02])
plt.legend([str(l) for l in L], frameon=False)
plt.title('OAE Time Domain')

# Zero padding para mejorar la resolución espectral de la FFT
oae_spectrum = oae.copy()
oae_spectrum[:200, :] = 0

plt.subplot(2, 1, 2)
oae_fft = np.fft.fft(oae_spectrum / p0, axis=0)
plt.plot(f_c / 1000, 20 * np.log10(np.abs(oae_fft)))
plt.xlabel('Frequency [kHz]')
plt.ylabel('EC Magnitude [dB re p0]')
plt.xlim([0, 12])
plt.legend([str(l) for l in L], frameon=False)
plt.title('OAE Frequency Domain')
plt.grid(True)
plt.tight_layout()
plt.show()

# ---- Gráfico 3: Velocidad BM y Potencial IHC ----
# Panel izquierdo superior: velocidad de la BM en una sección coclear específica.
#   La BM vibra en respuesta al sonido; la amplitud/fase de esta vibración
#   refleja la sintonización frecuencial de esa sección.
# Panel derecho superior: patrón de excitación (RMS de velocidad BM por CF).
#   Muestra qué secciones de la cóclea están más activas con el estímulo.
# Panel izquierdo inferior: potencial receptor de la IHC (transducción).
# Panel derecho inferior: patrón de excitación de la IHC.
plt.figure(figsize=(12, 10))

plt.subplot(2, 2, 1)
plt.plot(1000 * t_c, v)
plt.xlabel('Time [ms]')
plt.ylabel('v_{bm} [m/s]')
plt.xlim([0, 30])
plt.legend([str(l) for l in L], frameon=False)
plt.title(f'CF of {round(CF[No])} Hz')
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(CF / 1000, 20 * np.log10(vrms))
plt.xlabel('CF [kHz]')
plt.ylabel('rms of v_{bm} [dB re 1 m/s]')
plt.xlim([0, 14])
plt.ylim([np.max(20 * np.log10(vrms)) - 100, np.max(20 * np.log10(vrms)) + 10])
plt.title('Excitation Pattern')
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(1000 * t_c, ihc)
plt.xlabel('Time [ms]')
plt.ylabel('V_{ihc} [V]')
plt.xlim([0, 30])
plt.legend([str(l) for l in L], frameon=False)
plt.title(f'CF of {round(CF[No])} Hz')
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(CF / 1000, ihcrms)
plt.xlabel('CF [kHz]')
plt.ylabel('rms of V_{ihc} [V]')
plt.xlim([0, 14])
plt.title('Excitation Pattern')
plt.grid(True)

plt.tight_layout()
plt.show()

# Reorganización de datos para facilitar el procesamiento
anfH_data = output['anfH'].item()
anfM_data = output['anfM'].item()
anfL_data = output['anfL'].item()
an_summed_data = output['an_summed'].item()
cn_data = output['cn'].item()
ic_data = output['ic'].item()
w1_data = output['w1'].item()
w3_data = output['w3'].item()
w5_data = output['w5'].item()

HSR = np.zeros((anfH_data.shape[0], num_conditions))
MSR = np.zeros((anfM_data.shape[0], num_conditions))
LSR = np.zeros((anfL_data.shape[0], num_conditions))
AN = np.zeros((an_summed_data.shape[0], num_conditions))
CN = np.zeros((cn_data.shape[0], num_conditions))
IC = np.zeros((ic_data.shape[0], num_conditions))
W1 = np.zeros((w1_data.shape[1], num_conditions))  # Use shape[1] for wave data
W3 = np.zeros((w3_data.shape[1], num_conditions))
W5 = np.zeros((w5_data.shape[1], num_conditions))
EFR = np.zeros((w1_data.shape[1], num_conditions))

for n in range(num_conditions):
    HSR[:, n] = anfH_data[:, No]
    MSR[:, n] = anfM_data[:, No]
    LSR[:, n] = anfL_data[:, No]
    AN[:, n] = an_summed_data[:, No]
    CN[:, n] = cn_data[:, No]
    IC[:, n] = ic_data[:, No]
    W1[:, n] = w1_data.flatten()
    W3[:, n] = w3_data.flatten()
    W5[:, n] = w5_data.flatten()
    EFR[:, n] = w1_data.flatten() + w3_data.flatten() + w5_data.flatten()

# ---- Gráfico 4: Respuestas unitarias (una sección coclear) ----
# Muestra las tasas de disparo de cada tipo de fibra nerviosa y núcleo
# para una única sección coclear (CF específica).
#
# HSR: fibras de alta tasa espontánea (las primeras en responder, saturan rápido)
# MSR: fibras de media tasa espontánea (rango dinámico intermedio)
# LSR: fibras de baja tasa espontánea (solo responden a sonidos intensos)
# AN sumado: suma ponderada de todas las fibras (entrada al tronco encefálico)
# CN: salida del Núcleo Coclear (primera estación de relevo)
# IC: salida del Colículo Inferior (integración superior)
plt.figure(figsize=(12, 10))

plt.subplot(3, 2, 1)
plt.plot(1000 * t, HSR)
plt.title(f'CF of {round(CF[No])} Hz')
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('HSR fiber [spikes/s]')
plt.legend([str(l) for l in L], frameon=False)
plt.grid(True)

plt.subplot(3, 2, 3)
plt.plot(1000 * t, MSR)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('MSR fiber [spikes/s]')
plt.grid(True)

plt.subplot(3, 2, 5)
plt.plot(1000 * t, LSR)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('LSR fiber [spikes/s]')
plt.grid(True)

plt.subplot(3, 2, 2)
plt.plot(1000 * t, AN)
plt.title(f'CF of {round(CF[No])} Hz')
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('sum AN [spikes/s]')
plt.grid(True)

plt.subplot(3, 2, 4)
plt.plot(1000 * t, CN)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('CN [spikes/s]')
plt.grid(True)

plt.subplot(3, 2, 6)
plt.plot(1000 * t, IC)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('IC [spikes/s]')
plt.grid(True)

plt.tight_layout()
plt.show()

# ---- Gráfico 5: Respuestas poblacionales (ondas ABR) ----
# Estas son las ondas que se medirían con electrodos en el cuero cabelludo:
#   W1 (Onda I, µV): generada por el nervio auditivo (nervio VIII craneal)
#   W3 (Onda III, µV): generada por el núcleo coclear del tronco encefálico
#   W5 (Onda V, µV): generada por el colículo inferior (la más robusta)
#   EFR = W1 + W3 + W5: Envelope Following Response (respuesta total)
#
# Relevancia clínica:
# La Onda V es el marcador más usado en audiología para estimar umbrales
# auditivos en pacientes que no pueden cooperar (neonatos, UCI).
# Cambios en la latencia o amplitud de estas ondas pueden indicar
# neuropatía auditiva o pérdida auditiva retrococlear.
plt.figure(figsize=(10, 12))

plt.subplot(4, 1, 1)
plt.plot(1000 * t, 1e6 * W1)
plt.title('Population Responses summed across simulated CFs')
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('W-1 [μV]')
plt.legend([str(l) for l in L], frameon=False)
plt.grid(True)

plt.subplot(4, 1, 2)
plt.plot(1000 * t, 1e6 * W3)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('W-3 [μV]')
plt.grid(True)

plt.subplot(4, 1, 3)
plt.plot(1000 * t, 1e6 * W5)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('W-5 [μV]')
plt.grid(True)

plt.subplot(4, 1, 4)
plt.plot(1000 * t, 1e6 * EFR)
plt.xlim([0, 20])
plt.xlabel('Time [ms]')
plt.ylabel('EFR [μV]')
plt.grid(True)

plt.tight_layout()
plt.show()

print("Analysis complete!")