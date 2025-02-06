import time
from ultralytics import YOLO

# Load a YOLOv8n PyTorch model
model = YOLO("yolov8n.pt")

# Export the model to TensorRT
model.export(format="engine", device=0, int8=True)  
#model.export(format="engine")  # creates 'yolov8n.engine'

# Load the exported TensorRT model
trt_model = YOLO("yolov8n.engine")

# Run inference with timing
image_path = "https://raw.githubusercontent.com/zhreshold/mxnet-ssd/master/data/demo/dog.jpg"

start_time = time.time()  # Start timing
results = trt_model(image_path)  # Run inference
end_time = time.time()  # End timing

latency = end_time - start_time  # Calculate latency

# Process results
for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])  # Class index
        confidence = float(box.conf[0])  # Confidence score
        label = trt_model.names[class_id]  # Get class label
        print(f"Detected: {label}, Confidence: {confidence:.4f}, Latency: {latency:.4f} sec")

