#!/bin/bash
# Runs the model chain.
S=${ST_ROOT:-.}/01_스크립트; cd $S; T=HDRK; L=${ST_ROOT:-.}/04_분석/$T
export ST_GRAPH=$L/graph_593.graph ST_THREADS=1 ST_VER=std3
lw(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($2)}')" -ge 14 ]; do sleep 30; done; }
lw; ST_FH_ONLY=S0,S2,S3 ./rslot.sh Rscript 81fh_hdrk.R $T > $L/run_fh_main.log 2>&1
ST_FH_ONLY=S7 ST_MV_STOP=1 Rscript 81fh_hdrk.R $T >> $L/run_fh_main.log 2>&1
lw; ST_FH_ONLY=S4,S5,S6,S8,S9 ./rslot.sh Rscript 81fh_hdrk.R $T > $L/run_fh_sens.log 2>&1 &
lw; ST_FH_ONLY=S10,S11,S12,S13,S14,S16,S18,S19,S20,S21 ./rslot.sh Rscript 81fh_hdrk.R $T > $L/run_fh_sens2.log 2>&1 &
for R in 1-50 51-100 101-150 151-200; do lw; ST_FH_ONLY=S7 ST_MV_RANGE=$R ./rslot.sh Rscript 81fh_hdrk.R $T > $L/run_fh_s7_$R.log 2>&1 & sleep 20; done
wait
ST_FH_ONLY=S7,S17,S44 ./rslot.sh Rscript 81fh_hdrk.R $T >> $L/run_fh_main.log 2>&1
echo "chain done $(date)" >> $L/run_fh_main.log; echo ALLDONE
