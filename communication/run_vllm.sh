#!/bin/bash
. ~/scripts/slurm_info.sh
echo $CUDA_VISIBLE_DEVICES
echo $SLURM_NODELIST
echo $SLURM_NODEID

ml purge

GPU_IDS=$CUDA_VISIBLE_DEVICES
IFS=',' read -ra elements <<< "$GPU_IDS" # split and read 
DEVICE_COUNT=${#elements[@]}

echo "Node: $SLURM_NODELIST, Node id: $SLURM_NODEID, Num devices: $DEVICE_COUNT, gpu_ids: $GPU_IDS starts"

# model=mistralai/Mistral-7B-Instruct-v0.2
# port=4200
MAX_MODEL_LENGTH=8192

python -m vllm.entrypoints.openai.api_server \
--model $1 \
--port $2 \
--seed $2 \
--max-model-len=$MAX_MODEL_LENGTH \
--tokenizer mistralai/Mistral-7B-Instruct-v0.2 \
--served-model-name $3 \
--dtype=bfloat16