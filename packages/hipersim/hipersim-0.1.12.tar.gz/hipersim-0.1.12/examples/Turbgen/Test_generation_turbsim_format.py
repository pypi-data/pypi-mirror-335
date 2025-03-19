# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 23:08:14 2021

@author: nkdi
"""

from hipersim.turbgen import turbgen
import numpy as np


# Mean wind speed and TI at hub height
U = 8 # in m/s
TI = 9.8 # in percent

# Grid dimensions
Lt = 700
Ly = 160
Lz = 160

# time step
dt = 0.1 #time resolution


# Number of gird points
Ny = 16
Nz = 16
Nx = int(Lt / dt)

# Grid resolution
dx = U*dt
dy = Ly / Ny
dz = Lz / Nz 

x = dt*np.arange(Nx)
y = dy*np.arange(Ny)
z = dz*np.arange(Nz)
ygrid,zgrid = np.meshgrid(y,z)

sigmauens = np.zeros(len(z))
from generate_field import generate_field
    
for i in range(10):
    iSeed = i + 10
    print(i)
    """
    T = turbgen.turb_field(Nx = Nx, Ny = Ny, Nz = Nz, dx = dx, dy = dy, dz = dz, alphaepsilon = 0.1, SeedNo = iSeed, SaveToFile = 0, BaseName = 'HiperSim_'+str(U)+'ms')
    u,v,w = T.generate()
    
    # OUTPUT WITH MEAN FIELD CORRECTIONS IN HAWC2 FORMAT:
#    T.params['SaveToFile'] = 1
    T.TurbOptions = {'FileFormat': 0,
                     'Umean': U,
                     'zHub': 83.0,
                     'alpha': 0.08,
                     'TI_u': TI/100,
                     'TI_v': (TI/100)*0.8, # modified to agree with the assumptions of the Kaimal Model 
                     'TI_w': (TI/100)*0.5, # modified to agree with the assumptions of the Kaimal Model
                     'yaw': 0}
    
    u1,v1,w1 = T.output()
    
    # UPDATE FILE FORMAT OPTIONS TO SAVE THE OUTPUT IN TURBSIM FORMAT:
    T.TurbOptions['FileFormat'] = 'wnd'
#    u2,v2,w2 = T.output()
    
    """

    u,v,w = generate_field(BaseName = 'Turb',alphaepsilon = 0.1,L = 29.4,Gamma = 3.9,SeedNo = iSeed,
                       Nx = 8192,Ny = Ny,Nz = Nz,dx = dx,dy = dy,dz = dz, \
                        HighFreqComp = 0, SaveToFile = 0, TurbOptions = None)

    sigmauens = sigmauens + u[:,8,:].std(axis=0)
    
sigmauens = sigmauens/10

# %% Plots 
import matplotlib.pyplot as plt
umean = np.mean(u,axis=0)
#plt.plot(u[:,9,:].mean(axis=0))

# Plot a cross section of the resulting field

#vmax = np.max((np.max(T.u),-np.min(T.u)))
#vmin = -vmax
import matplotlib.pyplot as plt
#norm = plt.Normalize(vmin=vmin, vmax = vmax)
fig0 = plt.figure()
plt.plot(sigmauens/U,z)

fig = plt.figure(figsize = (10,10), dpi = 300)
plt.pcolormesh(ygrid,zgrid,umean, cmap = 'coolwarm', shading = 'gouraud')
plt.xlabel('x[m]')
plt.ylabel('z[m]')
plt.show()



