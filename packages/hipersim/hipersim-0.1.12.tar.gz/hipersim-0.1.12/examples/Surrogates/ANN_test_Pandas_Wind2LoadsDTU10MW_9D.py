# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
print('Hellow world!')

#%%  Import data

InputData = pd.read_excel('Example_ML_FeatureSet_L.xlsx','InputVariables')
InputData.index = InputData['Sample_No'] # Make the "Sample_No" column as index of the data
InputData.head() # Show the first few rows of the data

TargetData = pd.read_excel('Example_ML_FeatureSet_L.xlsx','LoadResults')
TargetData.index = TargetData['Sample_No'] # Make the "PointNo" column as index of the data
TargetData.head() # Show the first few rows of the data

AllInputData = InputData.where(InputData['Sample_No']==TargetData['Sample_No'])
AllTargetData = TargetData.where(TargetData['Sample_No']==InputData['Sample_No'])
AllInputData = AllInputData.drop(columns = 'Sample_No') # We drop the colum with Sample_No, as this is anyway the index
AllTargetData = AllTargetData.drop(columns = 'Sample_No') # Note that we need to re-assign the data frame to the value with the dropped column!


nsamples = AllInputData['U'].count() # Find the total number of data points in the data frame
FeatureNames = AllInputData.columns.values
DependentVariableNames = AllTargetData.columns.values
print('Feature names: ', FeatureNames)
print('Dependent variable names: ', DependentVariableNames)

#%%  Define ANN model
from hipersim.surrogates import neuralnets

atest = neuralnets.ann(layersizes = [FeatureNames.shape[0], 50, 50, DependentVariableNames.shape[0]],
                       params = {'minibatchsize':0, 'nepochs':500}, 
                       output_style = 'Plot')
atest.train(AllInputData.values, AllTargetData.values)
Yout = atest.predict(AllInputData.values) # Compute outputs
Yout,dYout = atest.backward_propagation_dy(AllInputData.values) # Compute outputs AND analytical gradients


#%% Repeat with scikit-learn
import sklearn
import sklearn.neural_network
ANNmodel = sklearn.neural_network.MLPRegressor(hidden_layer_sizes = (50,50), activation = 'tanh', max_iter = 1500, verbose = True, learning_rate_init = 0.05,batch_size = nsamples)
ANNmodel.get_params

Xscaler = sklearn.preprocessing.StandardScaler()
Yscaler = sklearn.preprocessing.StandardScaler()
Xscaler.fit(AllInputData)
Yscaler.fit(AllTargetData)
Xtrain = Xscaler.transform(AllInputData)
Ytrain = Yscaler.transform(AllTargetData)

ANNmodel.set_params(learning_rate_init = 0.01, activation = 'tanh',tol = 1e-6,n_iter_no_change = 10)
ANNmodel.fit(Xtrain,Ytrain)

Ypred = Yscaler.inverse_transform(ANNmodel.predict(Xscaler.transform(AllInputData)))

#%% Try the correlation between the predictions with the two models
import matplotlib.pyplot as plt
fig,ax = plt.subplots(1,3,figsize = (15,4))
ax[0].plot(AllTargetData.values[:,0],Yout[:,0],'.k',label = 'Data vs. Hipersim')
ax[0].set_xlabel('Tower top $M_x$, data')
ax[0].set_ylabel('Tower top $M_x$, hipersim model')
ax[0].set_title('Target data vs. hipersim model')
ax[1].plot(AllTargetData.values[:,0],Ypred[:,0],'.k',label = 'Data vs. Scikit-learn')
ax[1].set_xlabel('Tower top $M_x$, data')
ax[1].set_ylabel('Tower top $M_x$, sklearn model')
ax[1].set_title('Target data vs. sklearn model')
ax[2].plot(Yout[:,0],Ypred[:,0],'.k',label = 'Hipersim vs. Scikit-learn')
ax[2].set_xlabel('Tower top $M_x$, hipersim model')
ax[2].set_ylabel('Tower top $M_x$, sklearn model')
ax[2].set_title('Hipersim vs. sklearn model')
plt.tight_layout()
