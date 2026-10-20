# =============================================================================
# SCRIPT DE EJECUCIÓN: Pipeline completo de la simulación auditiva
# =============================================================================
# Este script orquesta toda la simulación del modelo Verhulst 2018.
# Lee los parámetros desde un archivo MATLAB (input.mat) y ejecuta
# la cadena completa de procesamiento auditivo:
#
#   Sonido → Oído Medio → Cóclea (BM) → IHC → Nervio Auditivo → CN → IC → ABR
#
# Cada etapa se almacena en archivos .mat independientes según el
# storeflag configurado por el usuario.
# =============================================================================
import numpy as np
import scipy as sp
import scipy.io as sio
from core.cochlear_model2018 import *
import os
import warnings
import multiprocessing as mp
import ctypes as c
import time
import sys
import core.inner_hair_cell2018 as ihc
import core.auditory_nerve2018 as anf
import core.ic_cn2018 as nuclei

#this relates to python 3.6 on ubuntu
#there is one future warning related to "scipy.signal.decimate" in this file
#there is one runtime warning related to firwin "scipy.signal.decimate" in ic_cn2017.py (not important)
#so we suppress these warnings here
warnings.filterwarnings("ignore")

# ---- Carga de parámetros de entrada desde MATLAB ----
# probes: qué secciones cocleares almacenar ('all', 'half', 'abr' o frecuencias específicas)
# storeflag: qué variables guardar (v=velocidad BM, i=IHC, h=HSR, m=MSR, l=LSR, etc.)
# sheraPo: polos de Shera que definen el perfil auditivo (normal vs. pérdida)
# numH/M/L: número de fibras HSR/MSR/LSR por IHC
par=sio.loadmat('input.mat')
probes=np.array(par['probes'])
storeflag_in=np.array(par['storeflag'],dtype=str)
storeflag=storeflag_in[0]
probe_points=probes
Fs=par['Fs']
Fs=Fs[0][0]
stim=par['stim']
channels=par['channels']
channels=int(channels[0][0])
subjectNo=int(par['subject'])
sectionsNo=int(par['sectionsNo'])
t_f=(par['data_folder'])
output_folder=str(t_f[0])
lgt=len(stim[0])
sheraPo=par['sheraPo']
if(max(np.shape(sheraPo))==1):
    sheraPo=sheraPo[0][0]
else:
    sheraPo=sheraPo[:,0]
# Número de fibras por tipo de tasa espontánea:
# numH (HSR): fibras de alta tasa espontánea (~13 por IHC)
# numM (MSR): fibras de media tasa espontánea (~3 por IHC)
# numL (LSR): fibras de baja tasa espontánea (~3 por IHC)
numH=par['nH']
if(max(np.shape(numH))==1):
    numH=numH[0][0]
else:
    numH=numH[:,0]
numM=par['nM']
if(max(np.shape(numM))==1):
    numM=numM[0][0]
else:
    numM=numM[:,0]
numL=par['nL']
if(max(np.shape(numL))==1):
    numL=numL[0][0]
else:
    numL=numL[:,0]




IrrPct=par['IrrPct']
IrrPct=IrrPct[0][0]
nl=np.array(par['non_linear_type'])
#print(IrrPct)
#print(sheraPo)
irr_on=np.array(par['irregularities'])
d=len(stim[0].transpose())
print("running human auditory model 2018 (version 1.2): Verhulst, Altoe, Vasilkov")
sig=stim

# Crea una instancia del modelo coclear por cada canal de estímulo
cochlear_list=[ [cochlea_model(),sig[i],irr_on[0][i],i] for i in range(channels)]
#sheraPo = np.loadtxt('StartingPoles.dat', delimiter=',')
#print(sheraPo)

# =============================================================================
# FUNCIÓN PRINCIPAL: Procesa un canal completo de la simulación
# =============================================================================
# Pipeline para cada canal:
#   1. Inicializar modelo coclear con los polos de Shera (perfil auditivo)
#   2. Resolver la mecánica coclear (BM velocity + displacement)
#   3. Calcular potencial receptor de las IHC (transducción mecánico-eléctrica)
#   4. Calcular tasas de disparo de las fibras AN (HSR, MSR, LSR)
#   5. Calcular respuestas del CN e IC (núcleos del tronco encefálico)
#   6. Generar las ondas ABR (W1, W3, W5) por suma poblacional
def solve_one_cochlea(model): #definition here, to have all the parameter implicit
    ii=model[3]
    coch=model[0]
    sig=model[1]
    # Paso 1: Inicializar el modelo coclear con el perfil auditivo
    coch.init_model(model[1],Fs,sectionsNo,probe_points,Zweig_irregularities=model[2],sheraPo=sheraPo,subject=subjectNo,IrrPct=IrrPct,non_linearity_type=nl)

    # Paso 2: Resolver la mecánica coclear (ondas viajeras en la BM)
    coch.solve()
    # Paso 3: Calcular el potencial receptor de las IHC.
    # magic_constant (0.118): factor de escala que convierte velocidad BM
    # en deflexión equivalente de estereocilios de la IHC.
    magic_constant=0.118;
    Vm=ihc.inner_hair_cell_potential(coch.Vsolution*magic_constant,Fs)
    # Paso 3b: Submuestreo (decimación x5) del potencial IHC para el
    # procesamiento del nervio auditivo (opera a menor frecuencia de muestreo).
    dec_factor=5
    Vm_resampled=sp.signal.decimate(Vm,dec_factor,axis=0,n=30,ftype='fir')
    Vm_resampled[0:5,:]=Vm[0,0]; #resting value to eliminate noise from decimate
    Fs_res=Fs/dec_factor
