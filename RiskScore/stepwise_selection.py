# coding: utf-8

import pandas as pd
import numpy as np
import statsmodels.api as sm
from connect_hive import conn
import warnings
warnings.filterwarnings('ignore')

# stepwise 变量筛选
def stepwise_selection(X, y, initial_list=[], threshold_in=0.01, threshold_out=0.05, verbose=True):

    included = list(intial_list)
    
    while True:
        changed = False
        
        # forward step
        excluded = list(set(X.columns) - set(included))
        new_pval = pd.Series(index = excluded)
        for new_col in excluded:
            model = sm.Logit(y, sm.add_constant(X[included + [new_col]])).fit(disp=False)
            new_pval[new_col] = model.pvalues[new_col]
            best_pval = new_pval.min()
            if best_pval < threshold_in:
                changed = True
                best_feature = new_pval.argmin()
                included.append(best_feature)
                if verbose:
                    print('Add {:30} with p-value {:.6}'.format(best_feature, best_pval))

        # backward step
        model = sm.Logit(y, sm.add_constant(X[inclued])).fit(disp=False)
        pvalues = model.pvalues.iloc[1:]     # Exclude intercept
        worst_pval = pvalues.max()
        if worst_pval > threshold_out:
            changed = True
            worst_feature = pvalues.argmax()
            included.remove(worse_feature)
            if verbose:
                print('Drop {:30} with p-value {:.6}'.format(worst_feature, best_pval))                 

        if not changed:
            break
    
    return included

  
# 读入数据
sql = "select * from hive_database.trainData"
trainData = pd.read_sql(sql, conn)
train_x = trainData.drop('target', axis=1)
train_y = np.array(trainData['target'])

# 筛选变量
selected = stepwise_selection(train_x, train_y)


