"""
Orquestador Python del modelo Verhulst et al. (2018) de la periferia auditiva.

Este módulo encapsula el pipeline completo de simulación en una función
Python pura (model2018), eliminando la dependencia de archivos .mat de MATLAB.
Implementa la misma cadena de procesamiento que run_model2018.py pero como
una API invocable directamente desde código Python.

Pipeline biológico simulado:
  Sonido → Oído Medio → Cóclea (BM) → IHC → Nervio Auditivo → CN → IC → ABR

Autor: Convertido desde MATLAB por Brent Nissens
Basado en el trabajo original de Alessandro Altoè y Sarah Verhulst
"""

import numpy as np
import scipy as sp
import scipy.signal
import multiprocessing as mp
import warnings
from typing import Union, Optional, Dict, List, Any
import os
from utils.get_RAM_stims import get_RAM_stims
import scipy.io as sio

# Importa los componentes del modelo (cada etapa del procesamiento auditivo)
from core.cochlear_model2018 import cochlea_model
import core.inner_hair_cell2018 as ihc
import core.auditory_nerve2018 as anf
import core.ic_cn2018 as nuclei

# Suprimir advertencias como en el run_model2018.py original
warnings.filterwarnings("ignore")


class ModelOutput:
    """
    Estructura de datos para almacenar las salidas del modelo.
    
    Cada campo corresponde a una etapa del procesamiento auditivo:
    desde la mecánica coclear hasta las ondas del ABR.
    """
    
    def __init__(self):
        self.cf = None          # Frecuencias características de las secciones cocleares (Hz)
        self.v = None           # Velocidad de la membrana basilar (m/s por sección)
        self.y = None           # Desplazamiento de la membrana basilar (m por sección)
        self.emission = None    # Emisión otoacústica: presión en el canal auditivo (Pa)
        self.ihc = None         # Potencial receptor de la célula ciliada interna (V)
        self.anfH = None        # Tasa de disparo de fibras HSR (spikes/s)
        self.anfM = None        # Tasa de disparo de fibras MSR (spikes/s)
        self.anfL = None        # Tasa de disparo de fibras LSR (spikes/s)
        self.an_summed = None   # Suma ponderada de todas las fibras AN por sección
        self.cn = None          # Respuesta del Núcleo Coclear (spikes/s)
        self.ic = None          # Respuesta del Colículo Inferior (spikes/s)
        self.w1 = None          # Onda I del ABR (nervio auditivo, µV)
        self.w3 = None          # Onda III del ABR (núcleo coclear, µV)
        self.w5 = None          # Onda V del ABR (colículo inferior, µV)
        self.fs_bm = None       # Frecuencia de muestreo de la BM (Hz)
        self.fs_ihc = None      # Frecuencia de muestreo de la IHC (Hz)
        self.fs_an = None       # Frecuencia de muestreo del nervio auditivo (Hz)
        self.fs_abr = None      # Frecuencia de muestreo de las ondas ABR (Hz)


