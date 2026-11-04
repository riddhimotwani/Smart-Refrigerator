from ultralytics import YOLO

model = YOLO("runs/detect/train-2/weights/best.pt")

metrics = model.val(
    data="data.yaml",
    split="test",
    imgsz=640,
    conf=0.25
)

P = metrics.box.mp
R = metrics.box.mr
F1 = 2 * P * R / (P + R) if (P + R) else 0
mAP50 = metrics.box.map50
mAP5095 = metrics.box.map

print("Precision:", P)
print("Recall:", R)
print("F1:", F1)
print("mAP@50:", mAP50)
print("mAP@50:95:", mAP5095)