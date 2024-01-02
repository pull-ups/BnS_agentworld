# See https://github.com/lm-sys/FastChat/blob/main/docs/openai_api.md for more usages.

# export CUDA_VISIBLE_DEVICES=0
MODEL_PATH="/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2"   # path_to_the_downloaded_model_dir
MODEL_NAME="mistral-7b-instruct"              # name_of_the_model
CONTROLLER_PORT=20002
python3 -m fastchat.serve.controller --host 127.0.0.1 --port ${CONTROLLER_PORT} & \
python3 -m fastchat.serve.multi_model_worker \
    --model-path ${MODEL_PATH} \
    --model-names ${MODEL_NAME} \
    --load-8bit \
    --host 127.0.0.1 \
    --controller-address http://127.0.0.1:${CONTROLLER_PORT} \
    --worker-address http://127.0.0.1:21002 & \
    
python3 -m fastchat.serve.openai_api_server --host 127.0.0.1 --port 5000 --controller-address http://127.0.0.1:${CONTROLLER_PORT}
