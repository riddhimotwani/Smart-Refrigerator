import os
import yaml
from collections import Counter

# Path to our new dataset
DATASET_DIR = "groceries_dataset"

# Load data.yaml
with open(os.path.join(DATASET_DIR, "data.yaml"), "r") as f:
    data = yaml.safe_load(f)

names = data["names"]

# Classes we want for our Smart Refrigerator
target_classes = [
    "Apple",
    "Banana",
    "Orange",
    "Tomatoes",
    "Potatoes",
    "Onion",
    "Cucumber",
    "Carrot",
    "Eggs",
    "Milk",
    "Cheese",
    "Broccoli",
    "Sweetcorn",
    "Bell Peppers",
    "Green bell pepper",
    "Red bell pepper",
    "Yellow bell pepper",
    "Mushroom"
]

# Count object instances
instance_counts = Counter()

# Count images containing each class
image_counts = Counter()

# Check train + validation data
for split in ["train", "valid"]:

    labels_dir = os.path.join(DATASET_DIR, split, "labels")

    if not os.path.exists(labels_dir):
        print(f"WARNING: {labels_dir} not found")
        continue

    for filename in os.listdir(labels_dir):

        if not filename.endswith(".txt"):
            continue

        classes_in_image = set()

        filepath = os.path.join(labels_dir, filename)

        with open(filepath, "r") as f:
            for line in f:
                parts = line.strip().split()

                if not parts:
                    continue

                class_id = int(parts[0])
                class_name = names[class_id]

                instance_counts[class_name] += 1
                classes_in_image.add(class_name)

        for class_name in classes_in_image:
            image_counts[class_name] += 1


print("\n==============================================")
print(" SMART REFRIGERATOR DATASET ANALYSIS")
print("==============================================\n")

print(f"{'CLASS':<25} {'INSTANCES':>12} {'IMAGES':>10}")
print("-" * 50)

for class_name in target_classes:

    instances = instance_counts[class_name]
    images = image_counts[class_name]

    print(f"{class_name:<25} {instances:>12} {images:>10}")

print("\n==============================================")
print(" ALL DATASET CLASSES")
print("==============================================")

print(f"Total classes in dataset: {len(names)}")
print("\n")

for i, name in enumerate(names):
    print(f"{i:3}: {name}")

print("\n==============================================")