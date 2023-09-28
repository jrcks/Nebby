For detecting the algorithm that is underlying the current file.
Current support : bic dctcp highspeed htcp lp scalable veno westwood yeah cubic reno
Here: dctcp lp highspeed reno (due to their similarity are taken together) 
Congestion control algorithms for whom support is missing : vegas nv 

Usage :
python3 check_cc_file.py [file_path] [p]
p arguement can take y/n :
    y means plot the bytes-in-flight graph, the fit graph and the error graph. 
    n mean plot nothing just output the result.


Output: 
The flow is as such :
1. First, it is checked if the CC is BBR. 
2. If BBR, the flow stops there. 
3. If it can't be classified, NAN is printed with the error.
4. If it is not BBR, then the flow moves on.
5. The polynomial fit is done to the first feature of the bytes in flight graph. 
6. If the fit produces a huge error, then the flow stops and outputs "It shows very high error". This means that the feature cannot fit a linear, quadratic or cubic polynomial very efficiently and is therefore indicating an unknown CC.
7. If the error is within limits, then we proceed further. 
8. Three groups of CCs are made according to the degree of polynomial they fit the best. The given file is tested against the group of CC which match it's fitted polynomial's degree.
9. A standard normal scaling is done to detect outliers. If the given file is an outlier it is output here. 
10. If it is not an outlier, then we use a Gaussian Naive Bayes classifier to detect the CC it matches to best and output it.


