## Following are the list of the scripts and their usage.
1. bif_trace.py 

```
python3 bif_trace.py file_path
python3 bif_trace.py ../../../../singapore/top1k/t.co-0-50-200-2-tcp.csv
```

Shows the bif trace for the file along with the FFT smoothened trace and the time point of retransmitted packets.

2. bbr_check.py 

```
python3 bbr_check.py file_path
python3 bbr_check.py ../../../../singapore/top1k/t.co-0-50-200-2-tcp.csv
```
NOTE: the file name should reflect the parameters like : website-predelay-postdelay-bandwidth-buffer-tcp.csv
The code has been written to get RTT and BDP from these parameters.


Checks whether a trace is BBR or not. For a BBR trace, the 8RTT probes will be highlighted in RED.

3. define_cc_degree.py
This files requires a lot of files to train on, therefore in the file configure the _PATH_ variable as the folder containing the files for training. These files should be of the format : cc-trial_number-predelay-postdelay-bandwidth-buffer_size-aws-88-60-tcp.csv. 

A variable _total_ is used to define how many files are to be used to decipher the degree. You can change this too.
Usage
```
python3 define_cc_degree.py

```
This scripts does the following
    For each congestion control algorithm:
        For all the files of the given congestion control algorithm:
            Get the first feature:
                Fit the polynomial of degree 1,2,3.
                Get the MSE error of each of them
                Add a regularization error term, defined as sum of coefficients*degree*_lambd_ for all the degree.
                Add MSE error and regularization error for all degree 
                Choos the degree for which we have minimum total error 
                Increase count for this degree
        Assign the degree to a congestion control algorithm for which the number of files are maximum

This files saves a dictionary like : 
```
{'bic': 1,
 'dctcp': 2,
 'highspeed': 2,
 'htcp': 3,
 'lp': 2,
 'nv': 1,
 'scalable': 1,
 'vegas': 3,
 'veno': 3,
 'westwood': 2,
 'yeah': 1,
 'cubic': 3,
 'reno': 2}
```

The number determines what degree that congestion control algorithm will be put against. 

4. train_model.py
This files requires a lot of files to train on, therefore in the file configure the _PATH_ variable as the folder containing the files for training. These files should be of the format : cc-trial_number-predelay-postdelay-bandwidth-buffer_size-aws-88-60-tcp.csv. 

A variable _total_ is used to define how many files are to be used to train the gaussian model. You can change this too.
Usage
```
python3 train_model.py

```

This scripts does the following
    For each congestion control algorithm:
        degree is taken from the cc_degree saved from define_cc_degree.py
        For all the files of the given congestion control algorithm:
            Get the first feature
            Fit the polynomial of given degree
            Save the coefficients
        Run a mahalanobis distance check on these coefficients to detect the outliers. These are those features that are too different from the other files of a congestion control algorithm and will introduce unwanted variance in the model
        Remove the outliers from the training files
        From the left training files choose _trainingcount_ number of files and save them.

        For all the _trainingcount_ files of the given congestion control algorithm:
            Get the first feature:
                Fit the polynomial of given degree.
                Get the coefficients and save them
        From the list of coefficients create a mutlivariate gaussian model with a mean and covariance matrix and save it to 'cc_gaussian_params'

Save 'cc_gaussian_params' to a file. 
cc_gaussian_params dictionary is :
```
{'bic': {'mean': array([0.17247678]), 'covar': array(0.00015149)},
 'dctcp': {'mean': array([-0.00263003,  0.34022997]),
  'covar': array([[ 1.98584418e-07, -8.16134371e-06],
         [-8.16134371e-06,  3.79829475e-04]])},
 'highspeed': {'mean': array([-0.00261203,  0.33692858]),
  'covar': array([[ 1.42782007e-07, -5.25557883e-06],
         [-5.25557883e-06,  2.28803143e-04]])},
 'htcp': {'mean': array([ 0.00515238, -0.11944827,  1.03966524]),
  'covar': array([[ 6.33716335e-07, -1.68116607e-05,  1.25047764e-04],
         [-1.68116607e-05,  4.51640127e-04, -3.40354595e-03],
         [ 1.25047764e-04, -3.40354595e-03,  2.62206290e-02]])},
 'lp': {'mean': array([-0.00262558,  0.33836758]),
  'covar': array([[ 1.84069828e-07, -7.03156668e-06],
         [-7.03156668e-06,  3.07305340e-04]])},
 'nv': {'mean': array([0.34999727]), 'covar': array(0.05381706)},
 'scalable': {'mean': array([0.38280008]), 'covar': array(0.0803832)},
 'vegas': {'mean': array([ 6.32155713e-07, -3.53457533e-04,  6.24558211e-02]),
  'covar': array([[ 3.43779430e-13, -1.36387276e-10,  1.34949393e-08],
         [-1.36387276e-10,  5.51786661e-08, -5.62417524e-06],
         [ 1.34949393e-08, -5.62417524e-06,  6.05796689e-04]])},
 'veno': {'mean': array([ 6.61346499e-05, -7.75879901e-03,  3.83273472e-01]),
  'covar': array([[ 4.32621421e-11, -4.32345838e-09,  1.12259109e-07],
         [-4.32345838e-09,  4.41200881e-07, -1.17493154e-05],
         [ 1.12259109e-07, -1.17493154e-05,  3.42028145e-04]])},
 'westwood': {'mean': array([-0.00185115,  0.24006152]),
  'covar': array([[ 1.18759298e-07, -6.26187536e-06],
         [-6.26187536e-06,  3.49456003e-04]])},
 'yeah': {'mean': array([0.37750383]), 'covar': array(0.00049868)},
 'cubic': {'mean': array([ 3.80876401e-04, -2.32098909e-02,  4.99363114e-01]),
  'covar': array([[ 2.79127268e-09, -1.66105118e-07,  3.28898541e-06],
         [-1.66105118e-07,  1.02664328e-05, -2.08268444e-04],
         [ 3.28898541e-06, -2.08268444e-04,  4.36285000e-03]])},
 'reno': {'mean': array([-0.00262187,  0.33963793]),
  'covar': array([[ 1.08795955e-07, -3.38307755e-06],
         [-3.38307755e-06,  1.34300971e-04]])}}
```
5. test_website.py

Usage
```
python3 test_website.py file_name
python3 test_website.py ../../../../singapore/top1k/t.co-0-50-200-2-tcp.csv

```

This script for the particular website:
    Check if it is BBR
        exit
    If not BBR 
        For all degrees in 1,2,3:
            Fits a polynomial and calculates the total errors
        Chooses a degree which gives minimum total error
        From all the congestion control algorithm that have features which have the same degree
            Calculate the probability density from the mutlivariate gaussian model recieved from 'cc_gaussian_params'
        Display the top 5 most probable congestion control
        Display the top 5 densities
        Display the relative densities
        Display the predicions:
            Based on heurisitic values:
                If the probability density is very low -> a new congestion control might be there
                If the relative density of the 2nd most probable cc is > 0.50, that means we cannot give a good predicion we are confused.
                Else the congestion control with the highest probability density is the best prediction





