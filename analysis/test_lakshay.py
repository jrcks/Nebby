from bif_lakshay import *
from features_lakshay import *
from fit_lakshay import *
from train_lakshay import *
from globals_lakshay import MAX_DEG

#TODO Add function for running on unknown files
#TODO Add feature on how to flag unreliable files

def collect_test_data(var, present_files):
    cc_coeff_test = getCCcoeff(var,present_files,ss=225,p="n",ft_thresh=1)
    vals_test, new_vals_test = getCoeff(cc_coeff_test)
    return vals_test, new_vals_test


from scipy.stats import multivariate_normal as mvn
def getPDensity(curr, cc_gaussian_params):
    prob = {}
    for cc in cc_gaussian_params:
        mn = cc_gaussian_params[cc]['mean']
        covar = cc_gaussian_params[cc]['covar']
#         print("CC being checked against",cc)
#         print(np.linalg.det(covar))
        curr_p = mvn.pdf(curr,mean=mn, cov=covar, allow_singular=True)
        prob[cc]=curr_p
    return prob

def get_test_accuracy(vals_test, cc_gaussian_params):
    acc_m = {}
    for cc in vals_test:
        if cc not in acc_m :
            acc_m[cc] = []
        if len(list(vals_test[cc].keys()))==0:
            continue
        data = vals_test[cc][1]
        for curr in data:
            p_dense = getPDensity(curr, cc_gaussian_params)
            acc_m[cc].append(p_dense)
    top = {}
    error = {}
    for cc in acc_m :
        top[cc] = {}
        ind = 0
        for item in acc_m[cc]:
            ccs = np.array(list(item.keys()))
            vals = np.array(list(item.values()))
            if min(vals) == 0:
                if max(vals) < 1 : 
                    # These are not able to matcht with any of the ccs
                    if cc not in error :
                        error[cc] = []
                        error[cc].append(ind)
                        ind+=1
                        continue        
            new_vals = (vals-min(vals))/(max(vals)-min(vals))
            index_list =list(np.argsort(new_vals))
            index_list.reverse()
            cc_list = [ccs[i] for i in index_list]
            vals_list = [vals[i] for i in index_list]
            new_vals_list = [new_vals[i] for i in index_list]
            top[cc][ind] = {}
            top[cc][ind]['cc'] = cc_list[0:3]
            top[cc][ind]['vals'] = vals_list[0:3]
            top[cc][ind]['new_vals'] = new_vals_list[0:3]
            ind+=1
    return acc_m, top, error

def print_confusion_matrix(ccs, top):    
    matrix = []
    for cc in ccs:
        # The underlying CC
        temp = []
        total = len(top[cc].keys())
        cc_index = ccs.index(cc)
        for check_cc in ccs :
            # The CC it gets classified as
            count = 0
            for i in range(0,len(top[cc].keys())):
                if i not in top[cc]:
                    continue
                if top[cc][i]['cc'][0]==check_cc:
                    count+=1
            temp.append(count)
        if total > 0:
            temp.append(float(temp[cc_index])*100/total)
        else :
            temp.append("NA")
        matrix.append(temp)
    rows = [cc for cc in ccs]
    columns = [cc for cc in ccs]
    columns.append("accuracy")
    df = pd.DataFrame(matrix,index=rows,columns=columns)
    print("Rows are the truth. Columns are the classifications")
    print(df)
    return df

def run_and_get_accuracy(train_cc_gaussian_params, ccs, present_files):
    vals, new_vals = collect_test_data(ccs, present_files)
    acc_m, top, error = get_test_accuracy(vals, train_cc_gaussian_params)
    print("Some files were not classfied due to lack of features : ")
    print(error)
    df = print_confusion_matrix(ccs, top)