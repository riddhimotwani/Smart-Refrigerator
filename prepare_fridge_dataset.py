import os
import shutil
import yaml
from collections import Counter

# ============================================================
# SMART REFRIGERATOR - DATASET PREPARATION
# ============================================================

SOURCE_DIR = "groceries_dataset"
OUTPUT_DIR = "fridge_dataset"

# ------------------------------------------------------------
# Final classes for our Smart Refrigerator model
# ------------------------------------------------------------

FINAL_CLASSES = [
    "apple",
    "banana",
    "orange",
    "tomato",
    "potato",
    "onion",
    "cucumber",
    "carrot",
    "egg",
    "milk",
    "cheese",
    "broccoli",
    "bell_pepper",
    "mushroom"
]

# ------------------------------------------------------------
# Original classes that we want to keep
# Multiple original classes can map to one final class.
# ------------------------------------------------------------

CLASS_MAPPING = {
    "Apple": "apple",
    "Banana": "banana",
    "Orange": "orange",
    "Tomatoes": "tomato",
    "Potatoes": "potato",
    "Onion": "onion",
    "Cucumber": "cucumber",
    "Carrot": "carrot",
    "Eggs": "egg",
    "Milk": "milk",
    "Cheese": "cheese",
    "Broccoli": "broccoli",
    "Mushroom": "mushroom",

    # Merge all pepper varieties into one class
    "Bell Peppers": "bell_pepper",
    "Green bell pepper": "bell_pepper",
    "Red bell pepper": "bell_pepper",
    "Yellow bell pepper": "bell_pepper",
}

# ------------------------------------------------------------
# Check source dataset
# ------------------------------------------------------------

SOURCE_YAML = os.path.join(SOURCE_DIR, "data.yaml")

if not os.path.exists(SOURCE_YAML):
    print("ERROR: Could not find:")
    print(SOURCE_YAML)
    print("\nMake sure the folder is named 'groceries_dataset'")
    exit()

# Load original data.yaml
with open(SOURCE_YAML, "r") as f:
    data = yaml.safe_load(f)

original_names = data["names"]

print("\n================================================")
print(" SMART REFRIGERATOR DATASET PREPARATION")
print("================================================\n")

print(f"Original dataset classes : {len(original_names)}")
print(f"Final model classes      : {len(FINAL_CLASSES)}")

print("\nFinal classes:")
for i, name in enumerate(FINAL_CLASSES):
    print(f"{i:2}: {name}")

# ------------------------------------------------------------
# Create mapping:
#
# Original class ID → New class ID
# ------------------------------------------------------------

class_id_mapping = {}

for original_id, original_name in enumerate(original_names):

    if original_name in CLASS_MAPPING:

        final_name = CLASS_MAPPING[original_name]
        new_id = FINAL_CLASSES.index(final_name)

        class_id_mapping[original_id] = new_id

print("\n================================================")
print(" CLASS ID MAPPING")
print("================================================\n")

for original_id, new_id in class_id_mapping.items():
    print(
        f"{original_id:3} {original_names[original_id]:25}"
        f" -> {new_id:2} {FINAL_CLASSES[new_id]}"
    )

# ------------------------------------------------------------
# Delete previously generated dataset if it exists
# ------------------------------------------------------------

if os.path.exists(OUTPUT_DIR):

    print("\nRemoving previous fridge_dataset...")

    shutil.rmtree(OUTPUT_DIR)

# ------------------------------------------------------------
# Counters
# ------------------------------------------------------------

instance_counts = Counter()
image_counts = Counter()

total_images_processed = 0
total_images_kept = 0
total_annotations_removed = 0

# ------------------------------------------------------------
# Supported image extensions
# ------------------------------------------------------------

IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
]

# ------------------------------------------------------------
# Process train / valid / test
# ------------------------------------------------------------

