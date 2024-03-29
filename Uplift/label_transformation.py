# coding: utf-8
# @Author: ChenZicong
# @Date: 20221231
# pyspark

#################################### 标签01转换法 ####################################
####### label为原标签，label_new为新标签（二分类变量）
####### 当分组为处理组时，原标签为1时，则新标签为1，否则为0
####### 当分组为对照组时，原标签为0时，则新标签为1，否则为0

data = data.withColumn('label_new', 
                       f.when( ((data['group']==1)&(data['label']==1)) 
                              |((data['group']==0)&(data['label']==0)),
                              1)
                        .otherwise(0)
                       )


#################################### 标签连续转换法 #####################################
####### label为原标签，label_new为新标签（连续变量），group_prob为属于处理组的概率，采用逆概率加权
####### 当分组为处理组时，则新标签为 label/group_prob
####### 当分组为对照组时，则新标签为 -labe/(1-group_prob)

data = data.withColumn('label_new', 
                       f.when(data['group']==1, data['label']/data['group_prob'])
                        .otherwise(f.lit(-1)*data['label']/(f.lit(1)-data['group_prob']))
                       )


#### 效果评估
import pylift
import seaborn
from matplotlib import pyplot as plt

data_pd = data.toPandas()

# cumulative gain chart
up_eval = pylift.eval.UpliftEval(data_pd['class'], data_pd['label'], data_pd['pred'], n_bins=10)
up_eval.plot('cgains')
pylift.eval.get_scores(data_pd['class'], data_pd['label'], data_pd['pred'], p=0.5*len(data_pd))

# uplift bar
x, y = up_eval.calc(plot_type='uplift', n_bins=10)
x = [round(v,1) for v in x]
plt.subplots(figsize=(10,6))
ax = seaborn.barplot(x, y, color='lightblue')
ax.set_title('Uplift Bar')
ax.set_xlabel('percentage')
ax.set_ylabel('response uplit')
ax.set_ylim(ymin=-0.09, ymax=0.15)
plt.show()
plt.close()

