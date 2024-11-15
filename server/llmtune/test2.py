
#pip install trl
#testing..
#git clone https://github.com/huggingface/trl
#pip install tf-keras
#pip install bitsandbytes
#request access https://huggingface.co/meta-llama/Llama-2-7b-hf
#
# pip install huggingface-hub[cli] 
#huggingface-cli login 
#pip install peft

#python trl/examples/scripts/sft.py --output_dir ./output --model_name meta-llama/Llama-2-7b-hf --dataset_name timdettmers/openassistant-guanaco --load_in_4bit --use_peft --per_device_train_batch_size 4 --per_device_eval_batch_size 2 --gradient_accumulation_steps 2


