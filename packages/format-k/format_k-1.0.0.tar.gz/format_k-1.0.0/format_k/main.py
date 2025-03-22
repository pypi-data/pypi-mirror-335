import os
from PIL import Image

def convert_format(input_image, output_format, output_folder="output"):
    """
    Converts an image to the specified format and saves it in the output directory.
    """

    # List of valid output formats
    valid_formats = ["png", "jpg", "bmp", "webp"]
    if output_format.lower() not in valid_formats:
        raise ValueError(f"❌ Invalid format! Choose from: {valid_formats}")

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Debugging print to check input file path
    print(f"🔍 Checking file path: {input_image}")

    # Check if input file exists
    if not os.path.exists(input_image):
        print(f"🚨 Error: File not found -> {input_image}")
        return
    
    # Load and convert image
    try:
        with Image.open(input_image) as img:
            # Generate output file path
            base_name = os.path.splitext(os.path.basename(input_image))[0]
            output_image = os.path.join(output_folder, f"{base_name}.{output_format.lower()}")

            # Convert and save image
            img.convert("RGB").save(output_image, format=output_format.upper())

            print(f"✅ Image converted successfully: {output_image}")
            return output_image
    except Exception as e:
        print(f"❌ Error processing image: {e}")

# Example usage
if __name__ == "__main__":
    input_folder = r"C:\Users\91702\Desktop\format_k_project\input"
    file_name = "honeybees.jpg"  # Change this to the correct filename
    output_folder = r"C:\Users\91702\Desktop\format_k_project\output"
    output_format = "png"  # Change to the desired format

    # Construct the full path
    input_path = os.path.join(input_folder, file_name)

    # Run the function
    convert_format(input_path, output_format, output_folder)
