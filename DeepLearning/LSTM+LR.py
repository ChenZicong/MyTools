# coding: utf-8
# @Author: ChenZicong
# @Date: 20211231

# train_data_ts 为时间序列数据，6个通道，16个日期
train_ts = train_data_ts.values.reshape((-1,6,16)
test_ts = test_data_ts.values.reshape((-1,6,16))
                                       
# train_data_var 为各类训练特征
train_var = train_data_var.values
test_var = test_data_var.values
                                            
# 预测目标Y
train_y = train_data_y.values
test_y = test_data_y.values

train_ts = torch.tensor(train_ts, dtype=torch.float32)
train_var = torch.tensor(train_var, dtype=torch.float32)
train_y = torch.tensor(train_y, dtype=torch.long)
                                        
test_ts = torch.tensor(test_ts, dtype=torch.float32)
test_var = torch.tensor(test_var, dtype=torch.float32)
test_y = torch.tensor(test_y, dtype=torch.long)
                                        
dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

class WrappedDataLoader:
    def __init__(self, dl, func):
        self.dl = dl
        self. func = func
                                        
    def len(self):
        return len(self.dl)

    def __iter__(self):
        batches = iter(self.dl)
        for b in batches:
        yield (self.func(*b))
  
def preprocess(x1, x2, y):
    return x1.to(dev), x2.to(dev), y.to(dev)
                                        
bs = 10000
train_ds = TensorDataset(train_ts, train_var, train_y)
train_dl = DataLoader(train_ds, batch_size=bs, shuffle=True)
train_dl = WrappedDataLoader(train_dl, preprocess)
test_ts_gpu = test_ts.to(dev)
test_var_gpu = test_var.to(dev)
test_y_gpu = test_y.to(dev)

class Rnn(nn.Module):
    def __init__(self, in_dim, hidden_dim, add_dim, n_layer, n_classes):
        super(Rnn, self).__init__()
        self.n_layer = n_layer
        self.hidden_dim = hidden_dim
        self.bn1 = nn.BatchNorm1d(num_features=in_dim, momentum=0.2)
        self.lstm = nn.LSTM(in_dim, hidden_dim, n_layer, batch_first=True)
        self.bn2 = nn.BatchNorm1d(num_features=hidden_dim+add_dim, momentum=0.2)
        self.classifier = nn.Linear(hidden_dim+add_dim, n_classes)

    def forward(self, x):
        x_seq, x_add = x
        x_seq = self.bn1(x_seq.transpose(2,1))
        out, (h_n, c_n) = self.lstm(x_seq.transpose(2,1)) # 可以从out中获得最后一层每个t的隐藏状态 h=out[:,-1,:]
        x_seq = h_n[-1, :, :]
        x = torch.cat((x_seq, x_add), dim=1)
        x = self.bn2(x)
        linear = self.classifier(x)
        prob = F.softmax(linear, dim=1)
        return linear, prob
                                        
def metric(y, pred):
    fpr, tpr, thresholds = metrics.roc_curve(y, pred)
    ks = abs(tpr-fpr).max()
    auc = metrics.auc(fpr, tpr)
    return ks, auc
                                        
model = Rnn(16, 8, 17, 2, 2)
model.to(dev)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
                                        
def train(epoch):
    model.train()
    for batch_idx, (inputs_seq, inputs_add, targets) in enumerate(train_dl):
        optimizer.zero_grad()
        inputs =(inputs_seq, inputs_add)
        linear, prob = model(inputs)
        loss = criterion(linear, targets)
        loss.backward()
        optimizer.step()
                                        
        targets = targets.cpu().detach().numpy()
        prob = prob[:,1].cpu().detach().numpy()
        ks, auc = metric(targets, prob)
                                        
        print('Train Batch', batch_idx+1, '=> Loss: %.3f | AUC: %.3f | KS: %.3f (N=%d)' 
              % (loss, auc, ks, inputs_seq. shape[0]), file=train_log)

def test(epoch):
    model.eval()
    with torch.no_grad():
        inputs_seq = test_ts_gpu
        inputs add = test_var_gpu
        targets = test_y_gpu
        inputs = (inputs_seq, inputs_add)
        linear, prob = model(inputs)
        loss = criterion(linear, targets)
                                        
        targets = targets.cpu().detach().numpy()
        prob = prob[:,1].cpu().detach().numpy()
        ks, auc = metric(targets, prob)
                                        
        print('Test Sample', '=> Loss: %.3f | AUC: %.3f | KS: %.3f (N=%d)\n'
              % (loss, auc, ks, inputs_seq.shape[0]), file train_log)
                                        
train_log = open('lstm_model_train.log', mode='w')
for epoch in tqdm(range(300)):
    print('Epoch: %d' % (epoch+1), file=train_log)
    train(epoch)
    test(epoch)
train_log. close()
                                        
model.eval()
f = './model_lstm.pt'
torch.save(model, f)

model = torch.load(f)
                                      
# model.eval()
# test_inputs = tuple(test_ts,test_var)
# traced_script_module = torch.jit.trace(model, test_inputs)
# f = './model_lstm_trace.pt'
# traced_script_module.save(f)
