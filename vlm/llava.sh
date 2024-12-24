jetson-containers run $(autotag nano_llm) \
  python3 -m nano_llm.vision.video \
    --model Efficient-Large-Model/VILA-2.7b \
    --max-images 8 \
    --max-new-tokens 32 \
    --video-input /dev/video4 \
    --video-output webrtc://@:8554/output \
    --prompt 'caption the video concisely'
