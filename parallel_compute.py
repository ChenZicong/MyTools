import pandas as pd
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed


## 计算函数自定义
def _dfunc(_cols):
    sub_iv_dict = {}
    sub_df_dict = {}
    
    for _col in _cols:
        # IV结果
        sub_iv_dict[_col] = 0.0
        # WOE转换结果
        sub_df_dict['woe_'+_col] = pd.Series([])
    
    return sub_iv_dict, sub_df_dict


## 对列并行计算 cols为列名list
cols = ['var1','var2','var3']
nwork = len(cols)//CPUS
result = Parallel(n_jobs=CPUS)(
    delayed(_dfunc)(sub_cols) for sub_cols in [cols[i:i+nwork] for i in range(0, len(cols), nwork)]
)


## 汇集并发结果
IV_dict = {}
X = pd.DataFrame()

for _iv, _df in tqdm(result):
    IV_dict.update(_iv)
    
    for _col, _values in _df.items():
        X[_col] = _values

del result
