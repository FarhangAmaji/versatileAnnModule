#%% imports
# trainAnn.py
import os
baseFolder = os.path.dirname(os.path.abspath(__file__))
os.chdir(baseFolder)
from models.nbeats_blocks import stack, stackWithSharedWeights, SeasonalityBlock, TrendBlock, GenericBlock
from models.nbeats import nBeats
import torch
import torch.optim as optim
#%% define model
stacks=[stack([
    SeasonalityBlock(256, 1, True, 4),
    SeasonalityBlock(256, 1, True),
    TrendBlock(256,3,False),
    GenericBlock(256,10,False),
    ]),
       stackWithSharedWeights(GenericBlock(256,10,True),4) ]
nBeatsModel=nBeats(stacks, backcastLength=10, forecastLength=5)
#%%
'#ccc how to set optimizer manually'
# nBeatsModel.lr=0.001
# nBeatsModel.learningRate=0.001
# nBeatsModel.changeLearningRate(0.001)
# nBeatsModel.optimizer=optim.Adam(nBeatsModel.parameters(), lr=0.4)
# nBeatsModel.tensorboardWriter=newTensorboardPath
# nBeatsModel.batchSize=32
# nBeatsModel.evalBatchSize=1024
# nBeatsModel.device=torch.device(type='cpu') or torch.device(type='cuda')
# nBeatsModel.l1Reg=1e-3 or nBeatsModel.l2Reg=1e-3 or nBeatsModel.regularization=[None, None]

# nBeatsModel.patience=10
# nBeatsModel.saveOnDiskPeriod=1
# nBeatsModel.lossMode='accuracy'
# nBeatsModel.variationalAutoEncoderMode=True
#%% regression test
nBeatsModel.dropoutEnsembleMode=True
nBeatsModel.variationalAutoEncoderMode=True
workerNum=0
# Set random seed for reproducibility
torch.manual_seed(42)
import time
t0=time.time()
trainInputs = torch.randn(100, 40)  # Assuming 100 training samples with 40 features each
trainOutputs = torch.randn(100, 1)  # Assuming 100 training output values

testInputs = torch.randn(50, 40)  # Assuming 50 testing samples with 40 features each
testOutputs = torch.randn(50, 1)  # Assuming 50 testing output values

# Define the criterion (loss function)
criterion = torch.nn.MSELoss()  # Example: Mean Squared Error (MSE) loss

# Train the model
nBeatsModel.trainModel(trainInputs, trainOutputs, testInputs, testOutputs, criterion, numEpochs=200, savePath=r'data\bestModels\a1', workerNum=workerNum)

# Evaluate the model
evalLoss = nBeatsModel.evaluateModel(testInputs, testOutputs, criterion, workerNum=workerNum)
print("Evaluation Loss:", evalLoss)
print('time:',time.time()-t0)
'#ccc access to tensorboard with "tensorboard --logdir=data" from terminal'
#%% 
runcell=runcell
runcell('imports', 'F:/projects/public github projects/private repos/versatileAnnModule/trainAnn.py')
runcell('define model', 'F:/projects/public github projects/private repos/versatileAnnModule/trainAnn.py')
runcell('make model instance', 'F:/projects/public github projects/private repos/versatileAnnModule/trainAnn.py')
#%%
runcell('regression test', 'F:/projects/public github projects/private repos/versatileAnnModule/trainAnn.py')
#%%
#%% reload model
runcell('imports', 'F:/projects/public github projects/private repos/versatileAnnModule/trainAnn.py')
bestModel=ann.loadModel(r'data\bestModels\a1_InM9')
# bestModel.evaluateModel(testInputs, testOutputs, criterion)
#%% 

#%%
#%%
#%%
#%%
#%%

#%%

#%%

#%%

#%%


