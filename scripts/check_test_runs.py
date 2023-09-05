import os
no_wget = []
path="../../16_1k"
for f in os.listdir(path):
    if "udp.csv" in f :
        continue
    size = os.path.getsize(path + "/" + f)
    if size < 20000 :
        no_wget.append(f)
output_file=path+"_results.txt"
with open(output_file, 'w') as f:
    for file_name in no_wget:
        f.write(file_name + '\n')
print("Saved the results of this test run in ", output_file)