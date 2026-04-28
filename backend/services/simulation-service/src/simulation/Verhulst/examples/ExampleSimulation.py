#!/usr/bin/env python3
"""
=============================================================================
EJEMPLO DE SIMULACIÓN: Interfaz simplificada para el modelo Verhulst 2018
=============================================================================
Este script proporciona una interfaz fácil de usar para ejecutar el modelo
completo de la periferia auditiva y calcular el EFR (Envelope Following Response).

Pipeline completo:
  1. Genera un estímulo RAM (Rectangular Amplitude Modulation) automáticamente
  2. Carga el perfil auditivo (polos de Shera) desde un archivo .dat
  3. Ejecuta la simulación completa: Sonido → Cóclea → IHC → AN → CN → IC → ABR
  4. Calcula el EFR usando análisis FFT (suma de armónicos a 110 Hz)
  5. Muestra los resultados y genera gráficos de diagnóstico

Contexto clínico:
  El EFR es una medida objetiva de la sincronización neural auditiva.
  Un EFR reducido (en µV) puede indicar pérdida auditiva, neuropatía
  auditiva o sinapatopatía coclear (sordera oculta).

Uso:
    python ExampleSimulation.py

Creado por: Brent Nissens
Basado en: Verhulst et al. 2018 y FullSimulationRAM.py
"""

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import os
import sys

# Agregar carpeta src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils.get_RAM_stims import get_RAM_stims
from model2018 import model2018

