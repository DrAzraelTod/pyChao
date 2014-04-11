#!/bin/bash
export PYTHONIOENCODING=utf-8
#stdbuf -oL -eL nohup ./freenode.sh 0<&- &> grep -v "PING :" >> ./log/freenode.log &
#stdbuf -oL -eL nohup ./euirc.sh 0<&- &> grep -v "PING :" >> ./log/euirc.log &
stdbuf -oL -eL nohup ./freenode.sh 2>&1 | stdbuf -oL -eL grep -v "PING :" >> ./log/freenode.log &
stdbuf -oL -eL nohup ./euirc.sh 2>&1 | stdbuf -oL -eL grep -v "PING :" >> ./log/euirc.log &
