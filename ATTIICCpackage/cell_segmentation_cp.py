# below is for running pretrained model on the whole dataset, process one subfolder at a time
import os
import matplotlib.pyplot as plt
from skimage import io
from cellpose import models, io as cellpose_io
import zipfile
import shutil

def seg_subfolder(saved_model_path, input_subfolder, output_subfolder):
    # Create output subfolder if it doesn't exist
    os.makedirs(output_subfolder, exist_ok=True)
    
    # Load the existing model
    model = models.CellposeModel(gpu=True, pretrained_model=saved_model_path)
    
    # List all image files in the subfolder
    image_files = [f for f in os.listdir(input_subfolder) if f.endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
    print(f"Found {len(image_files)} images in subfolder: {input_subfolder}")
    
    # Process each image
    segmented_images = []
    for i, image_file in enumerate(image_files):
        # Load the image
        image_path = os.path.join(input_subfolder, image_file)
        image = io.imread(image_path)
        
        # Run the Cellpose model
        masks, flows, styles = model.eval(image, diameter=None, channels=[0, 0])
        
        # Save the mask image
        base = os.path.basename(image_file)
        name, ext = os.path.splitext(base)
        
        # Save the mask image using Cellpose I/O
        io.imsave(os.path.join(output_subfolder, f"{name}_label{ext}"), masks.astype('uint16'))  # Save masks as 16-bit image
        
        # Save the mask image as a rois.zip file using Cellpose's built-in io.save_rois function
        cellpose_io.save_rois(masks, os.path.join(output_subfolder, f"{name}_rois.zip"))
        
        # Store original image, mask, and file name for later display
        segmented_images.append((image, masks, image_file))
        
    return segmented_images

def display_images_with_masks(segmented_images):
    # Limit to 16 images for display
    n_images = min(len(segmented_images), 16)
    
    plt.figure(figsize=(9, 4))
    for i in range(n_images):
        # Original image, mask, and file name
        img, mask, file_name = segmented_images[i]
        
        plt.subplot(4, 8, i + 1)
        plt.imshow(img, cmap="gray")  # Adjust this if your images are RGB
        plt.axis('off')
        plt.title(f"{file_name}", fontsize=6)

        # Segmented image (mask)
        plt.subplot(4, 8, i + 17)
        plt.imshow(mask, cmap="gray")  # Display the segmentation mask
        plt.axis('off')
        plt.title(f"Mask {file_name}", fontsize=6)
    
    plt.tight_layout()
    plt.show()

# Main function to process all subfolders and display images
def seg_all_subfolders(saved_model_path, input_directory, output_directory):
    """
    Process all subfolders in the input directory and save segmentation results in the output directory.
    
    Parameters:
    saved_model_path (str): Path to the saved model for segmentation.
    input_directory (str): Path to the input directory containing subfolders with images.
    output_directory (str): Path to the output directory where results will be saved.
    """
    for root, dirs, _ in os.walk(input_directory):
        for subfolder in dirs:
            input_subfolder = os.path.join(root, subfolder)
            output_subfolder = os.path.join(output_directory, subfolder)  # Create matching subfolder in output directory
            
            # Process the subfolder and get segmented images
            segmented_images = seg_subfolder(saved_model_path, input_subfolder, output_subfolder)
            
            # Display the images and masks
            if segmented_images:
                print(f"Displaying images from subfolder: {subfolder}")
                display_images_with_masks(segmented_images)

###############

def is_zip_file_empty(zip_path):
    """Check if a zip file is empty (contains no files)."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if len(zip_ref.infolist()) == 0:
            return True
    return False

def move_empty_zip_files_recursively(source_directory, destination_directory):
    """Move all empty zip files from the source directory and its subfolders to the destination directory, preserving folder structure."""
    # Walk through all the directories and subdirectories
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                
                if is_zip_file_empty(zip_path):
                    # Determine the relative path of the current directory to the source directory
                    relative_path = os.path.relpath(root, source_directory)
                    
                    # Create corresponding subfolder in the destination directory
                    dest_subfolder = os.path.join(destination_directory, relative_path)
                    if not os.path.exists(dest_subfolder):
                        os.makedirs(dest_subfolder)
                    
                    # Move the empty zip file to the corresponding destination subfolder
                    dest_path = os.path.join(dest_subfolder, file)
                    print(f"Moving empty ROI file: {zip_path} to {dest_path}")
                    shutil.move(zip_path, dest_path)
