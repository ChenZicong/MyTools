import torch  
import torch.nn as nn  
import torch.nn.functional as F 

# R-GCN
class GraphConvolutionLayer(nn.Module):
    def __init__(self, in_features, out_features, activation, edge_type_num, dropout_rate=0.):
        super(GraphConvolutionLayer, self).__init__()
        self.edge_type_num = edge_type_num
        self.out_features = out_features

        self.edgeType_linears = nn.ModuleList()        
        # self.edgeType_linears：
        # GCN卷积层中的W参数，其实就是对node-feature的线性变换
        # 在RGCN中，对每一种relation，分别定义一个GCN，实质就是定义该GCN的W参数，
        # 有R种relation，就定义R个W，用于在不同关系的GCN中，学习该关系下node-feature

        for _ in range(self.edge_type_num):
            self.edgeType_linears.append(nn.Linear(in_features, out_features))
        self.self_linear = nn.Linear(in_features, out_features)
        self.activation = activation
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, n_tensor, adj_tensor, h_tensor=None):
        # adj_tensor - torch.Size([batchsize, num_edgeTypes, num_nodes, num_nodes])
        # n_tensor - torch.Size([batchsize, num_nodes, node_feat_dim])
        # h_tensor 用于扩展RGCN的层数，搭建两层或三层RGCN时，h_tensor就是上一层RGCN输出的隐层nodes-embeddings
        if h_tensor is not None:
            node_annotations = torch.cat((n_tensor, h_tensor), -1)
        else:
            node_annotations = n_tensor
		    
        node_feat_all_edge_type = []
        for edge_type in range(self.edge_type_num):
            node_feat_single_edge_type = self.edgeType_linears[edge_type](node_annotations)
            node_feat_all_edge_type.append(node_feat_single_edge_type)

        output = torch.stack(node_feat_all_edge_type, dim=1)
		    
		    # 用num_edgeTypes个GCN(对应的W参数保存于self.edgeType_linears)处理不同关系下的node-feature
        # 将同一类型边的不同邻居特征聚合
        output = torch.matmul(adj_tensor, output) # adj_tensor(32,4,9,9) * output(32,4,9,128)
        # 将不同边类型特征进一步聚合为总邻居特征
        out_sum = torch.sum(input=output, dim=1) # out_sum(32,9,128)
        
        # 自身特征映射:		
        node_self_annotation = self.self_linear(node_annotations) # node_self_annotation(32,9,128)
        # 将总邻居特征与自身特征聚合
        output = out_sum + node_self_annotation # output(32,9,128)
        output = self.activation(output) if self.activation is not None else output
        output = self.dropout(output)
        return output
