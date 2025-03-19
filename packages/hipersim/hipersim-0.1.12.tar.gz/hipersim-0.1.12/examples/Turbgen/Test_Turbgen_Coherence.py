# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 19:34:56 2021

@author: nkdi
"""

import numpy as np
from hipersim.turbgen.generate_field import generate_field
from hipersim.turbgen.manntensor import manntensor
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d 
# import os
# import time
pi = np.pi

Umean = 9.4975
TI = 0.0549
Nx = 16384
# Nx = 8192
Ny = 32;
Nz = 32;
Tsim = 1100
dx = Tsim*Umean / Nx
dy = 200 / Ny
dz = 200 / Nz
sigmaIso=Umean*TI*0.55
L=0.8*42
Gamma = 3.9
alphaepsilon=55/18*0.4754*sigmaIso**2*L**(-2/3)

HighFreqComp = 1
BaseName = 'Turb_py'

Nseeds = 10


#%% Generate the turbulence boxes   


SeedNo = np.arange(1011,1011+Nseeds)
for iSeed in SeedNo:
#SeedNo = 1001
    [u,v,w] = generate_field(BaseName,alphaepsilon,L,Gamma,iSeed,Nx,Ny,Nz,dx,dy,dz, \
                            HighFreqComp = 1, SaveToFile = 1)
    # MannGenCommand = str('d:/Hawc2/Mann64Bit/mann_turb_x64.exe ' + str(BaseName) + '_s' + str(iSeed) \
    #    +  ' ' + str(alphaepsilon) + ' ' + str(L) + ' ' + str(Gamma) + ' ' + str(iSeed) \
    #    +  ' ' + str(Nx) + ' ' + str(Ny) + ' ' + str(Nz) + ' ' + str(dx) + ' ' \
    #    +  str(dy) + ' ' + str(dz) + ' false')
    # t1 = time.time()
    # os.system(str('cmd /c ' + MannGenCommand))
    # t2 = time.time()
    # print(str('Mann turbulence box generated - time elapsed is ' + str(t2-t1)))
        

#u = np.swapaxes(u,1,2)

#%% Point spectra

N1int = Nx
N2int = 2*Ny
N3int = 2*Nz

L1 = N1int*dx
L2 = N2int*dy
L3 = N3int*dz

m1 = np.concatenate([np.arange(0,N1int/2),np.arange(-N1int/2,0)])
k1 = m1*2*pi/L1

klogrange = np.linspace(-6,2,100)
k1shift = 10**np.linspace(np.log10(np.min(k1[k1>0])),np.log10(np.max(k1)),60)
k2shift = np.concatenate([-np.flip(10**klogrange), 10**klogrange])
k3shift = np.concatenate([-np.flip(10**klogrange), 10**klogrange])


Psi11 = np.zeros(len(k1shift))
Psi22 = np.zeros(len(k1shift))
Psi33 = np.zeros(len(k1shift))
Psi13 = np.zeros(len(k1shift), dtype = 'csingle')

[k3i,k2i] = np.meshgrid(k3shift,k2shift)

for i in range(len(k1shift)):
    print(i)
    k1i = np.ones(k2i.shape)*k1shift[i]
    Phi11ij = manntensor(k1i,k2i,k3i,Gamma,L,alphaepsilon,2,11)
    Phi22ij = manntensor(k1i,k2i,k3i,Gamma,L,alphaepsilon,2,22)
    Phi33ij = manntensor(k1i,k2i,k3i,Gamma,L,alphaepsilon,2,33)
    Phi13ij = manntensor(k1i,k2i,k3i,Gamma,L,alphaepsilon,2,13)
    Psi11[i] = trapezoidal_sum_2d(Phi11ij,k2shift,k3shift)
    Psi22[i] = trapezoidal_sum_2d(Phi22ij,k2shift,k3shift)
    Psi33[i] = trapezoidal_sum_2d(Phi33ij,k2shift,k3shift)
    Psi13[i] = trapezoidal_sum_2d(Phi13ij,k2shift,k3shift)


#%% Coherence spacing

deltak2_vect = [3, 6, 1, 0, 0]
deltak3_vect = [0, 0, 1, 3, 6]

#%% Compute  coherence

Coherence = np.zeros((60,len(deltak2_vect)))
CoherenceP = np.zeros((int(Nx/2),len(deltak2_vect)))

for iDelta in range(len(deltak2_vect)):
    deltak2 = deltak2_vect[iDelta]
    deltak3 = deltak3_vect[iDelta]

    # THEORETICAL COHERENCE    
    
    #j = np.sqrt(-1)
    PsiCrossij = np.zeros(len(k1shift), dtype = 'csingle')
    PsiPointi = np.zeros(len(k1shift))
    PsiPointj = np.zeros(len(k1shift))
    
    [k3i,k2i] = np.meshgrid(k3shift,k2shift)
    
    for i in range(len(k1shift)):
        print(i)
        k1i = np.ones(k2i.shape)*k1shift[i]
        Phiij = manntensor(k1i,k2i,k3i,Gamma,L,alphaepsilon,2,11)
        PhiDeltaij = Phiij*np.exp(1j*(k2i*deltak2*dy + k3i*deltak3*dz))
        PsiCrossij[i] = trapezoidal_sum_2d(PhiDeltaij,k2shift,k3shift)
        PsiPointi[i] = trapezoidal_sum_2d(Phiij,k2shift,k3shift)
        PsiPointj[i] = PsiPointi[i]
    
    #Phase = atan2(imag(PsiCrossij),real(PsiCrossij));
    
#    Coherence[:,iDelta] = (np.conj(PsiCrossij)*PsiCrossij)/(PsiPointi*PsiPointj)
    Coherence[:,iDelta] = np.real(PsiCrossij)/PsiPointi

    # Coherence from time series
    
    Nysteps = Ny - deltak2
    Nzsteps = Nz - deltak3
    
    SUPiens = np.zeros(int(Nx/2))
    SUPjens = np.zeros(int(Nx/2))
    SUPijens = np.zeros(int(Nx/2), dtype = 'csingle')
    
       
    for iSeed in range(Nseeds):
        
        print(iSeed)
        
        ufile = str('c:/Users/nkdi/Documents/Programs/HiperSim/turbgen/Turb_py_' + str(1011 + iSeed) + '_u.bin')
        u = np.fromfile(ufile,dtype = 'single').reshape((Nx,Ny,Nz))
        
    
        for iy in range(Nysteps):
            for iz in range(Nzsteps):
                ui = u[:,iy,iz]
                uj = u[:,iy + deltak2,iz + deltak3]
                Sui = np.fft.fft(ui)
                Suj = np.fft.fft(uj)
                Suij = (1/(np.sqrt(2)*Nx*dx))*np.conj(Sui)*Suj
                Sui = (1/(np.sqrt(2)*Nx*dx))*np.abs(Sui)**2
                Suj = (1/(np.sqrt(2)*Nx*dx))*np.abs(Suj)**2
                Sui = Sui[:int(Nx/2)]
                Suj = Suj[:int(Nx/2)]
                Suij = Suij[:int(Nx/2)]
                SUPiens = SUPiens + Sui
                SUPjens = SUPjens + Suj
                SUPijens = SUPijens + Suij
                            
    
    SUPiens = SUPiens/(Nseeds*Nysteps*Nzsteps)
    SUPjens = SUPjens/(Nseeds*Nysteps*Nzsteps)
    SUPijens = SUPijens/(Nseeds*Nysteps*Nzsteps)
    
#    CoherenceP[:,iDelta] = (np.abs(SUPijens)**2)/(SUPiens*SUPjens)
    CoherenceP[:,iDelta] = np.real(SUPijens)/SUPiens
    
#%% Point spectra from time series    

S11ens = np.zeros(int(Nx/2))
S22ens = np.zeros(int(Nx/2))
S33ens = np.zeros(int(Nx/2))
S13ens = np.zeros(int(Nx/2), dtype = 'csingle')

for iSeed in range(Nseeds):
    
    print(iSeed)
    
    ufile = str('c:/Users/nkdi/Documents/Programs/HiperSim/turbgen/Turb_py_' + str(1011 + iSeed) + '_u.bin')
    vfile = str('c:/Users/nkdi/Documents/Programs/HiperSim/turbgen/Turb_py_' + str(1011 + iSeed) + '_v.bin')
    wfile = str('c:/Users/nkdi/Documents/Programs/HiperSim/turbgen/Turb_py_' + str(1011 + iSeed) + '_w.bin')
    u = np.fromfile(ufile,dtype = 'single').reshape((Nx,Ny,Nz))
    v = np.fromfile(vfile,dtype = 'single').reshape((Nx,Ny,Nz))
    w = np.fromfile(wfile,dtype = 'single').reshape((Nx,Ny,Nz))

    for iy in range(Nysteps):
        for iz in range(Nzsteps):
            Sui = np.fft.fft(u[:,iy,iz])
            Svi = np.fft.fft(v[:,iy,iz])            
            Swi = np.fft.fft(w[:,iy,iz])
            Suwi = (1/(np.sqrt(2)*Nx*dx))*np.conj(Sui)*Swi            
            Sui = (1/(np.sqrt(2)*Nx*dx))*np.abs(Sui)**2
            Svi = (1/(np.sqrt(2)*Nx*dx))*np.abs(Svi)**2
            Swi = (1/(np.sqrt(2)*Nx*dx))*np.abs(Swi)**2
                
            
            S11ens+= Sui[:int(Nx/2)]
            S22ens+= Svi[:int(Nx/2)]
            S33ens+= Swi[:int(Nx/2)]
            S13ens+= Suwi[:int(Nx/2)]  
    
S11ens = S11ens/(Nseeds*Nysteps*Nzsteps)
S22ens = S22ens/(Nseeds*Nysteps*Nzsteps)
S33ens = S33ens/(Nseeds*Nysteps*Nzsteps)
S13ens = S13ens/(Nseeds*Nysteps*Nzsteps)    

#%%
import matplotlib.pyplot as plt
plt.rc('font', size = 12)
fig,ax = plt.subplots(2,3, figsize = (16,10), dpi = 200)

f1shift = k1shift*Umean/(2*np.pi)
k1plot = np.arange(0,int(Nx/2))*2*pi/L1
f1plot = k1plot*Umean/(2*np.pi)

from mannspectrum import MannSpectrum_TableLookup
Psiinterp = MannSpectrum_TableLookup(Gamma, L, alphaepsilon, k1shift)
kinterp = Psiinterp[0]
Psi11interp = Psiinterp[1][0]
finterp = kinterp*Umean/(2*np.pi)

ax[0,0].plot(f1plot,CoherenceP[:,0],'-r', label = 'Hipersim 0.0.25')
ax[0,0].plot(f1shift,Coherence[:,0],'-b', label = 'Mann model')
ax[0,0].set_xlim([0,0.3])
ax[0,0].set_xlabel('f[Hz]')
ax[0,0].set_ylabel('u co-coherence [-]')
ax[0,0].set_title('$\Delta_y$ = 18.75m, $\Delta_z$ = 0m')
ax[0,0].legend()
ax[0,1].plot(f1plot,CoherenceP[:,1],'-r')
ax[0,1].plot(f1shift,Coherence[:,1],'-b')
ax[0,1].set_xlim([0,0.3])
ax[0,1].set_xlabel('f[Hz]')
ax[0,1].set_ylabel('u co-coherence [-]')
ax[0,1].set_title('$\Delta_y$ = 37.5m, $\Delta_z$ = 0m')
ax[0,2].plot(f1plot,CoherenceP[:,2],'-r')
ax[0,2].plot(f1shift,Coherence[:,2],'-b')
ax[0,2].set_xlim([0,0.3])
ax[0,2].set_xlabel('f[Hz]')
ax[0,2].set_ylabel('u co-coherence [-]')
ax[0,2].set_title('$\Delta_y$ = 6.25m, $\Delta_z$ = 6.25m')
ax[1,0].plot(f1plot,CoherenceP[:,3],'-r')
ax[1,0].plot(f1shift,Coherence[:,3],'-b')
ax[1,0].set_xlim([0,0.3])
ax[1,0].set_xlabel('f[Hz]')
ax[1,0].set_ylabel('u co-coherence [-]')
ax[1,0].set_title('$\Delta_y$ = 0m, $\Delta_z$ = 18.75m')
ax[1,1].plot(f1plot,CoherenceP[:,4],'-r')
ax[1,1].plot(f1shift,Coherence[:,4],'-b')
ax[1,1].set_xlim([0,0.3])
ax[1,1].set_xlabel('f[Hz]')
ax[1,1].set_ylabel('u co-coherence [-]')
ax[1,1].set_title('$\Delta_y$ = 0m, $\Delta_z$ = 37.5m')
#ax[1,2].plot(np.log10(f1shift),f1shift*np.real(Psi13))
#ax[1,2].plot(np.log10(f1plot),f1plot*np.real(S13ens))
ax[1,2].plot(np.log10(f1shift),(f1shift*np.real(Psi11)),'-r')
ax[1,2].plot(np.log10(f1plot),(f1plot*np.real(S11ens)),'or', label = 'u')
ax[1,2].plot(np.log10(f1shift),(f1shift*np.real(Psi22)),'-g')
ax[1,2].plot(np.log10(f1plot),(f1plot*np.real(S22ens)),'og', label = 'v')
ax[1,2].plot(np.log10(f1shift),(f1shift*np.real(Psi33)),'-b')
ax[1,2].plot(np.log10(f1plot),(f1plot*np.real(S33ens)),'ob', label = 'w')
ax[1,2].plot(np.log10(f1shift),(f1shift*np.real(Psi13)),'-k')
ax[1,2].plot(np.log10(f1plot),(f1plot*np.real(S13ens)),'ok', label = 'uw')
ax[1,2].legend()
ax[1,2].set_title('Point spectrum')
ax[1,2].set_xlabel('f[Hz]')
ax[1,2].set_ylabel('$fS(f)[m^2s^{-2}]$')
plt.tight_layout()
plt.show()

fig.savefig('Hipersim_coherence_test_HFComp.png', format = 'png', dpi = 200)

# ax[1,2].plot(k1shift,Coherence[:,2])
# ax[1,2].set_xlim([0,0.1])


#fig = plt.fi
