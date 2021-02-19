#!/bin/sh
alias python=$HOME/local/bin/python
export PATH=${HOME}/local/bin:${HOME}/local/lib64/python3.8/site-packages:${PATH}
export PYTHONPATH=${HOME}/local/lib64/python3.8/site-packages:${PYTHONPATH}
export OPENBLAS_NUM_THREADS=1
cd /home/virtwww/w_s600spb-ru_c99ad702/collector/
CWD="$(pwd)"
#echo $CWD
python sender.py

