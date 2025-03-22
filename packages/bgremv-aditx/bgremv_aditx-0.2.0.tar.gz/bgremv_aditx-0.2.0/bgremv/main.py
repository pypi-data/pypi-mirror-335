import os
from rembg import remove
from PIL import Image
from typing import Union, List

def remove_background(input_path: Union[str, Image.Image], output_path: str = None) -> Image.Image:
    """
    Remove background from a single image.
    
    Args:
        input_path: Path to input image or PIL Image object
        output_path: Path to save the output image (optional)
    
    Returns:
        PIL Image object with background removed
    """
    try:
        # Handle both file path and PIL Image inputs
        if isinstance(input_path, str):
            input_image = Image.open(input_path)
        else:
            input_image = input_path
            
        output_image = remove(input_image)
        
        if output_path:
            output_image.save(output_path)
            print(f"Successfully saved to {output_path}")
            
        return output_image
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise

def process_directory(input_dir: str, output_dir: str = None) -> List[str]:
    """
    Process all images in a directory to remove backgrounds.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save processed images (optional)
    
    Returns:
        List of successfully processed file paths
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(input_dir), "output")
    
    os.makedirs(output_dir, exist_ok=True)
    processed_files = []
    
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_bg.png")
            
            try:
                remove_background(input_path, output_path)
                processed_files.append(output_path)
                print(f"Successfully processed {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
    
    return processed_files 