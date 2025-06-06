from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
import base64
from io import BytesIO

def compare_base64_images(base64_img1: str, base64_img2: str) -> float:
    def decode_base64_to_grayscale_array(base64_str):
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data)).convert("L").resize((800, 800))  # Normalize size
        return np.array(img)

    img1_array = decode_base64_to_grayscale_array(base64_img1)
    img2_array = decode_base64_to_grayscale_array(base64_img2)

    score, _ = ssim(img1_array, img2_array, full=True)
    return score 
