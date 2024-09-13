import pyrealsense2 as rs

# List connected devices
context = rs.context()
devices = context.query_devices()
if len(devices) == 0:
    print("No RealSense devices were found.")
else:
    print(f"Found {len(devices)} RealSense device(s):")
    for i, device in enumerate(devices):
        print(f"  {i+1}: {device.get_info(rs.camera_info.name)}")