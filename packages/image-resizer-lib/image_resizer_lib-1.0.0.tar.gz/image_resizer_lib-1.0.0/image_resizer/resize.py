from PIL import Image
import os

def resize_image(input_path, output_path, width, height):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No file found at {input_path}")
    with Image.open(input_path) as img:
        resized_img = img.resize((width, height))
        resized_img.save(output_path)
        print(f"Image saved to {output_path}")

def resize_by_scale(input_path, output_path, scale):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No file found at {input_path}")
    with Image.open(input_path) as img:
        width, height = img.size
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_img = img.resize((new_width, new_height))
        resized_img.save(output_path)
        print(f"Image saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize an image.")
    parser.add_argument("input_path", help="Path to input image")
    parser.add_argument("output_path", help="Path to save resized image")
    parser.add_argument("--width", type=int, help="Target width")
    parser.add_argument("--height", type=int, help="Target height")
    parser.add_argument("--scale", type=float, help="Scaling factor (optional)")

    args = parser.parse_args()

    if args.scale:
        resize_by_scale(args.input_path, args.output_path, args.scale)
    elif args.width and args.height:
        resize_image(args.input_path, args.output_path, args.width, args.height)
    else:
        print("Please provide either width & height OR scale.")