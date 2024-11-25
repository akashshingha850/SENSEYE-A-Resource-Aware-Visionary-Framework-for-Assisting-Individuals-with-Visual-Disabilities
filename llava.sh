jetson-containers run $(autotag nano_llm) \
  python3 -m nano_llm.agents.video_query --api=mlc \
    --model Efficient-Large-Model/VILA-2.7b \
    --max-context-len 256 \
    --max-new-tokens 16 \
    --video-input /dev/video6 \
    --video-output webrtc://@:8554/output
