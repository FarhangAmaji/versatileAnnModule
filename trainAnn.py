# trainAnn.py
import os
baseFolder = os.path.dirname(os.path.abspath(__file__))
os.chdir(baseFolder)
from annModule import ann
import torch.optim as optim
#%% 
class myAnn(ann):
    def __init__(self):
        super(myAnn, self).__init__()
        self.layer1 = self.linLReluDropout(40, 160, dropoutRate=0.5)
        self.layer2 = self.linLReluDropout(160, 160, dropoutRate=0.8)
        self.layer3 = self.linLReluDropout(160, 1)
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return x
#%%
z1=myAnn()
#%%
'#ccc how to set optimizer manually'
# z1.changeLearningRate(0.001)
# z1.optimizer=optim.Adam(z1.parameters(), lr=0.4)
#%%
