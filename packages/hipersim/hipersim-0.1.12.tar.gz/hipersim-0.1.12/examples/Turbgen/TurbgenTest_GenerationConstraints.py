# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 09:05:01 2021

@author: nkdi
"""
from hipersim.turbgen import turbgen
import numpy as np

Nx = 1024
dx = 2
dy = 4
dz = 4
T = turbgen.turb_field(Nx = 1024, dx = dx, dy = dy, dz = dz, HighFreqComp = 1,SaveToFile = 1, SeedNo = 10)

'''
u,v,w = generate_field(BaseName = 'Turb', \
                       alphaepsilon = 1,L = 30,Gamma = 3, \
                       SeedNo = 1, \
                       Nx = 1024,Ny = 32,Nz = 32,dx = 2,dy = 4,dz = 4, \
                       HighFreqComp = 0, SaveToFile = 0) 
'''

u, v, w = T.generate()

x = dx*np.arange(Nx)
y = dy*np.arange(32)
z = dz*np.arange(32)
xgrid,zgrid = np.meshgrid(x,z)
vmax = np.max((np.max(T.u),-np.min(T.u)))
vmin = -vmax
import matplotlib.pyplot as plt
norm = plt.Normalize(vmin=vmin, vmax = vmax)
fig,(ax0,ax1) = plt.subplots(2,figsize = (16,10), dpi = 300)
ax0.pcolormesh(xgrid,zgrid,T.u[:,15,:].T, cmap = 'coolwarm', shading = 'gouraud', norm = norm)



Xconstraints = np.atleast_2d(np.arange(1,2000,4)).T
Yconstraints1 = 60*np.ones(Xconstraints.shape)
Zconstraints1 = 10*np.ones(Xconstraints.shape)
Yconstraints2 = 10*np.ones(Xconstraints.shape)
Zconstraints2 = 60*np.ones(Xconstraints.shape)
Uconstraints = 10*np.exp(-0.5*( (Xconstraints - 1000)/200)**2)
Vconstraints = -5*np.exp(-0.5*( (Xconstraints - 1000)/200)**2)
Wconstraints = -2*np.exp(-0.5*( (Xconstraints - 1000)/200)**2)
Constraints = np.concatenate([np.concatenate([Xconstraints, Xconstraints]), 
                              np.concatenate([Yconstraints1, Yconstraints2]),
                              np.concatenate([Zconstraints1, Zconstraints2]),
                              np.concatenate([Uconstraints, -Uconstraints]),
                              np.concatenate([Vconstraints, -Vconstraints]),
                              np.concatenate([Wconstraints, -Wconstraints])],axis = 1)
ax0.plot(Xconstraints,Zconstraints1,'ok', markersize = 0.75)

u, v, w = T.constrain(Constraints = Constraints)

#ax1.pcolormesh(xgrid,zgrid,T.u[:,2,:].T, cmap = 'coolwarm', shading = 'gouraud', norm = norm)
ax1.pcolormesh(xgrid,zgrid,T.u[:,15,:].T, cmap = 'coolwarm', shading = 'gouraud', norm = norm)
ax1.plot(Xconstraints,Zconstraints1,'ok', markersize = 0.75)
#plt.imshow(T.u[:,15,:].T,cmap = 'coolwarm')

u1 = np.fromfile('c:/Users/nkdi/Documents/Programs/HiperSim/release/examples/Turb_py_10_c_u_py.bin', dtype = 'single').reshape((Nx,32,32))
ax0.pcolormesh(xgrid,zgrid,u1[:,15,:].T, cmap = 'coolwarm', shading = 'gouraud', norm = norm)