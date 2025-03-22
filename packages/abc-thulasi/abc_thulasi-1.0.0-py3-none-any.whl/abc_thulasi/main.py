from PIL import Image
import os

def convert_format(input_image, output_format, output_folder="output"):
    """
    Converts an image to the specified format.

    Parameters:
    - input_image (str): Path to the input image.
    - output_format (str): Desired output format ('png', 'jpg', 'bmp', 'webp').
    - output_folder (str): Directory to save the converted image.

    Returns:
    - str: Path to the saved converted image.
    """

    # Check if output format is valid
    valid_formats = ["png", "jpg", "bmp", "webp"]
    if output_format.lower() not in valid_formats:
        raise ValueError(f"Invalid format! Choose from: {valid_formats}")

    # Convert relative path to absolute path
    input_image = os.path.abspath(input_image)

    # Check if the input file exists
    if not os.path.exists(input_image):
        raise FileNotFoundError(f"❌ Error: File not found - {input_image}")

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Load and convert image
    with Image.open(input_image) as img:
        # Generate output file path
        base_name = os.path.splitext(os.path.basename(input_image))[0]
        output_image = os.path.join(output_folder, f"{base_name}.{output_format.lower()}")

        # Convert and save
        img.convert("RGB").save(output_image, format=output_format.upper())
        
        print(f"✅ Image converted successfully: {output_image}")
        return output_image

# Example Usage
if __name__ == "__main__":  # Fixed the main check
    input_image_path = os.path.abspath("input/rose.jpeg")  # Get full path
    output_format = "bmp"  # Change format to 'png', 'jpg', 'bmp', or 'webp'

    print(f"🔍 Checking file: {input_image_path}")
    
    try:
        convert_format(input_image_path, output_format)
    except Exception as e:
        print(f"❌ Error: {e}")

