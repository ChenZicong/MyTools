# coding: utf-8
# @Author: ChenZicong
# @Date: 20220831

from sklearn.decomposition import PCA

## train_data 为训练数据, test_data为验证数据, vars为X变量, label为Y
pca = PCA(n_components=0.9, whiten=True).fit(train_data[vars])
pca_data_train = pca.transform(train_data[vars])
pca_data_test = pca.transform(test_data[vars])
pca_data = pd.concat([pca_data_train,pca_data_test])

def propagation_matrix(G):
    degrees = G.sum(axis=1)
    if len(degrees[degrees==0])!=0:
        degrees[degrees==0]
        S = G/degrees.reshape((-1,1))
    return S
  
n = len(pca_data)
g_matrix = zeros([n,n])
for i in range(n):
    for j in range(i+1, n):
        dist = sum(np.square(pca_data[i]-pca_data[j]))
        g_matrix[i][j] = dist
        g_matrix[j][i] = dist


#### K近邻LPA算法，调参

accu_dict = {}
pred_df_dict = {}
Y = np.zeros([len(g_matrix[0]),len(set(train_data['label']))])
for (node, label) in enumerate(train_data['label']):
    Y[node][label] = 1

## _g, _n, _alpha 为参数
num = Y.shape[0]*Y.shape[1]
n_list = list(range(5,15,1))
for _g in tqdm(range(0,102,2)):
  
    _g = round(_g*0.01, 2)
    _g_matrix = np.exp(-g * g_matrix)   
    # _g_matrix -= np.identity(g_matrix_.shape[0])
    _g_matrix[:, len(list(train_data['label'])):] = 0.0
    S = propagation_matrix(_g_matrix)
  
    for _n in n_list:
      
        ind = np.argsort(S,axis=1)[:,:-_n]
        SS = S.copy()
        for i in range(len(SS)):
            SS[i,ind[i]] = 0
            
        for _alpha in range(21):
            _alpha = round(_alpha*0.05,2)
            F_old = Y.copy()

            ## 预测
            for i in range(100):
                _F = _alpha*np.matmul(SS,F_old)+(1-_alpha)*Y
            
            if sum(_F==F_old).sum()==num:
                break
                
            F_old = _F.copy()
            all_pred = np.argmax(_F, axis=1)
            pred_test = all_pred[len(train_data['label']):]  # 选取验证集客户
            
            ## 评估
            accu = sum(test_data['label']==pred_test)/len(test_data)
            y_test = np.array(test_data['label'])
            pred_test = np.array(pred_test)
            pred_df = pd.crosstab(y_test, pred_test)
            accu_dict[f"gamma{_g}_slimit{_n}_alpha{alpha}"] = accu
            pred_df_dict[f"gamma{_g}_slimit{_n}_alpha{alpha}"] = pred_df

