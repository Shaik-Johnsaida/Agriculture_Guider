"""
Generates high-quality synthetic demo leaf images for AgriShield AI sample selection.
Allows 1-click judging without needing manual file upload downloads.
"""

import os
import numpy as np
import cv2
from PIL import Image


def generate_samples():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_images")
    os.makedirs(output_dir, exist_ok=True)

    h, w = 400, 400

    # 1. Healthy Tomato Leaf
    img_healthy = np.zeros((h, w, 3), dtype=np.uint8)
    img_healthy[:] = (25, 45, 20) # Deep background
    # Draw leaf shape
    cv2.ellipse(img_healthy, (200, 200), (120, 170), 0, 0, 360, (34, 139, 34), -1) # Forest green
    cv2.ellipse(img_healthy, (200, 200), (100, 150), 0, 0, 360, (50, 205, 50), -1) # Lime green
    # Leaf vein
    cv2.line(img_healthy, (200, 50), (200, 350), (144, 238, 144), 3)
    cv2.line(img_healthy, (200, 150), (130, 100), (144, 238, 144), 2)
    cv2.line(img_healthy, (200, 150), (270, 100), (144, 238, 144), 2)
    cv2.line(img_healthy, (200, 250), (120, 220), (144, 238, 144), 2)
    cv2.line(img_healthy, (200, 250), (280, 220), (144, 238, 144), 2)
    Image.fromarray(cv2.cvtColor(img_healthy, cv2.COLOR_BGR2RGB)).save(os.path.join(output_dir, "healthy_leaf.png"))

    # 2. Tomato Late Blight (Dark lesions with yellow halo)
    img_blight = img_healthy.copy()
    # Add chlorotic yellow patches
    cv2.circle(img_blight, (150, 140), 45, (0, 215, 255), -1) # Yellow
    cv2.circle(img_blight, (240, 240), 50, (0, 215, 255), -1)
    # Add dark necrotic brown lesions inside yellow patches
    cv2.circle(img_blight, (150, 140), 30, (19, 38, 60), -1) # Dark brown
    cv2.circle(img_blight, (240, 240), 35, (19, 38, 60), -1)
    cv2.ellipse(img_blight, (180, 290), (35, 20), 45, 0, 360, (15, 30, 50), -1)
    Image.fromarray(cv2.cvtColor(img_blight, cv2.COLOR_BGR2RGB)).save(os.path.join(output_dir, "tomato_late_blight.png"))

    # 3. Rice Brown Spot (Small oval brown lesions)
    img_rice = np.zeros((h, w, 3), dtype=np.uint8)
    img_rice[:] = (20, 35, 20)
    # Rice leaf blade (long narrow)
    cv2.ellipse(img_rice, (200, 200), (60, 190), 0, 0, 360, (46, 139, 87), -1)
    # Central vein
    cv2.line(img_rice, (200, 15), (200, 385), (152, 251, 152), 2)
    # Scatter oval brown spots with yellow margins
    np.random.seed(42)
    for _ in range(18):
        rx = np.random.randint(160, 240)
        ry = np.random.randint(50, 350)
        cv2.ellipse(img_rice, (rx, ry), (8, 4), np.random.randint(0, 180), 0, 360, (0, 200, 255), -1) # Yellow halo
        cv2.ellipse(img_rice, (rx, ry), (5, 2), np.random.randint(0, 180), 0, 360, (20, 40, 80), -1)  # Brown spot
    Image.fromarray(cv2.cvtColor(img_rice, cv2.COLOR_BGR2RGB)).save(os.path.join(output_dir, "rice_brown_spot.png"))

    # 4. Cotton Leaf Curl (Curled yellowing margins)
    img_cotton = np.zeros((h, w, 3), dtype=np.uint8)
    img_cotton[:] = (20, 30, 20)
    cv2.ellipse(img_cotton, (200, 200), (130, 130), 0, 0, 360, (30, 120, 30), -1)
    # Draw yellowing chlorosis around outer margins
    cv2.ellipse(img_cotton, (200, 200), (135, 135), 0, 0, 360, (0, 220, 220), 12)
    # Distorted veins enation
    cv2.line(img_cotton, (200, 70), (200, 330), (0, 255, 255), 4)
    cv2.line(img_cotton, (200, 180), (100, 130), (0, 255, 255), 3)
    cv2.line(img_cotton, (200, 180), (300, 130), (0, 255, 255), 3)
    Image.fromarray(cv2.cvtColor(img_cotton, cv2.COLOR_BGR2RGB)).save(os.path.join(output_dir, "cotton_leaf_curl.png"))

    # 5. Corn Common Rust (Golden brown rust pustules)
    img_corn = np.zeros((h, w, 3), dtype=np.uint8)
    img_corn[:] = (15, 30, 15)
    cv2.ellipse(img_corn, (200, 200), (70, 180), -15, 0, 360, (34, 139, 34), -1)
    # Golden rust pustules
    for _ in range(25):
        rx = np.random.randint(150, 250)
        ry = np.random.randint(60, 340)
        cv2.circle(img_corn, (rx, ry), 6, (0, 140, 255), -1) # Rust orange
        cv2.circle(img_corn, (rx, ry), 3, (0, 90, 180), -1)  # Darker rust
    Image.fromarray(cv2.cvtColor(img_corn, cv2.COLOR_BGR2RGB)).save(os.path.join(output_dir, "corn_common_rust.png"))

    print(f"[INFO] Sample leaf images generated successfully in {output_dir}")

if __name__ == "__main__":
    generate_samples()
