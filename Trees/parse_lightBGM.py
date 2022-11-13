## 解析lightGBM模型文件，转为SQL

import codecs
import json

def parse_lgb_tree2sql(lgb_tree_json,feature_list,mid_sqls,tree_num,depth=0):
    indent = "    " * (depth+1)
    if 'leaf_value' in lgb_tree_json.keys():
        leaf_value = str(round(lgb_tree_json['leaf_value'],7))
        if(len(mid_sqls)>=1 and 'else'in mid_sqls[-1]):
            cur_sql = indent + leaf_value + ' '
        else:
            cur_sql = indent + leaf_value
        mid_sqls.append(cur_sql)
        return
      
    feat = feature_list[lgb_tree_json['split_feature']]
    threshold = str(round(lgb_tree_json['threshold'],7))
    left_tree_json = lgb_tree_json['left_child']
    right_tree_json = lgb_tree_json['right_child']
    missing_left = lgb_tree_json['default_left']
    
    if missing left:
    
        cur_sql = '(' + feat + ' is hull' + ' or ' + feat + '<=' + threshold + ')'
        mid_sqls.append("{}case when {} then\n".format(indent,cur_sql))
        parse_lgb_tree2sql(left_tree_json,feature_list,mid_sqls,tree_num,depth+1)
        
        mid_sqls.append("\nelse\n".format(indent))
        parse_lgb_tree2sql(right_tree_json,feature_list,mid_sqls,tree_num,depth+1)
        mid_sqls.append("\n{}end".format(indent))
        
    else:
        cur_sql = '(' + feat + ' is null' + ' or ' + feat + ' > ' + threshold + ')'
        mid_sqls.append("{}case when {} then\n".format(indent,cur_sql))
        parse_lgb_tree2sql(right_tree_json,feature_list,mid_sqls,tree_num,depth+1)
        
        mid_sqls.append("\n{}else\n".format(indent))
        parse_lgb_tree2sql(left_tree_json,feature_list,mid_sqls,tree_num,depth+1)
        mid_sqls.append("\n{}end".format(indent))
        
        
def parse_lgb_trees(lgb_model_json):
    tree_sqls = []
    feature_list = lgb_model_json['feature_names']
    
    idx =0
    for single_tree_info in lgb_model_json['tree_info']:
        mid_sqls = []
        single_tree = single_tree_info['tree_structure']
        parse_lgb_tree2sql(single_tree,feature_list,mid_sqls,idx,0)
        tree_sql = ''
        for t_sql in mid_sqls:
            tree_sql = tree_sql + t_sql
        tree_sql = tree_sql + ' as ' + 'tree_' + str(idx) + '_score,'
        idx += 1
        tree_sqls.append(tree_sql +'\n')
    
    tree_sqls[-1] = tree_sqls[-1][:-2]
    return tree_sqls
        
        
lgb_model_json = lgb_model.dump_model(num_iteration=lgb_model.best_iteration)
tree_sql = 'select\n cmid\n,'
for i in range(len(lgb_model_json['tree_info'])):
    tree_sql += "tree_{}_score".format(i)
    if i < len(lgb_model_json['tree_info'])-1:
        tree_sql += " + "
tree_sql += " as score\nfrom"

tree_sqls = parse_lgb_trees(lgb_model_json)
with codecs.open('·/lightGBM_model.sql', 'w', encoding='utf-8') as f:
    f.write(tree_sql + '\n(\n    select\n    cmid,\n')
    for item_sql in tree_sqls:
        f.write(item_sql +'\n')
    f.write(') t')