for split in ["train", "valid", "test"]:

    source_images = os.path.join(SOURCE_DIR, split, "images")
    source_labels = os.path.join(SOURCE_DIR, split, "labels")

    output_images = os.path.join(OUTPUT_DIR, split, "images")
    output_labels = os.path.join(OUTPUT_DIR, split, "labels")

    os.makedirs(output_images, exist_ok=True)
    os.makedirs(output_labels, exist_ok=True)

    if not os.path.exists(source_images):
        print(f"\nWARNING: {source_images} does not exist.")
        continue

    if not os.path.exists(source_labels):
        print(f"\nWARNING: {source_labels} does not exist.")
        continue

    print(f"\nProcessing {split.upper()} dataset...")

    split_images = 0
    split_kept = 0

    # Process every label file
    for label_file in os.listdir(source_labels):

        if not label_file.endswith(".txt"):
            continue

        total_images_processed += 1
        split_images += 1

        label_path = os.path.join(source_labels, label_file)

        # Read original annotations
        new_annotations = []

        with open(label_path, "r") as f:

            lines = f.readlines()

        for line in lines:

            parts = line.strip().split()

            if len(parts) < 5:
                continue

            try:
                original_class_id = int(parts[0])
            except ValueError:
                continue

            # Keep only our selected classes
            if original_class_id not in class_id_mapping:

                total_annotations_removed += 1
                continue

            new_class_id = class_id_mapping[original_class_id]

            # Keep bounding box coordinates unchanged
            new_line = (
                f"{new_class_id} "
                f"{parts[1]} "
                f"{parts[2]} "
                f"{parts[3]} "
                f"{parts[4]}\n"
            )

            new_annotations.append(new_line)

            class_name = FINAL_CLASSES[new_class_id]

            instance_counts[class_name] += 1

        # If this image contains none of our target classes,
        # don't copy it into the new dataset.
        if len(new_annotations) == 0:
            continue

        # Find corresponding image
        image_stem = os.path.splitext(label_file)[0]

        image_path = None

        for extension in IMAGE_EXTENSIONS:

            possible_path = os.path.join(
                source_images,
                image_stem + extension
            )

            if os.path.exists(possible_path):

                image_path = possible_path
                break

        if image_path is None:

            print(
                f"WARNING: Image not found for label: "
                f"{label_file}"
            )

            continue

        # Copy image
        destination_image = os.path.join(
            output_images,
            os.path.basename(image_path)
        )

        shutil.copy2(image_path, destination_image)

        # Write new label file
        destination_label = os.path.join(
            output_labels,
            label_file
        )

        with open(destination_label, "w") as f:
            f.writelines(new_annotations)

        # Count this image
        split_kept += 1
        total_images_kept += 1

        # Count unique classes in this image
        classes_in_image = set()

        for annotation in new_annotations:

            class_id = int(annotation.split()[0])
            classes_in_image.add(
                FINAL_CLASSES[class_id]
            )

        for class_name in classes_in_image:
            image_counts[class_name] += 1

    print(
        f"  Images processed : {split_images}"
    )

    print(
        f"  Images kept      : {split_kept}"
    )

# ------------------------------------------------------------
# Create new data.yaml
# ------------------------------------------------------------

new_yaml = {
    "train": "train/images",
    "val": "valid/images",
    "test": "test/images",
    "nc": len(FINAL_CLASSES),
    "names": FINAL_CLASSES
}

output_yaml = os.path.join(
    OUTPUT_DIR,
    "data.yaml"
)

with open(output_yaml, "w") as f:

    yaml.dump(
        new_yaml,
        f,
        sort_keys=False,
        allow_unicode=True
    )

# ------------------------------------------------------------
# Print final statistics
# ------------------------------------------------------------

print("\n================================================")
print(" FINAL DATASET STATISTICS")
print("================================================\n")

print(
    f"{'CLASS':<20}"
    f"{'INSTANCES':>12}"
    f"{'IMAGES':>10}"
)

print("-" * 45)

for class_name in FINAL_CLASSES:

    print(
        f"{class_name:<20}"
        f"{instance_counts[class_name]:>12}"
        f"{image_counts[class_name]:>10}"
    )

print("\n================================================")
print(" DATASET PREPARATION COMPLETE")
print("================================================\n")

print(f"Original classes       : {len(original_names)}")
print(f"Final classes          : {len(FINAL_CLASSES)}")
print(f"Images kept            : {total_images_kept}")
print(f"Annotations removed    : {total_annotations_removed}")

print("\nNew dataset created at:")
print(os.path.abspath(OUTPUT_DIR))

print("\nNew data.yaml:")
print(os.path.abspath(output_yaml))

print("\nNext step:")
print("DO NOT TRAIN YET.")
print("Send the statistics above for verification.")