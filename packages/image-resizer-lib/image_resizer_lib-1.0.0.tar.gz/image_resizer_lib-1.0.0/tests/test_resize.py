import os
from image_resizer import resize_image, resize_by_scale

input_path = os.path.join("input", "input.jpg")
output_resized_path = os.path.join("input", "output_resized.jpg")
output_scaled_path = os.path.join("input", "output_scaled.jpg")

resize_image(input_path, output_resized_path, 300, 300)
resize_by_scale(input_path, output_scaled_path, 0.5)

print("Test complete! Check the 'input' folder for resized images.")