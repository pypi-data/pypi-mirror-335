import torch
from qusi.internal.hadryss_model import Hadryss
from torch import Tensor
from torch.nn import Module, Linear, Sigmoid, ReLU, Conv2d, Conv1d


class SingleDense(Module):
    def __init__(self):
        super().__init__()
        self.dense = Linear(in_features=3500, out_features=1)
        self.sigmoid = Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        x = self.dense(x)
        x = self.sigmoid(x)
        x = torch.reshape(x, [-1])
        return x


class TwoConOneDense(Module):
    def __init__(self):
        super().__init__()
        self.activation = ReLU()
        self.convolution0 = Conv1d(in_channels=1, out_channels=8, kernel_size=100, stride=100)
        self.convolution1 = Conv1d(in_channels=8, out_channels=16, kernel_size=10, stride=10)
        self.dense0 = Linear(in_features=3*16, out_features=1)
        self.sigmoid = Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        x = torch.reshape(x, [-1, 1, 3500])
        x = self.convolution0(x)
        x = self.activation(x)
        x = self.convolution1(x)
        x = self.activation(x)
        x = torch.reshape(x, [-1, 3*16])
        x = self.dense0(x)
        x = self.sigmoid(x)
        x = torch.reshape(x, [-1])
        return x


class MultiDense(Module):
    def __init__(self):
        super().__init__()
        self.activation = ReLU()
        self.dense0 = Linear(in_features=3500, out_features=100)
        self.dense1 = Linear(in_features=100, out_features=1)
        self.sigmoid = Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        x = self.dense0(x)
        x = self.activation(x)
        x = self.dense1(x)
        x = self.sigmoid(x)
        x = torch.reshape(x, [-1])
        return x


class SingleConvolution(Module):
    def __init__(self):
        super().__init__()
        self.activation = ReLU()
        self.convolution0 = Conv1d(in_channels=1, out_channels=8, kernel_size=100, stride=100)
        self.dense0 = Linear(in_features=35, out_features=1)
        self.sigmoid = Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        x = torch.reshape(x, [-1, 1, 3500])
        x = self.convolution0(x)
        x = self.activation(x)
        x = torch.reshape(x, [-1, 35])
        x = self.dense0(x)
        x = self.sigmoid(x)
        x = torch.reshape(x, [-1])
        return x


if __name__ == '__main__':
    x_ = torch.rand([1000, 3500])
    model = Hadryss.new()
    y_ = model(x_)
    torch.onnx.export(model, x_, 'custom_model.onnx', input_names=['light_curve'], output_names=['heart_beat_confidence'])