def calculate_EFR(output):
    """
    Calcula el EFR (Envelope Following Response) a partir de la salida del modelo.
    
    Biología:
    El EFR mide qué tan bien el sistema auditivo sigue la envolvente temporal
    de un sonido modulado. Se calcula sumando las ondas ABR (W1+W3+W5) y
    extrayendo la energía en la frecuencia de modulación (110 Hz) y sus
    armónicos (220, 330, 440 Hz) mediante análisis FFT.
    
    Un EFR bajo indica que las neuronas auditivas no logran sincronizarse
    con el ritmo del estímulo, lo cual puede deberse a:
      - Daño en las OHC (pérdida auditiva sensorineural)
      - Pérdida de sinapsis ribbon (sinapatopatía coclear / sordera oculta)
      - Neuropatía del nervio auditivo
    
    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo model2018
        
    Retorna:
    --------
    float
        Valor del EFR en microvoltios (μV)
    """
    try:
        # Manejar el caso donde la salida es una lista conteniendo un diccionario
        if isinstance(output, list) and len(output) > 0:
            output = output[0]  # Obtener el primer (y probablemente único) elemento
        
        # Extraer las ondas ABR de la salida del modelo
        fs = float(output.fs_an)
        w1 = output.w1.flatten()  # Onda I: nervio auditivo
        w3 = output.w3.flatten()  # Onda III: núcleo coclear
        w5 = output.w5.flatten()  # Onda V: colículo inferior

        # EFR = suma de las 3 ondas ABR (respuesta poblacional total)
        EFR = w1 + w3 + w5

        # Análisis FFT: descomponer el EFR en sus componentes frecuenciales
        L = len(EFR)
        Y = np.fft.fft(EFR)
        P2 = np.abs(Y / L)
        P1 = P2[:L//2 + 1]
        P1[1:-1] = 2 * P1[1:-1]
        f = fs * np.arange(L//2 + 1) / L

        # Buscar los 4 armónicos de la frecuencia de modulación (110 Hz):
        #   110 Hz (fundamental), 220 Hz (2°), 330 Hz (3°), 440 Hz (4°)
        # La energía en estos armónicos indica qué tan bien las neuronas
        # siguen el ritmo de modulación del estímulo RAM.
        fundamental = 110  # Hz
        num_harmonics = 4
        harmonics = np.arange(1, num_harmonics + 1) * fundamental
        idx = []
        for harmonic in harmonics:
            idx.append(np.argmin(np.abs(f - harmonic)))
        
        # Suma de armónicos convertida a microvoltios (µV)
        harmonic_sum = np.sum(P1[idx]) * 1e6

        return harmonic_sum, f, P1, harmonics, idx

    except Exception as e:
        print(f"Error calculating EFR: {e}")
        return np.nan, None, None, None, None

def run_easy_model(carrier_freq=4000, poles_profile='Flat00', show_plots=True, save_results=True):
    """
    Interfaz simplificada para ejecutar el modelo auditivo y calcular el EFR.
    
    Parámetros:
    -----------
    carrier_freq : float
        Frecuencia portadora del estímulo RAM en Hz (default: 4000).
        Típicamente 500, 1000, 2000 o 4000 Hz para mapear el audiograma.
    poles_profile : str
        Nombre del perfil de polos en ./Poles/ (default: 'Flat00' = audición normal).
        Otros perfiles simulan diferentes grados de pérdida auditiva.
    show_plots : bool
        Si generar gráficos de resultados
    save_results : bool
        Si guardar resultados en archivos .mat
        
    Retorna:
    --------
    dict
        Diccionario con:
        - 'efr_value': valor del EFR en µV
        - 'output': salida completa del modelo
        - 'stimulus': estímulo generado
        - 'frequency_spectrum': vector de frecuencias FFT
        - 'power_spectrum': espectro de potencia
    """
    
    print("="*60)
    print("Easy Model2018 Runner with EFR Calculation")
    print("="*60)
    
    # Configuration
    fs = 1e5  # Frecuencia de muestreo
    fRAM = np.array([carrier_freq])
    
    print(f"Carrier frequency: {carrier_freq} Hz")
    print(f"Sampling frequency: {fs} Hz")
    print(f"Poles profile: {poles_profile}")
    print()
    
    # Generar estímulo RAM
    print("Generating RAM stimulus...")
    try:
        stimulus = get_RAM_stims(fs, fRAM)
        print(f"✓ Generated stimulus: {stimulus.shape[1]} samples, duration: {stimulus.shape[1]/fs:.3f} s")
    except Exception as e:
        print(f"✗ Error generating stimulus: {e}")
        return None
    
    # Cargar perfil de polos de Shera
    poles_path = os.path.join(os.path.dirname(__file__), f'../data/Poles/{poles_profile}/StartingPoles.dat')
    print(f"Loading poles from: {poles_path}")
    try:
        sheraP = np.loadtxt(poles_path)
        # Take only the first row if there are multiple rows
        if sheraP.ndim > 1:
            sheraP = sheraP[0, :]
        print(f"✓ Loaded poles profile: {len(sheraP)} values")
    except Exception as e:
        print(f"✗ Error loading poles: {e}")
        print(f"Available poles profiles in ../data/Poles/:")
        try:
            poles_base_dir = os.path.join(os.path.dirname(__file__), '../data/Poles/')
            poles_dirs = [d for d in os.listdir(poles_base_dir) if os.path.isdir(os.path.join(poles_base_dir, d))]
            for d in sorted(poles_dirs):
                print(f"  - {d}")
        except:
            print("  Could not list poles directories")
        return None
    
    # Ejecutar modelo
    print("\nRunning model2018...")
    try:
        # Ejecutar la simulación completa del modelo auditivo.
        # Parámetros clave:
        #   fc='abr': secciones cocleares usadas para calcular las ondas ABR
        #   storeflag='evihmlbw': almacenar todas las variables del pipeline
        #   nH=13, nM=3, nL=3: distribución normal de fibras AN por IHC
        #   IrrPct=0.05: 5% de irregularidades en la BM (genera OAE)
        #   non_linear_type='vel': compresión coclear basada en velocidad BM
        results = model2018(
            stimulus, 
            fs, 
            fc='abr',                    # Puntos de sondeo para ABR
            irregularities=1,            # Habilitar irregularidades de Zweig (OAE)
            storeflag='evihmlbw',        # Almacenar: emisión, velocidad, IHC, fibras, ondas
            subject=1,                   # Semilla para irregularidades aleatorias
            sheraPo=sheraP,              # Perfil auditivo (polos de Shera)
            IrrPct=0.05,                 # Magnitud de irregularidades BM (5%)
            non_linear_type='vel',       # No-linealidad basada en velocidad BM
            nH=13,                       # Fibras HSR por IHC (alta tasa espontánea)
            nM=3,                        # Fibras MSR por IHC (media tasa espontánea)
            nL=3,                        # Fibras LSR por IHC (baja tasa espontánea)
            clean=1,
            data_folder='./'
        )
        print("✓ Model simulation completed successfully!")
    except Exception as e:
        print(f"✗ Error running model: {e}")
        return None
    
    # Calcular EFR
    print("\nCalculating EFR...")
    try:
        efr_value, f, P1, harmonics, harmonic_idx = calculate_EFR(results)
        if not np.isnan(efr_value):
            print(f"✓ EFR calculated: {efr_value:.4f} μV")
        else:
            print("✗ EFR calculation failed")
            return None
    except Exception as e:
        print(f"✗ Error calculating EFR: {e}")
        return None
    
    # Mostrar detalles de armónicos
    print("\nHarmonic Analysis:")
    for i, (harm_freq, idx) in enumerate(zip(harmonics, harmonic_idx)):
        power_uv = P1[idx] * 1e6
        print(f"  {harm_freq} Hz (harmonic {i+1}): {power_uv:.4f} μV")
    
    # Guardar resultados si fue solicitado
    if save_results:
        print("\nSaving results...")
        try:
            output = results[0]
            
            # Guardar EFR y ondas ABR
            EFR_combined = output.w1 + output.w3 + output.w5
            sio.savemat('easy_model_EFR.mat', {
                'EFR': EFR_combined,
                'w1': output.w1,
                'w3': output.w3,
                'w5': output.w5,
                'efr_value_uV': efr_value,
                'fs': output.fs_an,
                'carrier_freq': carrier_freq,
                'poles_profile': poles_profile
            })
            
            # Guardar velocidad BM y otras salidas
            sio.savemat('easy_model_output.mat', {
                'v': output.v,
                'cf': output.cf,
                'stimulus': stimulus,
                'fs_bm': output.fs_bm
            })
            
            print("✓ Results saved to:")
            print("  - easy_model_EFR.mat (EFR and waves)")
            print("  - easy_model_output.mat (full model output)")
            
        except Exception as e:
            print(f"✗ Error saving results: {e}")
    
    # Crear gráficos si fue solicitado
    if show_plots and f is not None:
        print("\nGenerating plots...")
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Model2018 Results - Carrier: {carrier_freq} Hz, Profile: {poles_profile}', fontsize=14)
            
            # Plot 1: Stimulus
            t_stim = np.arange(len(stimulus[0])) / fs
            axes[0,0].plot(t_stim[:1000], stimulus[0][:1000])  # Show first 1000 samples
            axes[0,0].set_title('RAM Stimulus (first 10 ms)')
            axes[0,0].set_xlabel('Time (s)')
            axes[0,0].set_ylabel('Amplitude')
            axes[0,0].grid(True)
            
            # Plot 2: EFR waveform
            output = results[0]
            EFR_combined = output.w1 + output.w3 + output.w5
            t_efr = np.arange(len(EFR_combined)) / output.fs_an
            axes[0,1].plot(t_efr, EFR_combined)
            axes[0,1].set_title('EFR Waveform (w1+w3+w5)')
            axes[0,1].set_xlabel('Time (s)')
            axes[0,1].set_ylabel('Amplitude')
            axes[0,1].grid(True)
            
            # Plot 3: Frequency spectrum
            axes[1,0].semilogy(f[:2000], P1[:2000])  # Show up to 400 Hz
            for i, idx in enumerate(harmonic_idx):
                axes[1,0].semilogy(f[idx], P1[idx], 'ro', markersize=8, 
                                 label=f'{harmonics[i]} Hz')
            axes[1,0].set_title('FFT Spectrum with Harmonics')
            axes[1,0].set_xlabel('Frequency (Hz)')
            axes[1,0].set_ylabel('Power')
            axes[1,0].grid(True)
            axes[1,0].legend()
            axes[1,0].set_xlim(0, 500)
            
            # Plot 4: Individual waves
            axes[1,1].plot(t_efr, output.w1, label='Wave 1', alpha=0.7)
            axes[1,1].plot(t_efr, output.w3, label='Wave 3', alpha=0.7)
            axes[1,1].plot(t_efr, output.w5, label='Wave 5', alpha=0.7)
            axes[1,1].set_title('Individual ABR Waves')
            axes[1,1].set_xlabel('Time (s)')
            axes[1,1].set_ylabel('Amplitude')
            axes[1,1].legend()
            axes[1,1].grid(True)
            
            plt.tight_layout()
            plt.savefig('easy_model_results.png', dpi=150, bbox_inches='tight')
            plt.show()
            
            print("✓ Plots saved as 'easy_model_results.png'")
            
        except Exception as e:
            print(f"✗ Error creating plots: {e}")
    
    # Preparar diccionario de retorno
    result_dict = {
        'efr_value': efr_value,
        'output': results[0],
        'stimulus': stimulus,
        'frequency_spectrum': f,
        'power_spectrum': P1,
        'harmonics': harmonics,
        'carrier_freq': carrier_freq,
        'poles_profile': poles_profile
    }
    
    print(f"\n" + "="*60)
    print(f"SUMMARY: EFR = {efr_value:.4f} μV")
    print("="*60)
    
    return result_dict

if __name__ == "__main__":
    # Ejemplo de uso con diferentes configuraciones
    
    print("Running easy model with default parameters...")
    results = run_easy_model()
    
    if results is not None:
        print(f"\nSuccess! EFR value: {results['efr_value']:.4f} μV")
        
        # You can also run with different parameters:
        # results = run_easy_model(carrier_freq=2000, poles_profile='Normal', show_plots=False)
        # results = run_easy_model(carrier_freq=8000, poles_profile='Flat10', save_results=False)
    else:
        print("\nModel run failed. Please check the error messages above.")
