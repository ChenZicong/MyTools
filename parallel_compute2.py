import multiprocessing
from sklearn import LogisticRegression

# 交叉验证调参C
# 训练数据 train_x, train_y

def gs_run(gs):
    gs.fit(train_x, train_y)
    return gs.best_params_, gs_best_score_

results = []
model = LogisticRegression(penalty='l1', solver='saga')

# 多进程计算
pool = multiprocessing.Pool(5)
for C in [0.1, 0.2, 0.3, 0.4, 0.5]:
    param = {"C": [C]}
    gs = GridSearchCV(estimator=model, param_grid=param, scoring='roc_auc', cv=3)
    results.append(pool.apply_async(gs_run, [gs]))
    
pool.close()
pool.join()

param_dict = {}
for i in range(len(results)):
    best_params_, best_score_ = results[i].get()
    param_dict[str(best_params_)] = best_score_
