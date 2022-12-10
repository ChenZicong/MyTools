# coding: utf-8
# @Author: ChenZicong
# @Date: 20221130

from sklearn import metrics

def auc_ks_graph(pred, targets):

    fpr, tpr, thresholds = metrics.roc_curve(targets, pred)
    AUC = metrics.auc(fpr,tpr)
    KS = abs(tpr-fpr).max()
    print('KS:', round(KS,3))
    print('AUC:', round(AUC,3))
    
    plt.plot(fpr,tpr)
    plt.title('ROC_Curve' + ' ( AUC: ' + str(round(AUC,3)) + ' )')
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()
    
    thresh = [1-var for var in thresholds[1:]]
    plt.plot(thresh, fpr[1:], color='green')
    plt.plot(thresh, tpr[1:], color='orange')
    plt.plot(thresh, tpr[1:]-fpr[1:], linestyle='dashed', color='red')
    plt.title('KS_Curve' + ' ( KS: ' + str(round(KS,3)) + ' )')
    plt.ylabel("Cumulative Rate")
    plt.xlabel('1 - Pred')
    plt.show()
    

def lift_graph(df, pred='score', label='label', r=0.01):

    _df = df.sort_values(pred, ascending=False).reset_index(drop=True)
    lift_dict = dict()
    bad_cnt_list = []
    total_cnt_list = []
    bad_rate_list = []
    pred_list = []
    lift_list = []
    n = np.ceil(len(_df)/20)
    for i in range(20):
        bad_cnt_list.append(_df.loc[i*n:(i+1)*n-1, label].sum())
        total_cnt_list.append(len(_df.loc[i*n:(i+1)*n-1]))
        bad_rate_list.append(_df.loc[i*n:(i+1)*n-1, label].sum()/(len(_df.loc[i*n:(i+1)*n-1])))
        pred_list.append((round(min(_df.loc[i*n:(i+1)*n-1, pred]),3), round(max(_df.loc[i*n:(i+1)*n-1, pred]),3)))
        lift_list.append(_df.loc[:(i+1)*n-1, label].sum()/(r*len(_df.loc[:(i+1)*n-1])))
    
    lift_dict['topN%'] = list(range(5,105,5))
    lift_dict['pred'] = pred_list
    lift_dict['bad_cnt'] = bad_cnt_list
    lift_dict['total_cnt'] = total_cnt_list
    lift_dict['bad_rate'] = bad_rate_list
    lift_dict['lift'] = lift_list
    lift_df = pd.DataFrame(lift_dict)
    print('top 5%: {}'.format(lift_list[0]))
    print('top 10%: {}'format(lift_list[1]))
    print(lift_df)
    
    plt.figure(figsize=(8,5))
    plt.scatter(lift_df['topN%'], lift_df['lift'], s=15)
    plt.plot(lift_df['topN%'], lift_df['lift'])
    plt.xticks(list(range(5,105,5)))
    plt.xlim(0,105)
    plt.yticks(list(range(0,11,1)))
    # plt.ylim(0.5,10)
    plt.title('LIFT_Curve')
    plt.ylabel('LIFT', size=12)
    plt.xlabel('Top N%', size=12)
    plt.show()
