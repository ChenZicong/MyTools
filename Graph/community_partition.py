# coding: utf-8
# @Author: ChenZicong
# @Date: 20211230

import networkx
from community import community_louvain

# 图分割,识别聚集团伙,并把团伙内实体控制在100以下
def partition(id_list, G, v_df, e_df):
    _nodelist = id_list
    _edgelist = []
    for node_i in range(len(_nodelist)):
        for node_j in range(node_i+1,len(_nodelist)):
            if node_i != node_j and G.has_edge(_nodelist[node_i], _nodelist[node_j]):
                _edgelist.append((node_i, node_j))
                
    vertices_t_d = v_df.loc[v_df['id'].isin(_nodelist),:]
    edges_t_d = e_df.loc[((e_df['src']+e_df['dst']).isin([v1+v2 for v1,v2 in _edgelist]))|
                         ((e_df['src']+e_df['dst']).isin([v2+v1 for v1,v2 in _edgelist])),:]
    _g_t_d = networkx.Graph()
    
    _n_t_d = list(_vertices_t_d['id'].values)
    _f_t_d = [t[1] for t in _vertices_t_d[['label']].T.to_dict().items()]
    _g_t_d.add_nodes_from([(t[0],t[1]) for t in zip(_n_t_d,_f_t_d)])
    
    _r_t_d = [t[1] for t in _edges_t_d[['relation','weight']].T.to_dict().items())]
    _e_t_d =[(t[e],t[1]) for t in _edges_t_d[['src','dst']].values]
    _g_t_d.add_edges_from([(t[0][0],t[0][1],t[1]) for t in zip(_e_t_d,_r_t_d)])
    
    _best_community = community_louvain.best_partition(_g_t_d, random_state=202210, weight='weight')
    _community = pd.DataFrame({'id':_best_community.keys(), 'component':_best_community.values()})
    _community = _community.merge(_vertices_t_d[['id','label']], on='id', how='left')

    if len(set(_best_community.values()))==1:
        return _community, []
      
    c_counts = _community.loc[_community.label.isin(['nodoubt',"big_amt','black','doubt_report','doubt_norepprt']),'component']
    c_lt100 = list(c_counts[c_counts<100].index)
    c_ge100 = list(c_counts[c_counts>=100].index)
    
    coms_lt100_df = _community.loc[_community.component.isin(c_1t100),:]                                      
    
    coms_ge100_ids = []
    if len(c_ge100)>0:
        for c in c_ge100:
            coms_ge100_ids.append(list(_community.loc[_community.component==c,'id'].values))

    return coms_lt100_df, coms_ge100_ids


# vertices_t_d和edges_t_d是点和边数据集, g_t_d_是通过networkx构造的图文件
# resultG_pd包含待分割图中的团伙号-实体号
coms_lt100_df_list = []
coms_all = list(set(resultG_pd['component']))
for c in coms_all:
    _id_list = list(resultG_pd.loc[resultG_pd.component==c,'id'].values)
    coms_lt100_df, coms_ge100_ids = partition(_id_list, g_t_d_, vertices_t_d, edges_t_d)

    if len(coms_lt100_df)>0:
        coms_lt100_df_list.append(coms_lt100_df)
                                                     
    while len(coms_ge100_ids)>0:
        id_list = coms_ge100_ids.pop(0)
        coms_lt100_df, coms_ge100_ids_add = partition(_id_list, g_t_d_, vertices_t_d, edges_t_d)

        if len(coms_lt100_df)>0:
            coms_lt100_df_list.append(coms_lt100_df)

        if len(coms_ge100_ids_add)>0:
            coms_ge100_ids.extend(coms_ge100_ids_add)    
