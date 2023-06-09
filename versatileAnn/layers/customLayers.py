# versatileAnn\layers\customLayers.py
import torch.nn as nn

class CustomLayer(nn.Module):
    def __init__(self, innerSize, outterSize, activation=None, dropoutRate=None, normalization=None, regularization=None):
        super(CustomLayer, self).__init__()
        self.innerSize = innerSize
        self.outterSize = outterSize
        self.activation = activation
        self.dropoutRate = dropoutRate
        self.normalization = normalization
        if regularization:
            assert isinstance(regularization, (list, set)), "Regularization should be a list or set"
            assert len(regularization) == 2, "Regularization should have a length of 2"
            assert regularization[0] in [None,'l1','l2'],'regularization type should be either None , "l1", "l2"'
            self.regularization=regularization
        else:
            self.regularization=None

        layers = [nn.Linear(innerSize, outterSize)]

        if normalization is not None:
            assert normalization in ['batch', 'layer'], f"Invalid normalization option: {normalization}"
            if normalization == 'batch':
                normLayer = nn.BatchNorm1d(outterSize)
            else:
                normLayer = nn.LayerNorm(outterSize)
            layers.append(normLayer)

        if activation is not None:
            layers.append(activation)

        if dropoutRate:
            assert isinstance(dropoutRate, (int, float)), f"dropoutRateType={type(dropoutRate)} is not int or float"
            assert 0 <= dropoutRate <= 1, f"dropoutRate={dropoutRate} is not between 0 and 1"
            drLayer = nn.Dropout(p=dropoutRate)
            layers.append(drLayer)

        self.layer = nn.Sequential(*layers)

    def forward(self, x):
        return self.layer(x)


class linLReluNormDropout(CustomLayer):
    def __init__(self, innerSize, outterSize, leakyReluNegSlope=0.05, dropoutRate=None, normalization='layer', regularization=None):
        activation = nn.LeakyReLU(negative_slope=leakyReluNegSlope)
        super(linLReluNormDropout, self).__init__(innerSize, outterSize, activation, dropoutRate, normalization, regularization=regularization)


class linLSigmoidNormDropout(CustomLayer):
    def __init__(self, innerSize, outterSize, dropoutRate=None, normalization='layer', regularization=None):
        activation = nn.Sigmoid()
        super(linLSigmoidNormDropout, self).__init__(innerSize, outterSize, activation, dropoutRate, normalization, regularization=regularization)