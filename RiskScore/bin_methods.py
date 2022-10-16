import scipy
import sklearn
import tabulate
import numpy as np

from sklearn.isotonic import IsotonicRegression
from sklearn.cluster import KMeans
from lightgbm import LGBMRegressor

def qcut(x, n):
    _q = np.linspace(0, 100, n, endpoint=False)[1:]
    _x = [_ for _ in x if not np.isnan(_)]
    _c = np.unique(np.percentile(_x, _q, interpolation="lower"))
    return ([_ for _ in _c])

def manual_bin(x, y, cuts):
    _x = [_ for _ in x]
    _y = [_ for _ in y]
    _c = sorted([_ for _ in set(cuts)] + [np.NINF, np.PINF])
    _g = np.searchsorted(_c, _x).tolist()
    _l1 = sorted(zip(_g, _x, _y), key=lambda x: x[0])
    _l2 = zip(set(_g), [[l for l in _l1 if l[0] == g] for g in set(_g)])
    return (sorted([dict(zip(["bin","freq","miss","bads","minx","maxx"],
                             [_1,  len(_2), 0,
                              sum([_[2] for _ in _2]),
                              min([_[1] for _ in _2]),
                              max([_[1] for _ in _2])])) for _1, _2 in _l2],
                    key=lambda x: x["bin"]))


## quantile cut
def qtl_bin(x, y):
    _data = [_ for _ in zip(x, y, ~_np.isnan(x))]
    _x = [_[0] for _ in _data if _[2] == 1]
    _y = [_[1] for _ in _data if _[2] == 1]
    _n = np.arange(2, max(3, min(50, len(np.unique(_x))-1)))
    _p = set(tuple(qcut(_x, _)) for _ in _n)
    
    _l1 = [[_, manual_bin(_x, _y, _)] for _ in _p]
    _l2 = [[l[0],
            min([_["bads"]/_["freq"] for _ in l[1]]),
            max([_["bads"]/_["freq"] for _ in l[1]]),
            scipy.stats.spearmanr([_["bin"] for _ in l[1]], [_["bads"]/_["freq"] for _ in l[1]])[0]
           ] for l in _l1]
    _l3 = [l[0] for l in sorted(_l2, key=lambda x: -len(x[0]))
           if np.abs(round(l[3], 8)) == 1 and round(l[1], 8) > 0 and round(l[2], 8) < 1][0]
    return _l3

    
## isotonic regression
def iso_bin(x, y):
    _data = [_ for _ in zip(x, y, ~np.isnan(x))]
    _x = [_[0] for _ in _data if _[2] == 1]
    _y = [_[1] for _ in _data if _[2] == 1]
    _cor = scipy.stats.spearmanr(_x, _y)[0]
    _reg = IsotonicRegression()
    _f = np.abs(_reg.fit_transform(_x, list(map(lambda y: y*_cor/np.abs(_cor), _y))))
    
    _l1 = sorted(list(zip(_f, _x, _y)), key=lambda x: x[0])
    _l2 = [[l for l in _l1 if l[0] == f] for f in sorted(set(_f))]
    _l3 = [[*set(_[0] for _ in l),
            max(_[1] for _ in l),
            np.mean([_[2] for _ in l]),
            sum(_[2] for _ in l)] for l in _l2]
    _c = sorted([_[1] for _ in [l for l in _l3 if l[2] < 1 and l[2] > 0 and l[3] > 1]])
    _p = _c[1:-1] if len(_c) > 2 else _c[:-1]
    return _p


## kmean clustering
def kmn_bin(x, y):
    _data = [_ for _ in zip(x, y, ~np.isnan(x))]
    _x = [_[0] for _ in _data if _[2] == 1]
    _y = [_[1] for _ in _data if _[2] == 1]
    _n = np.arange(2, max(3, min(50, len(np.unique(_x))-1)))
    _m = [[np.median([_[0] for _ in _data if _[2] == 1 and _[1] == 1])],
          [np.median([_[0] for _ in _data if _[2] == 1])]]
    _c1 = [KMeans(n_clusters=_, random_state=1).fit(np.reshape(_x, [-1,1])).labels_ for _ in _n]
    _c2 = [sorted(_l, key=lambda x: x[0]) for _l in [list(zip(_, x)) for _ in _c1]]
    group = lambda x: [[_l for _l in x if _l[0] == _k] for _k in set([_[0] for _ in x])]
    upper = lambda x: sorted([max([_2[1] for _2 in _1]) for _1 in x])
    _c3 = list(set(tuple(upper(_2)[:-1]) for _2 in [group(_1) for _1 in _c2])) + _m
    
    _l1 = [[_, manual_bin(_x, _y, _)] for _ in _c3]
    _l2 = [[l[0],
            min([_["bads"]/_["freq"] for _ in l[1]]),
            max([_["bads"]/_["freq"] for _ in l[1]]),
            scipy.stats.spearmanr([_["bin"] for _ in l[1]], [_["bads"]/_["freq"] for _ in l[1]])[0]
           ] for l in _l1]
    _l3 = [l[0] for l in sorted(_l2, key=lambda x: -len(x[0]))
           if np.abs(round(l[3], 8))==1 and round(l[1], 8)>0 and round(l[2], 8)<1][0]
    return _l3
    

## gradient boosting
def gbm_bin(x, y):
    _data = [_ for _ in zip(x, y, ~np.isnan(x))]
    _x = [_[0] for _ in _data if _[2] == 1]
    _y = [_[1] for _ in _data if _[2] == 1]
    _cor = scipy.stats.spearmanr(_x, _y)[0]
    _con = "1" if _cor > 0 else "-1"
    _gbm = LGBMRegressor(num_leaves=100, min_child_samples=3, n_estimators=1, random_state=1）
    _gbm.fit(np.reshape(_x, [-1,1]), _y)
    
    _f = np.abs(_gbm.predict(np.reshape(_x, [-1,1])))
    
    _l1 = sorted(list(zip(_f, _x, _y)), key=lambda x: x[0])
    _l2 = [[l for l in _l1 if l[0] == f] for f in sorted(set(_f))]
    _l3 = [[*set(_[0] for _ in l),
            max(_[1] for _ in l),
            np.mean([_[2] for _ in l]),
            sum(_[2] for _ in l)] for l in _l2]
    _c = sorted([_[1] for _ in [l for l in _l3 if l[2] < 1 and l[2] > 0 and l[3] > 1]])
    _p = _c[1:-1] if len(_c) > 2 else _c[:-1]
    return _p



# def miss_bin(y):
#     return ({"bin": 0, "freq": len([_ for _ in y]), "miss": len([_ for _ in y]),
#              "bads": sum([_ for _ in y]), "minx": np.nan, "maxx": np.nan})
  
# def add_miss(d, l):
#     _l = l[:]
#     if len([_ for _ in d if _[2] == 0]) > 0:
#         _m = miss_bin(_[1] for _ in d if _[2] == 0])
#         if _m["bads"] == 0:
#             for _ in ["freq", "miss", "bads"]:
#                 _l[0][_] = _l[0][_] + _m[_]
#         elif _m["freq"] == _m["bads"]:
#             for _ in ["freq", "miss", "bads"]:
#                 _l[-1][_] = _l[-1][_] + _m[_]
#         else:
#             _l.append(_m)
#     return (_l)
