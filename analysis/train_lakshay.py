from bif_lakshay import *
from features_lakshay import *
from fit_lakshay import *
from globals_lakshay import MAX_DEG

def getCCcoeff(ccs,present_files,ss=225,p="n",ft_thresh=100):
    cc_coeff = {}
    for v in ccs: 
        files = []            
        for f in present_files:
            curr_cc = f.split("-")[0] 
            if v == curr_cc :
                files.append(f)       
        cc_mp = get_feature_degree(files,ss=ss,p=p,ft_thresh=ft_thresh)
        coeff = getCC(files, cc_mp,p=p)
        cc_coeff[v] = coeff[v]
        #     getRed(files,p="y")
    return cc_coeff 

def getCoeff(cc_coeff):
    vals = {}
    degree = 0
    for cc in cc_coeff:
        coeff = cc_coeff[cc]
        if cc not in vals :
            vals[cc] = {}
        for trace in coeff:
            i = 1
            for feature in trace:
                if i not in vals[cc]:
                    vals[cc][i] = []
                degree = len(feature)-1
                vals[cc][i].append(feature)
                i+=1
    new_vals = {}
    coe = []
    coeff_count = degree+1
    for i in range(0,coeff_count):
        coe.append("c"+str(i))
    for cc in vals:
        new_vals[cc] = {}
        for i in vals[cc]:
            new_vals[cc][i] = {}
            c_val = {}
            for x in range(0,coeff_count):
                c_val["c"+str(x)] = []
            for ft in vals[cc][i]:
                for x in range(0,coeff_count):
                    c_val[coe[x]].append(ft[x])
            for x in range(0,coeff_count):
                new_vals[cc][i][coe[x]] = c_val[coe[x]]
    return vals, new_vals

def getGaussianParams(vals):
    cc_gaussian_params = {}
    for cc in vals :
        if len(list(vals[cc].keys()))==0 :
            continue
        # Taking the first feature only
        data = vals[cc][1]
        cc_coeff_mean = np.mean(data,axis=0)
        coeff_var = np.cov(data, rowvar=False)
        iden = np.identity(len(cc_coeff_mean))
        cc_coeff_var = coeff_var * iden
        cc_gaussian_params[cc] = {
            'mean' : cc_coeff_mean,
            'covar' : cc_coeff_var
        }
    return cc_gaussian_params

def train(var, present_files,ss=225):
    cc_coeff = getCCcoeff(var,present_files,ss=ss,ft_thresh=1)
    vals, new_vals = getCoeff(cc_coeff)
    cc_gaussian_params = getGaussianParams(vals)
    return vals, new_vals, cc_gaussian_params