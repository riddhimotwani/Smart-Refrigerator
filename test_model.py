from ultralytics import YOLO

# Load the pretrained YOLO model
model = YOLO("yolo11n.pt")

# Run detection on our test image
results = model("test_image.jpg")

# Print detected objects
for result in results:
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = result.names[class_id]

        print(
            f"Detected: {class_name} "
            f"| Confidence: {confidence:.2f}"
        )

# Save the image with detection boxes
results[0].save(filename="result.jpg")

print("\nDetection complete!")
print("Result saved as result.jpg")