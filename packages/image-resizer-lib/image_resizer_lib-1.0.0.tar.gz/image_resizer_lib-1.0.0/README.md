# Image Resizer Library

A simple Python library to resize images using Pillow.

## How to Use

### CLI:
```bash
python image_resizer/resize.py input/input.jpg input/output_resized.jpg --width 300 --height 300
python image_resizer/resize.py input/input.jpg input/output_scaled.jpg --scale 0.5
```

### Programmatically:
```python
from image_resizer import resize_image, resize_by_scale
resize_image('input/input.jpg', 'input/output_resized.jpg', 400, 400)
resize_by_scale('input/input.jpg', 'input/output_scaled.jpg', 0.5)
```

### To run test:
```bash
python tests/test_resize.py
```