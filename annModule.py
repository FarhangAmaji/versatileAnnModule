# annModule.py
import torch
import torch.nn as nn
import torch.optim as optim
import inspect
import types
import os
from torch.utils.tensorboard import SummaryWriter

def randomIdFunc(stringLength=4):
    import random
    import string
    characters = string.ascii_letters + string.digits
    
    return ''.join(random.choices(characters, k=stringLength))

class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj

class ann(nn.Module, metaclass=PostInitCaller):#kkk do hyperparam search maybe with mopso(note to utilize the tensorboard)
    def __init__(self):
        super(ann, self).__init__()
        self.getInitInpArgs()
        self.device= torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.patience = 10
        self.optimizer = None
        self.tensorboardWriter = None
        self.batchSize = 64
        self.evalBatchSize = 1024
        self.saveOnDiskPeriod = 5
        
        # define model here
        # self.layer1 = self.linLReluDropout(40, 160, dropoutRate=0.5)
        # self.layer2 = self.linLSigmoidDropout(200, 300, dropoutRate=0.2)
        #self.layer3 = nn.Linear(inputSize, 4*inputSize)
        # Add more layers as needed
    def __post_init__(self):
        '# ccc this is ran after child class constructor'
        if isinstance(self, ann) and not type(self) == ann:
            self.to(self.device)
            # self.initOptimizer()

    def forward(self, x):
        # define forward step here
        # x = self.layer1(x)
        # x = self.layer2(x)
        # x = self.layer3(x)
        return x
    
    @property
    def device(self):
        return self._device
    
    @device.setter
    def device(self, value):
        assert value in [torch.device(type='cuda'),torch.device(type='cpu')],"device={value} must be 'cuda' or 'cpu'"
        self._device = value
        self.to(value)
    
    @property
    def optimizer(self):
        return self._optimizer

    @optimizer.setter
    def optimizer(self, value):
        assert isinstance(value, (optim.Optimizer, type(None))),f'optimizerType={type(value)} is not correct'
        self._optimizer = value
    
    def getInitInpArgs(self):
        numOfFbacksNeeded=0
        foundAnn=False
        classHierarchy = self.__class__.mro()
        for i in range(len(classHierarchy)):
            if classHierarchy[i]==ann:
                numOfFbacksNeeded = i +1
                foundAnn=True
                break
        assert foundAnn,'it seems the object is not from ann class'
        frame_ = inspect.currentframe()
        for i in range(numOfFbacksNeeded):
            frame_=frame_.f_back
        args, _, _, values = inspect.getargvalues(frame_)
        "#ccc patience and optimizer's change should not affect that doesnt let the model rerun"
        excludeInputArgs = ['patience', 'optimizer', 'device']
        for eia in excludeInputArgs:
            if eia in args:
                args.remove(eia)
        self.inputArgs = {arg: values[arg] for arg in args if arg != 'self'}
        
    def linLReluDropout(self, innerSize, outterSize, leakyReluNegSlope=0.05, dropoutRate=False):
        activation = nn.LeakyReLU(negative_slope=leakyReluNegSlope)
        return self.linActivationDropout(innerSize, outterSize, activation, dropoutRate)
    
    def linLSigmoidDropout(self, innerSize, outterSize, dropoutRate=False):
        activation = nn.Sigmoid()
        return self.linActivationDropout(innerSize, outterSize, activation, dropoutRate)
    
    def linActivationDropout(self, innerSize, outterSize, activation, dropoutRate=None):
        '#ccc instead of defining many times of leakyRelu and dropOuts I do them at once'
        layer = nn.Sequential(
            nn.Linear(innerSize, outterSize),
            activation)
        
        if dropoutRate:
            assert type(dropoutRate) in (int, float),f'dropoutRateType={type(dropoutRate)} is not int or float'
            assert 0 <= dropoutRate <= 1, f'dropoutRate={dropoutRate} is not between 0 and 1'
            drLayer = nn.Dropout(p=dropoutRate)
            return nn.Sequential(layer, drLayer)
        return layer
    @property
    def tensorboardWriter(self):
        return self._tensorboardWriter
    
    @tensorboardWriter.setter
    def tensorboardWriter(self, tensorboardPath):
        if tensorboardPath:
            os.makedirs(os.path.dirname(tensorboardPath+'_Tensorboard'), exist_ok=True)
            self._tensorboardWriter = SummaryWriter(tensorboardPath+'_Tensorboard')
    
    def initOptimizer(self):
        if list(self.parameters()):
            self.optimizer = optim.Adam(self.parameters(), lr=0.00001)
        else:
            self.optimizer = None
    def tryToSetDefaultOptimizerIfItsNotSet(self):
        if not isinstance(self.optimizer, optim.Optimizer):
            self.initOptimizer()
    
    def havingOptimizerCheck(self):
        self.tryToSetDefaultOptimizerIfItsNotSet()
        assert isinstance(self.optimizer, optim.Optimizer), "model's optimizer is not defined"
    @property
    def lr(self):
        return self.optimizer.param_groups[0]['lr']
    
    @lr.setter
    def lr(self, value):
        self.changeLearningRate(value)
        
    @property
    def learningRate(self):
        return self.optimizer.param_groups[0]['lr']
    
    @learningRate.setter
    def learningRate(self, value):
        self.changeLearningRate(value)
        
    def changeLearningRate(self, newLearningRate):
        self.tryToSetDefaultOptimizerIfItsNotSet()
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = newLearningRate
    
    def divideLearningRate(self,factor):
        self.changeLearningRate(self.optimizer.param_groups[0]['lr']/factor)
    
    def batchDatapreparation(self,indexesIndex, indexes, inputs, outputs, batchSize):
        #kkk do parallel datapreparation
        batchIndexes = indexes[indexesIndex*batchSize:indexesIndex*batchSize + batchSize]
        appliedBatchSize = len(batchIndexes)
        
        batchInputs = inputs[batchIndexes].to(self.device)
        batchOutputs = outputs[batchIndexes].to(self.device)
        return batchInputs, batchOutputs, appliedBatchSize
    
    def saveModel(self, bestModel, savePath):
        torch.save({'className':self.__class__.__name__,'classDefinition':inspect.getsource(self.__class__),'inputArgs':self.inputArgs,
                    'model':bestModel}, savePath)
        #kkk model save subclass definition for i.e. if there is some property of this object has a encoder class I should save their definitions also
    
    @classmethod
    def loadModel(cls, savePath):
        bestModelDic = torch.load(savePath)
        exec(bestModelDic['classDefinition'], globals())
        classDefinition = globals()[bestModelDic['className']]
        emptyModel = classDefinition(**bestModelDic['inputArgs'])
        emptyModel.load_state_dict(bestModelDic['model'])
        return emptyModel

    def trainModel(self, trainInputs, trainOutputs, valInputs, valOutputs, criterion, numEpochs, savePath, tensorboardPath=''):
        self.havingOptimizerCheck()
        randomId=randomIdFunc()
        savePath+='_'+randomId
        print(f'model will be saved in {savePath}')
        os.makedirs(os.path.dirname(savePath), exist_ok=True)
        if tensorboardPath:
            tensorboardPath+randomId
        else:
            tensorboardPath = savePath
        self.tensorboardWriter = tensorboardPath
        
        self.train()
        bestValScore = float('inf')
        patienceCounter = 0
        bestModel = None
        bestModelCounter = 1
        
        def checkPatience(valScore, bestValScore, patienceCounter, epoch, bestModel, bestModelCounter):
            if valScore < bestValScore:
                bestValScore = valScore
                patienceCounter = 0
                bestModel = self.state_dict()
                bestModelCounter += 1
            else:
                patienceCounter += 1
                if patienceCounter >= self.patience:
                    print(f"Early stopping! in {epoch+1} epoch")
                    raise StopIteration
            
            if patienceCounter == 0 and (bestModelCounter -1 ) % self.saveOnDiskPeriod == 0:
                # Save the best model to the hard disk
                self.saveModel(bestModel, savePath)
            
            return bestValScore, patienceCounter, bestModel, bestModelCounter
        
        # Create random indexes for sampling
        indexes = torch.randperm(trainInputs.shape[0])
        batchIterLen = len(trainInputs)//self.batchSize if len(trainInputs) % self.batchSize == 0 else len(trainInputs)//self.batchSize + 1
        for epoch in range(numEpochs):
            trainLoss = 0.0
            
            for i in range(0, batchIterLen):
                self.optimizer.zero_grad()
                
                batchTrainInputs, batchTrainOutputs, appliedBatchSize = self.batchDatapreparation(i, indexes, trainInputs, trainOutputs, self.batchSize)
                
                batchTrainOutputsPred = self.forward(batchTrainInputs)
                loss = criterion(batchTrainOutputsPred, batchTrainOutputs)
                
                loss.backward()
                self.optimizer.step()
                
                trainLoss += loss.item()#kkk add l1 and l2 regularization
                #kkk add layer based l1 and l2 regularization
            
            epochLoss = trainLoss / len(trainInputs)
            self.tensorboardWriter.add_scalar('train loss', epochLoss, epoch + 1)
            print(f"Epoch [{epoch+1}/{numEpochs}], aveItemLoss: {epochLoss:.6f}")
            
            valScore = self.evaluateModel(valInputs, valOutputs, criterion, epoch + 1, 'eval')
            bestValScore, patienceCounter, bestModel, bestModelCounter = checkPatience(valScore, bestValScore, patienceCounter, epoch, bestModel, bestModelCounter)
        
        print("Training finished.")
        
        # Save the best model to the hard disk
        self.saveModel(bestModel, savePath)
        
        # Load the best model into the current instance
        self.load_state_dict(bestModel)
        
        # Return the best model
        return self
    
    def evaluateModel(self, inputs, outputs, criterion, stepNum=0, evalOrTest='Test'):
        self.eval()
        evalLoss = 0.0
        
        with torch.no_grad():
            indexes = torch.arange(len(inputs))
            for i in range(0, len(inputs), self.evalBatchSize):
                batchEvalInputs, batchEvalOutputs, appliedBatchSize = self.batchDatapreparation(i, indexes, inputs, outputs, batchSize=self.evalBatchSize)
                
                batchEvalOutputsPred = self.forward(batchEvalInputs)
                loss = criterion(batchEvalOutputsPred, batchEvalOutputs)
                
                evalLoss += loss.item()
            
            evalLoss /= inputs.shape[0]
            if hasattr(self, 'tensorboardWriter'):
                self.tensorboardWriter.add_scalar(f'{evalOrTest} loss', evalLoss, stepNum)
            return evalLoss
