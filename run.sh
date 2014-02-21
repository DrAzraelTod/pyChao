#!/bin/bash
export PYTHONIOENCODING=utf-8
nohup ./freenode.sh 0<&- &> grep -v "PING :" >> ./log/freenode.log &
nohup ./euirc.sh 0<&- &> grep -v "PING :" >> ./log/euirc.log &
