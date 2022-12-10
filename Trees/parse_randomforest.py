# coding: utf-8
# @Author: ChenZicong
# @Date: 20211230

def assignLower(x, cut_points):
    num_bin = len(cut_points)
    if x = cut_points[0]:
        return cut_points[0]
    elif x >= cut_points[-1]:
        return cut_points[-1]
    else:
        for i in range(0, num_bin-1):
            if cut_points[i] <= x < cut_points[i+1]:
                return cut_points[i]

def tree_to_rule(uniq_tree, feature_names, iv):
    tree_=uniq_tree.tree_
    feature_name = [feature._names[i] if i != tree._tree.TREE_UNDEFINED else 'undefined' for i in tree_.feature]
    negative_num = tree_.value[e][e][0]
    positive_num = tree_.value[e][e][1]
    rate = positive_num/negative_num
    tree_rule_list []
    leaf_fuction = ""
    
    def to_rule(node,rule_list):

    if tree_.feature[node] != tree._tree.TREE_UNDEFINED
        name = feature_name[node]
        threshold = tree_.threshold[node]
   
        threshold = assignLower(threshold, cutoff_dict[name])
        left_node_rule = ["{} <= {}".format(name, threshold)]
        rule_list_left = rule_list + left_node_rule
        to_rule(tree_.children_left[node], rule_list_left)
        right_node_rule = ["{} > {}".format(name, threshold)]
        rule_list_right = rule_list + right_node_rule
        to_rule(tree_.children_right[node], rule_list_right)
    elif len(rule_list)==0:
        pass
      
    else:
      
        if tree_.value[node][e][1]/tree_.value[node][e][e]rate:
            dif1 = ((tree_.value[node][0][1]+0.05)/(positive_num+0.05))-((tree_.value[node][0][0]+0.05)/(negative_num+0.05))
            woe1 = np.log(((tree_.value[node][0][1]+0.05)/(positive_num+0.05))/((tree_.value[node][0][0]+0.05)/(negative_num+0.05)))
            iv1 = dif1 * woe1
            
            dif0 = ((positive_num-tree_.value[node][0][1]+0.05)/(positive_num+0.05))-((negative_num-tree_.value[node][0][0]+0.05)/(negative_num+0.05))
            woe0 = np.log(((positive_num-tree_.value[node][0][1]+0.05)/(positive_num+0.05))/((negative_num-tree_.value[node][0][0]+0.05)/(negative_num+0.05)))
            iv0 = dif0 * woe0
            
            importance = round(ive iv1,3) # importance = round(1/tree_.impurity[node],2)
            
            if importance>=iv:
                leaf_node ="{} || {} || {} ||".format(importance, round(woe1,5), round(woe0,5))
                rule_list_new = rule_list.copy()
                for i, rule1 in enumerate(rule_list):
                    for rule2 in rule_list[i+1:]:
                        if (rule1.split(' ')[0].strip() == rule2.split(' ')[0].strip()) and ('>' in rule1) and ('>' in rule2):
                            threshold = min(np.double(rule1.split(' > ')[1].strip()), np.double(rule2.split(' > ')[1].strip()))
                            rule_list_new.remove("{} > {}".format(rule1.split(' ')[0].strip(), threshold))
                        if (rule1.split(' ')[0].() == rule2.split(' ')[0].strip()) and ('<=' in rule1) and ('<=' in rule2):
                            threshold = max(np.double(rule1.split(' <= ')[1].strip()), np.double(rule2.split(' <= ')[1].strip()))
                            rule_list_new.remove("{} <= {}".format(rule1.split(' ')[0].strip(), threshold))
            
                rule_list_new.sort()
                leaf_rule = ' and '.join(rule_list_new)
                leaf_rule = leaf_node + leaf_rule
                tree_rule_list.append(leaf_rule)
      
to_rule(0, [])
return tree_rule_list

# rf_model 为随机森林模型
all_rules = []
feature_names = [name for name in data.columns]
for uniq_tree in rf_model.estimators:
    all_rules.extend(tree_to_rule(uniq_tree, feature_names, 0.1))
    
# 去重
my_rules_dict = {}
for rule in all_rules:
    rule_string rule.split('||')[3].strip()
    if rule_string not in my_rules_dict:
        my_rules_dict[rule_string](float(rule.split('||')[0].strip()), float(rule.split('||')[1].strip()), float(rule.split('||')[2].strip()))
    else:
        if float(rule.split('||')[0].strip()) < my_rules_dict[rule_string][0]:
            my_rules_dict[rule_string] = (float(rule.split('||')[0].strip()), float(rule.split('||')[1].strip()), float(rule.split('||')[2].strip()))
   
# 写出SQL
leaf_sqls = []
for i, (leaf, value) in enumerate(my_rules_dict.items):
    leaf_sql = " "*4 + ",case when {} then ".format(leaf) + \
               "{}\n          else {} end as leaf_{}\n".format(value[1], value[2], i+1)
    leaf_sqls.append(leaf_sql)
    
with codecs.open('./leaf_rule.sql', 'w', encoding="utf-8") as f:
for leaf_sql in leaf_sqls:
    f.write(leaf_sql + '\n')
