# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 10:26:26 2021

@author: nkdi
"""

#%% IMPORT LIBRARIES
import numpy as np
from hipersim.surrogates import neuralnets
from hipersim.surrogates.farm_utils import FarmUpwindDisturbances
import tensorflow_probability as tfp
import matplotlib.pyplot as plt

rng = np.random.default_rng(seed = 1)

#%% INPUTS

Nregular = 20
Nrandom = 20
Nturbrange = [20,100]
ThetaRange = np.arange(0,360,1)
Nthetas = len(ThetaRange)
AngleStep = 25
Nclosest = 20
Xmax = 100 # Maximum distance, also used as default value for empty features

#%% Regular wind farms - Horns Rev 1 - type of layout
X = np.empty((1,1))
fig,ax = plt.subplots(4,5)
for iF in range(50):
    Nx = rng.integers(2,11)
    Nturbines = rng.integers(Nturbrange[0],Nturbrange[1]+1)
    Nturbines = int(np.floor(Nturbines/Nx)*Nx)

    Dx = 3 + (10 - 3)*rng.random()
    Dy = 3 + (10 - 3)*rng.random()
    Alpha = -20 + 40*rng.random()
    Ny = int(np.floor(Nturbines/Nx))
    Drow = Dy*np.tan(np.deg2rad(Alpha))
    X01 = np.arange(0,(Nx-1)*Dx+1e-4,Dx)
    X1 = np.zeros((Ny,Nx))
    Y1 = np.zeros((Ny,Nx))
    X1[0,:] = X01
    for i in range(1,Ny):
        X1[i,:] = X01 + i*Drow

    Y01 = np.arange(0,(Ny-1)*Dy+1e-4,Dy)
    Y1[:,0] = Y01
    for i in range(1,Nx):
        Y1[:,i] = Y01   
        
    if iF < Nregular:
        plotrow = int(np.floor(iF/5))
        plotcolumn = int(np.mod(iF,5))
        ax[plotrow,plotcolumn].plot(X1,Y1,'ok',markersize = 2)
    
        X1 = X1.reshape(Nx*Ny)
        Y1 = Y1.reshape(Nx*Ny)         
        TurbineIDNumeric = np.arange(1,Nturbines+1)    
        DisturbanceList,DisturbanceDist,DisturbanceRelAngle,__,__,__,__ = FarmUpwindDisturbances(ThetaRange,TurbineIDNumeric,X1,Y1,None,None)    
        
        Xi = np.zeros((Nturbines*Nthetas,Nclosest*2))
        # Xi[:,:Nclosest[0]] = Xmax
        for iTheta in range(Nthetas):
            for iTurb in range(Nturbines):
                nDisturb = len(DisturbanceList[iTheta][iTurb])
                nDisturb = np.min((nDisturb,Nclosest))
                Xi[iTheta*Nturbines + iTurb,:nDisturb] = DisturbanceDist[iTheta][iTurb][:nDisturb]
                Xi[iTheta*Nturbines + iTurb,Nclosest:(Nclosest + nDisturb)] = np.sin(np.deg2rad(DisturbanceRelAngle[iTheta][iTurb][:nDisturb]))*DisturbanceDist[iTheta][iTurb][:nDisturb]
        
        if iF == 0:
            X = Xi
        else:
            X = np.concatenate([X,Xi])

plt.tight_layout()
#%% GENERATE "RANDOM" WIND FARMS
X0R = np.asarray(tfp.mcmc.sample_halton_sequence(2,num_results = Nturbrange[1]*Nrandom-1,randomized = False))
X0R = np.concatenate((np.zeros((1,2)),X0R))
Xcount = 0
fig,ax = plt.subplots(4,5)
for iF in range(Nrandom):
    Nturbines = np.random.randint(Nturbrange[0],Nturbrange[1]+1)
    XR = X0R[Xcount:(Xcount+Nturbines),:]
    Xcount = Xcount + Nturbines
    Scale = 20 + np.random.rand()*80
    Xrange = [0, Scale]
    Yrange = [0, Scale]

    X2 = Xrange[0] + XR[:,0]*(Xrange[-1] - Xrange[0])
    Y2 = Yrange[0] + XR[:,1]*(Yrange[-1] - Yrange[0])
    
    if iF < Nrandom:
    
        plotrow = int(np.floor(iF/5))
        plotcolumn = int(np.mod(iF,5))
        ax[plotrow,plotcolumn].plot(X2,Y2,'ok',markersize = 2)    
        
        TurbineIDNumeric = np.arange(1,Nturbines+1)    
        DisturbanceList,DisturbanceDist,DisturbanceRelAngle,__,__,__,__ = FarmUpwindDisturbances(ThetaRange,TurbineIDNumeric,X2,Y2,None,None)    
        
        Xi = np.zeros((Nturbines*Nthetas,Nclosest*2))
        # Xi[:,:Nclosest[0]] = Xmax
        for iTheta in range(Nthetas):
            for iTurb in range(Nturbines):
                nDisturb = len(DisturbanceList[iTheta][iTurb])
                nDisturb = np.min((nDisturb,Nclosest))
                Xi[iTheta*Nturbines + iTurb,:nDisturb] = DisturbanceDist[iTheta][iTurb][:nDisturb]
                Xi[iTheta*Nturbines + iTurb,Nclosest:(Nclosest + nDisturb)] = np.sin(np.deg2rad(DisturbanceRelAngle[iTheta][iTurb][:nDisturb]))*DisturbanceDist[iTheta][iTurb][:nDisturb]
        
        X = np.concatenate([X,Xi])
    
plt.tight_layout()
    
#%% SHUFFLE DATA
rng.shuffle(X,axis=0)

#%% DEFINE AUTOENCODER ARCHITECTURE AND TRAIN
ANN = neuralnets.ann(layersizes = [X.shape[1], 60, 10, 60, X.shape[1]],
                       params = {'minibatchsize':10000, 'nepochs':50, 
                                 'testratios':[0.9, 0.05, 0.05],'regularization':0.1,
                                 'learningrate':0.001}, 
                       output_style = 'Verbose')
Outdata = ANN.train(X,X)

#%% CHECK THE LEVEL OF RECOVERY OF X FEATURES
Xprime = ANN.predict(X)
from hipersim.surrogates.math_utils import pairwise_correlation

Rsqout = pairwise_correlation(X,Xprime)

#%% EXTRACT THE AUTOENCODER PART OF THE NETWORK
import copy
Autoencoder = copy.deepcopy(ANN)
EncodeLayers = 2
Autoencoder.nlayers = EncodeLayers
Autoencoder.layersizes = Autoencoder.layersizes[:EncodeLayers + 1]
Autoencoder.neurontypes = Autoencoder.neurontypes[:EncodeLayers + 1]
Autoencoder.activation = Autoencoder.activation[:EncodeLayers + 1]
Autoencoder.weights['W'] = Autoencoder.weights['W'][:EncodeLayers+1]
Autoencoder.weights['bias'] = Autoencoder.weights['bias'][:EncodeLayers+1]
Autoencoder.Ybias = np.zeros((1,Autoencoder.layersizes[-1]))
Autoencoder.Yscale = np.ones((1,Autoencoder.layersizes[-1]))

# Test if the autoencoder runs:
    
LatentVariables = Autoencoder.predict(X)

np.savetxt('Weights0.txt',Autoencoder.weights['W'][0])
np.savetxt('Weights1.txt',Autoencoder.weights['W'][1])
np.savetxt('Weights2.txt',Autoencoder.weights['W'][2])
np.savetxt('Biases0.txt',Autoencoder.weights['bias'][0])
np.savetxt('Biases1.txt',Autoencoder.weights['bias'][1])
np.savetxt('Biases2.txt',Autoencoder.weights['bias'][2])
np.savetxt('Xbias.txt',Autoencoder.Xbias)
np.savetxt('Xscale.txt',Autoencoder.Xscale)

import pickle
outfile = open('AutoencoderModel_20Farms_10outputs.sav','wb')
pickle.dump(Autoencoder,outfile)
outfile.close()