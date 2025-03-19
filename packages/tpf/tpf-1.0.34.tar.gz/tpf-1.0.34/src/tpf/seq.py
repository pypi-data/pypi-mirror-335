"""
序列类问题通用方法
"""
import torch 
from torch import nn 


##----------------------------------------------------
## 位置编码 - 开始
##----------------------------------------------------

import math 
torch.manual_seed(73)

# 位置编码层
class PositionEmbedding(nn.Module):
    def __init__(self,seq_len=50,num_embeddings=39,embedding_dim=32):
        super().__init__()

        # pos是第几个词,i是第几个维度,d_model是维度总数
        def get_pe(pos, i, d_model):
            temp = 1e4 ** (i / d_model)
            pe = pos / temp

            if i % 2 == 0:
                return math.sin(pe)
            return math.cos(pe)

        # 初始化位置编码矩阵
        pe = torch.empty(seq_len, embedding_dim)
        for i in range(seq_len):#第几个词
            for j in range(embedding_dim):#第几个维度
                pe[i, j] = get_pe(i, j, embedding_dim)

        pe = pe.unsqueeze(0)

        # 定义为不更新的常量
        self.register_buffer('pe', pe)

        # 词编码层,39=26+10+3
        self.embed = torch.nn.Embedding(num_embeddings, embedding_dim)
        
        # 初始化参数
        self.embed.weight.data.normal_(0, 0.1)

    def forward(self, x):
        # [8, 50] -> [8, 50, 32]
        embed = self.embed(x)

        # 词编码和位置编码相加
        # [8, 50, 32] + [1, 50, 32] -> [8, 50, 32]
        embed = embed + self.pe
        return embed


##----------------------------------------------------
## 位置编码 - 结束
##----------------------------------------------------




























