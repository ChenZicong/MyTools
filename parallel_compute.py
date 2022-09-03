## 计算函数
def _dfunc(_cols):
    ## processing ...
    sub_iv_dict = {}
    sub_df_dict = {}
    
    for _col in _cols:
        sub_iv_dict[_col] = 0.0
        sub_df_dict['woe_'+_col] = pd.Series([])
    
    return sub_iv_dict, sub_df_dict


## 对列并行计算
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
