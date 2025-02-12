#!/bin/bash

jetson-containers run $(autotag nano_llm) \
  python3 -m nano_llm.chat --api=mlc \
    --model Efficient-Large-Model/VILA1.5-13b \
    --max-context-len 128 \
    --max-new-tokens 32 \
    --prompt '/data/images/dog.jpg' \
    --prompt 'describe the image concisely.'

# Efficient-Large-Model/VILA1.5-3b
# liuhaotian/llava-v1.5-7b
# liuhaotian/llava-v1.5-13b
# liuhaotian/llava-v1.6-vicuna-7b
# liuhaotian/llava-v1.6-vicuna-13b
# NousResearch/Obsidian-3B-V0.5
# Efficient-Large-Model/VILA-2.7b
# Efficient-Large-Model/VILA-13b
# Efficient-Large-Model/VILA1.5-3b
# Efficient-Large-Model/Llama-3-VILA1.5-8B
# Efficient-Large-Model/VILA1.5-13b
