jetson-containers run $(autotag nano_llm) \
  python3 -m nano_llm.chat --api=mlc \
    --model Efficient-Large-Model/VILA1.5-3b \
    --max-context-len 128 \
    --max-new-tokens 32 \
    --prompt '/data/images/bus.jpg' \
    --prompt 'please describe the image concisely.' 
