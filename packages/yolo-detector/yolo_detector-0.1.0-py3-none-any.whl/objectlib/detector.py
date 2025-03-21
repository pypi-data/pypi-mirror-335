import os
import cv2
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):
        """Initialize the YOLO model."""
        self.model = YOLO(model_path)
        self.input_folder = "input"
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)

    def process_images(self):
        """Process all images in the input folder."""
        if not os.path.exists(self.input_folder):
            print(f"Error: Input folder '{self.input_folder}' does not exist! Create it and add images.")
            return

        for image_name in os.listdir(self.input_folder):
            image_path = os.path.join(self.input_folder, image_name)

            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Skipping {image_name}: Unable to read image")
                continue

            # Run YOLO inference
            results = self.model(image)
            detected_objects = self.extract_detected_objects(results)

            # Save the annotated image
            self.save_annotated_image(results, image_name, detected_objects)

    def extract_detected_objects(self, results):
        """Extract detected object names from results."""
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                detected_objects.append(class_name)
        return list(set(detected_objects))

    def save_annotated_image(self, results, image_name, detected_objects):
        """Save image with detections."""
        object_names = "_".join(detected_objects) if detected_objects else "no_object"
        new_filename = f"{object_names}.jpeg"
        output_path = os.path.join(self.output_folder, new_filename)

        annotated_image = results[0].plot()
        cv2.imwrite(output_path, annotated_image)
        print(f"Processed image saved as: {new_filename}")
