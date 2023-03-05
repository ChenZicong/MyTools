
# train_data_ts 为时间序列数据，6个通道，16个日期
train_ts = train_data_ts.values.reshape((-1,6,16)
test_ts = test_data_ts.values.reshape((-1,6,16))
                                       
# train_data_var 为各类训练特征
train_var = train_data_var.values
test_var = test_data_var.values
                                            
# 预测目标Y
train_y = train_data_y.values
test_y = test_data_y.values
