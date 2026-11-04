from ultralytics import YOLO

# Load our trained food detection model
model = YOLO(
    "runs/detect/train-2/weights/best.pt"
)

# Run the model on our refrigerator image
results = model(
    "test_image.jpg",
    conf=0.75
)

print("\n========== DETECTED FOOD ITEMS ==========\n")

# Read the detections
for result in results:

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = result.names[class_id]

        print(
            f"{class_name} "
            f"→ confidence: {confidence:.2f}"
        )

    # Save image with bounding boxes
    result.save(filename="custom_result.jpg")

print("\n=========================================")
print("Detection complete!")
print("Result saved as custom_result.jpg")