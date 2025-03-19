"""主要内容
- Encoder
- Decoder
- FullyConnectedOutput 
  - 全连接输出层
  - 带激活函数，层归一化
"""

import torch 
from torch import nn 
from tpf.att import MultiHead


# 全连接输出层
class FullyConnectedOutput(torch.nn.Module):
    """全连接输出层,使用短接进行微调
    - 特征数先变大再变小
    - 并且是变回原来的大小，这样才能使用短接相加 
    """
    def __init__(self,features=32):
        super().__init__()
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(in_features=features, out_features=features*4),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=features*4, out_features=features),
            torch.nn.Dropout(p=0.1)
        )

        self.norm = torch.nn.LayerNorm(normalized_shape=features,
                                       elementwise_affine=True)

    def forward(self, x):
        # 保留下原始的x,后面要做短接用
        clone_x = x.clone()

        # 单词维度归一化
        x = self.norm(x)

        # 线性全连接运算
        # [b, seq_len, feature_nums] -> [b, seq_len, feature_nums]
        out = self.fc(x)

        # 做短接
        out = clone_x + out

        return out


# 编码器层
class EncoderLayer(nn.Module):
    """编码器层,带补码,使用多头注意力 
    - features:数据的特征维数
    - 编码层是求自注意力
    """
    def __init__(self,features=32):
        super().__init__()
        # 多头注意力
        self.mh = MultiHead(features=features)

        # 全连接输出
        self.fc = FullyConnectedOutput(features=features)

    def forward(self, x, mask):
        # 计算自注意力,维数不变
        # [b, seq_len, feature_nums] -> [b, seq_len, feature_nums]
        score = self.mh(x, x, x, mask)

        # 全连接输出,维数不变
        # [b, seq_len, feature_nums] -> [b, seq_len, feature_nums]
        out = self.fc(score)

        return out



# 解码器层
class DecoderLayer(torch.nn.Module):
    """求y相对x的注意力，带补码，使用多头注意力
    模型对象参数
    - x.shape默认为[B,C,L]
    - x.shape默认为[B,C,L]
    """
    def __init__(self,features=32):
        super().__init__()

        # 自注意力提取输入的特征
        self.mh1 = MultiHead(features=features)
        
        # 融合自己的输入和encoder的输出
        self.mh2 = MultiHead(features=features)
        
        # 全连接输出
        self.fc = FullyConnectedOutput(features=features)

    def forward(self, x, y, mask_pad_x, mask_tril_y):
        # 先计算y的自注意力,维度不变
        # [b, 50, 32] -> [b, 50, 32]
        y = self.mh1(y, y, y, mask_tril_y)

        # 结合x和y的注意力计算,维度不变
        # [b, 50, 32],[b, 50, 32] -> [b, 50, 32]
        y = self.mh2(y, x, x, mask_pad_x)

        # 全连接输出,维度不变
        # [b, 50, 32] -> [b, 50, 32]
        y = self.fc(y)

        return y



class Encoder(torch.nn.Module):
    def __init__(self,features=32):
        super().__init__()
        self.layer_1 = EncoderLayer(features=features)
        self.layer_2 = EncoderLayer(features=features)
        self.layer_3 = EncoderLayer(features=features)

    def forward(self, x, mask):
        x = self.layer_1(x, mask)
        x = self.layer_2(x, mask)
        x = self.layer_3(x, mask)
        return x



class Decoder(torch.nn.Module):
    """解码器
    模型对象参数
    - x:[B,L,C]
    - y:[B,L,C]
    - mask_pad_x:[B,1,L,L],01布尔矩阵
    - mask_tril_y:[B,1,L,L],01布尔矩阵
    """
    def __init__(self,features=32):
        super().__init__()

        self.layer_1 = DecoderLayer(features=features)
        self.layer_2 = DecoderLayer(features=features)
        self.layer_3 = DecoderLayer(features=features)

    def forward(self, x, y, mask_pad_x, mask_tril_y):
        """多层解码器变换，每次输入都是编码器x，即x不变 
        """
        y = self.layer_1(x, y, mask_pad_x, mask_tril_y)
        y = self.layer_2(x, y, mask_pad_x, mask_tril_y)
        y = self.layer_3(x, y, mask_pad_x, mask_tril_y)
        return y
