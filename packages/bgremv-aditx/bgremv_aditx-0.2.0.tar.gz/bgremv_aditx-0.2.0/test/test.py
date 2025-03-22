import os
from bgremv.main import remove_background, process_directory

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")
    
    # Create input directory if it doesn't exist
    os.makedirs(input_dir, exist_ok=True)
    
    # Example usage
    print("Please place images in the 'input' directory")
    print("Processing directory...")
    processed_files = process_directory(input_dir, output_dir)
    
    if processed_files:
        print(f"Successfully processed {len(processed_files)} files")
        print(f"Output saved to: {output_dir}")
    else:
        print("No images found for processing")
        
    # To test single image processing, uncomment the following:
    # remove_background("path/to/your/image.jpg", "path/to/output.png")