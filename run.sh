#!/bin/bash
export PYTHONIOENCODING=utf-8
stdbuf -oL -eL nohup ./freenode.sh 0<&- &> grep -v "PING :" >> ./log/freenode.log &
stdbuf -oL -eL nohup ./euirc.sh 0<&- &> grep -v "PING :" >> ./log/euirc.log &
