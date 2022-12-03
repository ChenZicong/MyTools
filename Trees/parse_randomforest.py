
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
