# coding: utf-8

import statsmodels.stats.outliers_influence import variance_inflation_factor

# 共线性分析-CORR
# trainDataWOE为训练集woe编码数据, IV_dict为IV值字典
# SPARK版本: 
#   import pyspark.mllib.stat as st
#   corrsMatrix = st.Statistics.corr(trainDataWOE.select(iv_var_list).rdd.map(lambda row: [e for e in row]))

corrsMatrix = trainDataWOE[iv_var_list].corr(method='pearson').values
del_var_list = []
for i in range(corrsMatrix.shape[0]-1):
     for j in range(i+1, corrsMatrix.shape[0]):
          if corrsMatrix[i,j] >= 0.7:
               v1 = iv_var_list[i]
               v2 = iv_var_list[j]
               del_var = v2 if IV_dict[v1[:-4]]>IV_dict[v2[:-4]] else v1
               print(v1, v2, round(corrsMatrix[i,j], 2), '==> delete var:', del_var)
               del_var_list.append(del_var)
del_var_list = list(set(del_var_list))
select_var = [i for i in iv_var_list if i not in del_var_list]


# 共线性分析-VIF

X = np.matrix(trainDataWOE[select_var])
VIF_list = [variance_inflation_factor(X,i) for i in range(X.shape[1])]
VIF_dict = {}
for i, j in zip(select_var, VIF_list):
     VIF_dict[i] = j
sorted(VIF_dict.items(), key=lambda x: x[1], reverse=True)

