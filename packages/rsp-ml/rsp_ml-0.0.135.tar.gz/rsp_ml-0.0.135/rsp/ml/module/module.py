import torch
import torch.nn as nn
import torch.nn.functional as F

class SelfAttention(nn.Module):
    def __init__(
            self,
            d_q:int = 2,
            d_k:int = 2,
            d_v:int = 4,
            embed_dim:int = 3
        ):
        super().__init__()

        self.d_q = d_q
        self.d_k = d_k
        self.d_v = d_v

        self.W_q = nn.Parameter(torch.rand(embed_dim, d_q))
        self.W_k = nn.Parameter(torch.rand(embed_dim, d_k))
        self.W_v = nn.Parameter(torch.rand(embed_dim, d_v))
        pass

    def forward(self, X):
        Z = []
        # iterate over batch_size
        for x in X:
            Q = x @ self.W_q    # Queries
            K = x @ self.W_k    # Keys
            V = x @ self.W_v    # Values

            omega = Q @ K.T                                     # omega ...unnormalized attantion weights
            alpha = F.softmax(omega / self.d_k**0.5, dim=0)     # alpha ...normalized attention weights
            z = alpha @ V                                       # z     ...context vector -> attention-weighted version of original query input x_i
            Z.append(z)
        
        Z = torch.stack(Z)
        return Z

class MultiHeadSelfAttention(nn.Module):
    def __init__(
            self,
            num_heads:int,
            d_q:int = 2,
            d_k:int = 2,
            d_v:int = 4,
            embed_dim:int = 3
        ):
        super().__init__()

        self.d_q = d_q
        self.d_k = d_k
        self.d_v = d_v

        self.heads = nn.ModuleList([SelfAttention(d_q, d_k, d_v, embed_dim) for _ in range(num_heads)])

    def forward(self, X):
        return torch.cat([head(X) for head in self.heads], dim=-1)