#    print(np.shape(coch.Vsolution),np.shape(Vm_resampled))

    fname = output_folder+"cf"+str(ii+1)+".mat"
    mdict = {'cf':coch.cf}
    sio.savemat(fname,mdict)

    if 'v' in storeflag:
        fname = output_folder+"v"+str(ii+1)+".mat"
        mdict = {'Vsolution':coch.Vsolution}
        sio.savemat(fname,mdict)

    if 'y' in storeflag:
        fname = output_folder+"y"+str(ii+1)+".mat"
        mdict = {'Ysolution':coch.Ysolution}
        sio.savemat(fname,mdict)

    if 'i' in storeflag:
        fname = output_folder+"ihc"+str(ii+1)+".mat"
        mdict = {'Vm':Vm}
        sio.savemat(fname,mdict)

    # ---- Paso 4: Fibras del nervio auditivo ----
    # Se calculan las tasas de disparo para cada tipo de fibra:
    #   HSR (tipo 2): alta tasa espontánea, bajo umbral
    #   MSR (tipo 1): media tasa espontánea
    #   LSR (tipo 0): baja tasa espontánea, alto umbral
    if 'h' in storeflag or 'b' in storeflag:
        anfH=anf.auditory_nerve_fiber(Vm_resampled,Fs_res,2)*Fs_res
    #print(np.shape(coch.Vsolution),np.shape(Vm_resampled),np.shape(anfH))

    if 'h' in storeflag:
        fname = output_folder+"anfH"+str(ii+1)+".mat"
        mdict = {'anfH':anfH}
        sio.savemat(fname,mdict)

    if 'm' in storeflag or 'b' in storeflag:
        anfM=anf.auditory_nerve_fiber(Vm_resampled,Fs_res,1)*Fs_res

    if 'm' in storeflag:
        fname = output_folder+"anfM"+str(ii+1)+".mat"
        mdict = {'anfM':anfM}
        sio.savemat(fname,mdict)

    if 'l' in storeflag or 'b' in storeflag:
        anfL=anf.auditory_nerve_fiber(Vm_resampled,Fs_res,0)*Fs_res

    if 'l' in storeflag:
        fname = output_folder+"anfL"+str(ii+1)+".mat"
        mdict = {'anfL':anfL}
        sio.savemat(fname,mdict)

    if 'e' in storeflag:
        fname = output_folder+"emission"+str(ii+1)+".mat"
        mdict = {'oto_emission':coch.oto_emission}
        sio.savemat(fname,mdict)

    # ---- Paso 5: Núcleos del tronco encefálico (CN e IC) ----
    # El CN suma las fibras HSR+MSR+LSR ponderadas y aplica excitación-inhibición.
    # El IC procesa la salida del CN con un segundo nivel de integración.
    if 'b' in storeflag or 'w' in storeflag:
        cn,anSummed=nuclei.cochlearNuclei(anfH,anfM,anfL,numH,numM,numL,Fs_res)
        ic=nuclei.inferiorColliculus(cn,Fs_res)

        if 'b' in storeflag:
            fname = output_folder+"cn"+str(ii+1)+".mat"
            mdict = {'cn':cn}
            sio.savemat(fname,mdict)

            fname = output_folder+"AN"+str(ii+1)+".mat"
            mdict = {'anSummed':anSummed}
            sio.savemat(fname,mdict)

            fname = output_folder+"ic"+str(ii+1)+".mat"
            mdict = {'ic':ic}
            sio.savemat(fname,mdict)

        # ---- Paso 6: Ondas del ABR (Auditory Brainstem Response) ----
        # Las ondas del ABR se generan sumando la actividad neural poblacional
        # de cada estación y escalándola con factores de voltaje (M1, M3, M5).
        # W1 (Onda I): nervio auditivo sumado × M1 → actividad del nervio VIII
        # W3 (Onda III): núcleo coclear sumado × M3 → actividad del CN
        # W5 (Onda V): colículo inferior sumado × M5 → actividad del IC
        # La suma de W1+W3+W5 = EFR (Envelope Following Response)
        if 'w' in storeflag:

            w1=nuclei.M1*np.sum(anSummed,axis=1);
            w3=nuclei.M3*np.sum(cn,axis=1)
            w5=nuclei.M5*np.sum(ic,axis=1)

            fname = output_folder+"1w"+str(ii+1)+".mat"
            mdict = {'w1':w1}
            sio.savemat(fname,mdict)

            fname = output_folder+"3w"+str(ii+1)+".mat"
            mdict = {'w3':w3}
            sio.savemat(fname,mdict)

            fname = output_folder+"5w"+str(ii+1)+".mat"
            mdict = {'w5':w5}
            sio.savemat(fname,mdict)


# Ejecución paralela: cada canal de estímulo se procesa en un core de CPU
# independiente, aprovechando multiprocessing para acelerar la simulación.
if __name__ == "__main__":
    p=mp.Pool(mp.cpu_count(),maxtasksperchild=1)
    p.map(solve_one_cochlea,cochlear_list)
    p.close()
    p.join()

    print("cochlear simulation: done")
