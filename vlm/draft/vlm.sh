jetson-containers run \
  -v /home/jetson/bme/vlm:/mount
  $(autotag nano_llm) \
  python3 -m nano_llm.agents.video_query --api=mlc \
    --model Efficient-Large-Model/VILA1.5-3b \
    --max-context-len 256 \
    --max-new-tokens 32 \
    --video-input /dev/video4 \
    --video-output webrtc://@:8554/output