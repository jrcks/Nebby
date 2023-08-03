from bif_lakshay import *
from features_lakshay import *
from fit_lakshay import *
from train_lakshay import *
from test_lakshay import *
import os
import globals_lakshay
import pickle

'''
For getting the bytes in file trace
run-lakshay.py -b filenames
For getting the features
run-lakshay.py -f filenames
For getting the polynomial fit of each feature and the mse error seen while fitting the polynomial with degree 1 to MAX_DEG
run-lakshay.py -c filenames 
For training the model on train and saving the parameters of the model
run-lakshay.py -t output_file folder_name
For testing the model on known traces and getting the accuray
run-lakshay.py -a param_file folder_name
'''

ccs = ['bic','dctcp','highspeed','htcp','lp','nv','scalable','vegas','veno','westwood','yeah','cubic','reno']

cmd=sys.argv[1][1]
files=sys.argv[2:]

options=['b','f','c','t','a']
if cmd not in options:
    print("Incorrect flag please check the file run-lakshay.py")
    exit()

if cmd == 'b':
    flows = run(files, "y")
elif cmd == "f":
    for file in files:
        time, data, features = get_plot_features(file, "y")
elif cmd == "c":
    cc_coeff = showCC(files,ss=225,p='y',ft_thresh=1,max_deg=5)
elif cmd == "t":
    save_file = files[0]
    folder = files[1]
    train_files = []
    globals_lakshay.PATH = folder +  "/"
    for file in os.listdir(folder):
    # Check whether file is required
        if file.endswith("-tcp.csv"):
            file_name = file[:-8]
            train_files.append(file_name)

    vals, new_vals, cc_gaussian_params = train(ccs,train_files)
    
    output = {}
    output['vals'] = vals
    output['new_vals'] = new_vals
    output['cc_gaussian_params'] = cc_gaussian_params 

    with open(save_file, "wb") as f:
        pickle.dump(output, f)
elif cmd == "a":
    param_file = files[0]
    folder = files[1]
    test_files = []
    globals_lakshay.PATH = folder +  "/"
    for file in os.listdir(folder):
    # Check whether file is required
        if file.endswith("-tcp.csv"):
            file_name = file[:-8]
            test_files.append(file_name)
    with open(param_file, "rb") as f:
        param_dict = pickle.load(f)
    var = param_dict['vals']
    cc_gaussian_params = param_dict['cc_gaussian_params']
    run_and_get_accuracy(cc_gaussian_params, ccs, test_files)
exit()