#!/bin/bash
# Wait (max 180 s) until the passed-through NVIDIA GPU and /dev/nvidia-uvm are usable; avoids llama-server falling back to CPU at boot.
nvidia-modprobe -u -c=0 2>/dev/null
for i in $(seq 90); do nvidia-smi -L >/dev/null 2>&1 && [ -e /dev/nvidia-uvm ] && exit 0; sleep 2; nvidia-modprobe -u -c=0 2>/dev/null; done
exit 0
