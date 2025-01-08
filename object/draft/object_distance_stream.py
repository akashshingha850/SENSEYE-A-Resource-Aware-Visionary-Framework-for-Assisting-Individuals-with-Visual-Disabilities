import sys, os
import argparse
import pyrealsense2 as rs
import numpy as np
import cv2  # OpenCV for color format conversion
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput, Log, cudaFromNumpy

# Parse the command line arguments
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=detectNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="lines", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.4, help="minimum detection threshold to use") 

try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# Initialize the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Enable the color and depth streams (RGB and depth)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)    #1280, 720
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)    #640,480

# Start the pipeline
pipeline.start(config)

# Load the object detection network
net = detectNet(args.network, sys.argv, args.threshold)

# Initialize the video output for rendering the image with detections
output = videoOutput("display://0")  # This will display the output on screen

# Function to initialize RTSP streaming
def start_rtsp_stream():
    gst_pipeline = (
    'appsrc ! videoconvert ! video/x-raw,format=I420,width=1280,height=720,framerate=30/1 ! '
    'x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! rtph264pay config-interval=1 ! '
    'udpsink host=0.0.0.0 port=8554'
)

    gst_pipeline = (
    'appsrc ! queue ! videoconvert ! queue ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! queue ! rtph264pay ! queue ! udpsink host=0.0.0.0 port=8554'
)

    
    video_writer = cv2.VideoWriter(gst_pipeline, cv2.CAP_GSTREAMER, 0, 30, (1280, 720))
    if not video_writer.isOpened():
        raise RuntimeError("Failed to open RTSP stream")
    return video_writer

# Initialize RTSP streamer
rtsp_streamer = start_rtsp_stream()

# Capture frames until EOS or the user exits
while True:
    # Capture frames from the RealSense camera
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()

    if not color_frame or not depth_frame:
        print("Failed to capture color or depth frame")
        continue  # Continue capturing frames if this happens
    
    # Convert the captured color frame to a numpy array
    color_image = np.asanyarray(color_frame.get_data())

    # Convert the BGR image to RGB format using OpenCV (this is crucial)
    rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

    # Convert the RGB image (numpy array) to CUDA memory that Jetson Inference can use
    cuda_image = cudaFromNumpy(rgb_image)

    # Detect objects in the image (with overlay)
    detections = net.Detect(cuda_image, overlay=args.overlay)

    for detection in detections:
        center_x, center_y = detection.Center
        width, height = detection.Width, detection.Height
        x1 = int(center_x - width / 2)
        y1 = int(center_y - height / 2)
        x2 = int(center_x + width / 2)
        y2 = int(center_y + height / 2)
        
        distance = depth_frame.get_distance(int(center_x), int(center_y))
        confidence = detection.Confidence
        label = detection.ClassID
        label_name = net.GetClassDesc(label)

        overlay_text = f"{confidence*100:.1f}% {label_name} at {distance:.2f}m"
        cv2.rectangle(color_image, (x1, y1), (x2, y2), (255, 255, 255), 1)
        cv2.putText(color_image, overlay_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    # Stream to RTSP
    rtsp_streamer.write(color_image)

    # Convert the color image back to CUDA memory and render
    final_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
    cuda_image = cudaFromNumpy(final_image)
    output.Render(cuda_image)  # Render the image with detections
    output.SetStatus("Object Detection | Network FPS: {:.2f}".format(net.GetNetworkFPS()))  # Show FPS

    # Exit on input/output EOS
    if not output.IsStreaming():
        break

# Stop the RealSense pipeline and RTSP streamer
pipeline.stop()
rtsp_streamer.release()
