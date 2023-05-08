# Nebby
---
Measurement toolkit for identifying congestion control algorithms in the wild

## Dependancies: 
1. Mahimahi ([install instructions here](http://mahimahi.mit.edu/))

## Running tests:
1. Update choice of client in ```scripts/client.sh```.
2. Launch ```scripts/run_test.sh <descriptor> <pre-ow-delay> <post-ow-delay> <bottleneck linkspeed in Kbps> <Buffer size in BDP>``` For example, ```./run_test.sh sample-test 1 50 200 2```.
3. Run a post test analysis using ```analysis/pif-tcp-perflow.py <descriptor>```. For example, ```python3 pif-tcp-perflow.py sample-test```.

### Notes:
* Run ```scripts/clean.sh``` to clear old files, queues, etc. before a fresh test
* While measuring video, choose a relatively higher bandwidth (>500kbps). 200kbps is sufficient for static webpages.

