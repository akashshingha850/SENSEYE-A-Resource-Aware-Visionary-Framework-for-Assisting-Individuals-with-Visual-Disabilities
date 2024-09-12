#!/bin/bash
  
# go to location
cd ~/jetson-inference/build/aarch64/bin

# Loop to rerun the command if it fails
while true; do
	detectnet --ssl-key=key.pem --ssl-cert=cert.pem /dev/video6 webrtc://@:8555/output
    #./detectnet --ssl-key=key.pem --ssl-cert=cert.pem /dev/video6 webrtc://@:8555/output
	#video-viewer /dev/video6 
	if [ $? -eq 0 ]; then
		break
	else
		echo "Command failed, retrying..."
		sleep 2  # Optional: wait for 2 seconds before retrying
	fi
done
