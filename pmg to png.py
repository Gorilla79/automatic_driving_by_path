from PIL import Image
import os

def convert_pgm_to_png(input_file, output_file):
    """
    Converts a PGM or PPM file to a PNG file.

    Parameters:
        input_file (str): Path to the input PGM or PPM file.
        output_file (str): Path to save the output PNG file.
    """
    try:
        # Ensure the input file exists
        if not input_file:
            raise ValueError("Input file path is empty.")

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file {input_file} does not exist.")

        # Open the file
        with Image.open(input_file) as img:
            # Ensure the input file is a PGM or PPM
            if img.format not in ['PGM', 'PPM']:
                raise ValueError(f"Input file {input_file} is not a PGM or PPM file.")

            # Ensure the output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Save the image as PNG
            img.save(output_file, "PNG")
            print(f"Converted {input_file} to {output_file} successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define fixed file paths
    input_file = "D:\\capstone\\24_12_13\\415inside.pgm"
    output_file = "D:\\capstone\\24_12_13\\415inside.png"

    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    convert_pgm_to_png(input_file, output_file)