def model2018(
    sign: np.ndarray,
    fs: float,
    fc: Union[np.ndarray, str, int, float] = 'all',
    irregularities: Union[int, np.ndarray] = 1,
    storeflag: str = 'vihlmeb',
    subject: int = 1,
    sheraPo: Union[float, np.ndarray] = 0.06,
    IrrPct: float = 0.05,
    non_linear_type: str = 'vel',
    nH: Union[int, np.ndarray] = 13,
    nM: Union[int, np.ndarray] = 3,
    nL: Union[int, np.ndarray] = 3,
    clean: int = 1,
    data_folder: str = './') -> List[ModelOutput]:
    """
    Computational model of the auditory periphery (Verhulst, Altoe, Vasilkov, 2018).
    
    Parameters:
    -----------
    sign : np.ndarray
        Stimulus signal
    fs : float
        Sample rate
    fc : Union[np.ndarray, str, int, float], optional
        Probe frequency or alternatively a string 'all' to probe all cochlear
        sections or 'half' to probe half sections, 'abr' to store the
        401 sections used to compute the abr responses in Verhulst et al. 2017
    irregularities : Union[int, np.ndarray], optional
        Decide whether turn on (1) or off (0) irregularities and
        nonlinearities of the cochlear model (default 1)
    storeflag : str, optional
        String that sets what variables to store from the computation, 
        each letter correspond to one desired output variable (e.g., 'avhl' 
        to store acceleration, displacement, high and low spont. rate fibers.) 
        Default: 'vihlmeb'.
    subject : int, optional
        Number representing the seed to generate the random
        irregularities in the cochlear sections (default 1)
    sheraPo : Union[float, np.ndarray], optional
        Starting real part of the poles of the cochlear model
        it can be either an array with one value per BM section, or a
        single value for all sections (default 0.06)
    IrrPct : float, optional
        Magnitude of random perturbations on the BM (irregularities, default 0.05=5%)
    non_linear_type : str, optional
        Select the type of nonlinearity in the BM model.
        Currently implemented:
           'vel'= instantaneous nonlinearity based on local BM velocity (see Verhulst et al. 2012)
           'none'= linear model
    nH, nM, nL : Union[int, np.ndarray], optional
        Number of high, medium and low spont. fibers employed to
        compute the response of cn and ic nuclei. Default 13,3,3. These
        parameters can be passed either as a single value for all sections or
        as an array with each value corresponding to a single CF location
    clean : int, optional
        Not used in Python version (kept for compatibility)
    data_folder : str, optional
        Not used in Python version (kept for compatibility)
        
    Returns:
    --------
    List[ModelOutput]
        List of ModelOutput objects, one per channel, containing:
        - v: BM velocity (store 'v')
        - y: BM displacement (store 'y') 
        - emission: pressure output from the middle ear (store 'e')
        - cf: center frequencies (always stored)
        - ihc: IHC receptor potential (store 'i')
        - anfH: HSR fiber spike probability [0,1] (store 'h')
        - anfM: MSR fiber spike probability [0,1] (store 'm')
        - anfL: LSR fiber spike probability [0,1] (store 'l')
        - an_summed: summation of HSR, MSR and LSR per channel (storeflag 'b')
        - cn: cochlear nuclei output (storeflag 'b')
        - ic: IC (storeflag 'b')
        - w1, w3, w5: wave 1,3 and 5 (storeflag 'w')
        - fs_bm: sampling frequency of the bm simulations
        - fs_ihc: sample rate of the inner hair cell output
        - fs_an: sample rate of the an output
        - fs_abr: sample rate of the IC,CN and W1/3/5 outputs
    """
    
    DECIMATION = 5
    sectionsNo = 1000
    
    # Manejar dimensiones de la señal de entrada
    sign = np.atleast_2d(sign)
    if sign.shape[0] > sign.shape[1]:
        sign = sign.T  # Make sure it's channels x samples
    
    channels = sign.shape[0]
    
    # Manejar parámetro de irregularidades
    if np.isscalar(irregularities):
        irregularities = irregularities * np.ones(channels)
    
    # Manejar puntos de sondeo (parámetro fc)
    if isinstance(fc, str):
        if fc == 'all':
            l = sectionsNo
            probes = 'all'
        elif fc == 'half':
            l = sectionsNo // 2
            probes = 'half'
        elif fc == 'abr':
            l = 401
            probes = 'abr'
        else:
            raise ValueError(f"Unknown fc string option: {fc}")
    else:
        fc = np.atleast_1d(fc)
        l = len(fc)
        probes = np.round(fc).astype(int)
    
    # Manejar parámetro sheraPo (polos de Shera)
    if np.isscalar(sheraPo):
        sheraPo_val = sheraPo
    else:
        sheraPo_val = np.atleast_1d(sheraPo)
    
    # Manejar número de fibras AN por tipo
    if np.isscalar(nH):
        numH = nH
    else:
        numH = np.atleast_1d(nH)
        
    if np.isscalar(nM):
        numM = nM
    else:
        numM = np.atleast_1d(nM)
        
    if np.isscalar(nL):
        numL = nL
    else:
        numL = np.atleast_1d(nL)
    
    # Crear modelos cocleares para cada canal de estímulo
    cochlear_list = []
    for i in range(channels):
        coch = cochlea_model()
        cochlear_list.append([coch, sign[i], irregularities[i], i])
    
    def solve_one_cochlea(model_data):
        """
        Procesa un canal completo de la simulación auditiva.
        
        Pipeline: Cóclea → IHC → AN (HSR/MSR/LSR) → CN → IC → ABR (W1/W3/W5)
        """
        coch, sig, irr_on, channel_idx = model_data
        
        # ---- Etapa 1: Inicializar y resolver la mecánica coclear ----
        # Configura los polos de Shera (perfil auditivo) y resuelve la
        # ecuación diferencial de la línea de transmisión coclear.
        coch.init_model(
            sig, fs, sectionsNo, probes,
            Zweig_irregularities=irr_on,
            sheraPo=sheraPo_val,
            subject=subject,
            IrrPct=IrrPct,
            non_linearity_type=non_linear_type
        )
        
        # Resolver mecánica coclear (ondas viajeras en la membrana basilar)
        coch.solve()
        
        # Crear estructura de salida
        output = ModelOutput()
        output.cf = coch.cf
        output.fs_bm = fs
        output.fs_ihc = fs
        output.fs_an = fs // DECIMATION
        output.fs_abr = fs // DECIMATION
        
        # Almacenar velocidad BM si fue solicitada
        if 'v' in storeflag:
            output.v = coch.Vsolution
            
        # Almacenar desplazamiento BM si fue solicitado
        if 'y' in storeflag:
            output.y = coch.Ysolution
            
        # Almacenar emisiones otoacústicas si fue solicitado
        if 'e' in storeflag:
            output.emission = coch.oto_emission
            
        # ---- Etapa 2: Transducción mecano-eléctrica en la IHC ----
        # La velocidad BM (Vsolution) deflecta los estereocilios de las IHC,
        # generando corrientes de transducción que producen el potencial receptor (Vm).
        if any(flag in storeflag for flag in 'ihmlbw'):
            # magic_constant (0.118): factor de escala velocidad BM → deflexión de estereocilios
            magic_constant = 0.118
            Vm = ihc.inner_hair_cell_potential(coch.Vsolution * magic_constant, fs)
            
            if 'i' in storeflag:
                output.ihc = Vm
                
            # ---- Etapa 3: Submuestreo para el nervio auditivo ----
            # El nervio auditivo opera a frecuencias de muestreo menores
            # que la mecánica coclear (la sinapsis actúa como filtro paso bajo).
            dec_factor = 5
            Vm_resampled = sp.signal.decimate(Vm, dec_factor, axis=0, n=30, ftype='fir')
            Vm_resampled[0:5, :] = Vm[0, 0]  # valor de reposo para eliminar ruido del decimado
            Fs_res = fs / dec_factor
            
            # ---- Etapa 4: Fibras del nervio auditivo ----
            # Simula la transducción sináptica IHC → AN para cada tipo de fibra:
            if any(flag in storeflag for flag in 'hmlbw'):
                
                # HSR (High Spontaneous Rate): fibras de bajo umbral, primeras en responder
                if 'h' in storeflag or 'b' in storeflag:
                    anfH = anf.auditory_nerve_fiber(Vm_resampled, Fs_res, 2) * Fs_res
                    if 'h' in storeflag:
                        output.anfH = anfH
                        
                # MSR (Medium Spontaneous Rate): umbral intermedio
                if 'm' in storeflag or 'b' in storeflag or 'w' in storeflag:
                    anfM = anf.auditory_nerve_fiber(Vm_resampled, Fs_res, 1) * Fs_res
                    if 'm' in storeflag:
                        output.anfM = anfM
                        
                # LSR (Low Spontaneous Rate): alto umbral, cruciales para codificar en ruido
                if 'l' in storeflag or 'b' in storeflag or 'w' in storeflag:
                    anfL = anf.auditory_nerve_fiber(Vm_resampled, Fs_res, 0) * Fs_res
                    if 'l' in storeflag:
                        output.anfL = anfL
                
                # ---- Etapa 5: Núcleos del tronco encefálico (CN e IC) ----
                # CN: suma ponderada de las fibras AN + excitación-inhibición
                # IC: segundo nivel de integración neural
                if 'b' in storeflag or 'w' in storeflag:
                    cn, anSummed = nuclei.cochlearNuclei(anfH, anfM, anfL, numH, numM, numL, Fs_res)
                    ic = nuclei.inferiorColliculus(cn, Fs_res)
                    
                    if 'b' in storeflag:
                        output.cn = cn
                        output.ic = ic
                        output.an_summed = anSummed
                        
                    # ---- Etapa 6: Ondas del ABR ----
                    # W1 (Onda I): nervio auditivo sumado × M1
                    # W3 (Onda III): núcleo coclear sumado × M3
                    # W5 (Onda V): colículo inferior sumado × M5
                    # La suma W1+W3+W5 = EFR (Envelope Following Response)
                    if 'w' in storeflag:
                        output.w1 = nuclei.M1 * np.sum(anSummed, axis=1)
                        output.w3 = nuclei.M3 * np.sum(cn, axis=1)
                        output.w5 = nuclei.M5 * np.sum(ic, axis=1)
        
        return output
    
    # ---- Ejecución paralela o secuencial ----
    # Para múltiples canales se usa multiprocessing para acelerar la simulación.
    if channels == 1:
        results = [solve_one_cochlea(cochlear_list[0])]
    else:
        with mp.Pool(mp.cpu_count(), maxtasksperchild=1) as p:
            results = p.map(solve_one_cochlea, cochlear_list)
    
    print("cochlear simulation: done")
    
    return results


if __name__ == "__main__":
    # Crear un estímulo de prueba a 4000 Hz
    fs = 1e5
    stimulus = get_RAM_stims(fs,np.array([4000]))

    # Cargar el perfil de polos de Shera
    sheraP = np.loadtxt(f'./Poles/Flat00/StartingPoles.dat')

    # Ejecutar el modelo
    print("Running model2018 example...")
    results = model2018(
        stimulus, 
        fs, 
        fc='abr',
        irregularities=0.05,
        storeflag='evihmlbw',
        subject=1,
        sheraPo=sheraP,
        IrrPct=0.05,
        non_linear_type='vel',
        nH=13,
        nM=3,
        nL=3,
        clean=1,
        data_folder='./'
    )
    
    # Mostrar resultados
    output = results[0]
    print(f"Model completed successfully!")