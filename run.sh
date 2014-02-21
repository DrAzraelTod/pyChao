#!/bin/bash
export PYTHONIOENCODING=utf-8
./freenode.sh | grep -v "PING :" > ./log/freenode.log &
./euirc.sh | grep -v "PING :" > ./log/euirc.log
