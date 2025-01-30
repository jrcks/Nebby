import os
import pickle

# Load the pickled files
script_dir = os.path.dirname(os.path.realpath(__file__))
scaled_vals = pickle.load(open(script_dir + "/final/scaled_vals.txt","rb"))
classifiers = pickle.load(open(script_dir + "/final/classifiers.txt","rb"))
count_to_mp = pickle.load(open(script_dir + "/final/count_to_mp.txt","rb"))
cc_degree = pickle.load(open(script_dir + "/final/cc_degree.txt","rb"))

# Log the unpickled variables
print(scaled_vals)
print("="*20)
print(classifiers)
print("="*20)
print(count_to_mp)
print("="*20)
print(cc_degree)

# Save the pickeled files
pickle.dump(scaled_vals, open(script_dir + "/final/scaled_vals.txt","wb"))
pickle.dump(classifiers, open(script_dir + "/final/classifiers.txt","wb"))
pickle.dump(count_to_mp, open(script_dir + "/final/count_to_mp.txt","wb"))
pickle.dump(cc_degree, open(script_dir + "/final/cc_degree.txt","wb"))