import cv2
import numpy as np
import os
from scipy.ndimage import gaussian_filter
#import imagej
from skimage import restoration

#############gaussian_filter##############
def read_image(file_path):
    return cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

def write_image(image, file_path):
    cv2.imwrite(file_path, image)

def gaussian_smoothing(image, sigma):
    return gaussian_filter(image, sigma=sigma)

def background_subtraction(original_image, background_image):
    corrected_image = original_image.astype(float) - background_image.astype(float)
    corrected_image[corrected_image < 0] = 0  # Set negative values to zero
    return corrected_image.astype(np.uint16)

def process_images_bg(input_folder, output_folder, sigma_d0, sigma_d1, sigma_d2):
    # Walk through the directory tree
    for root, dirs, files in os.walk(input_folder):
        # Determine the relative path of the current directory
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        
        # Ensure the corresponding output directory exists
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        # Choose the sigma value based on the subfolder name
        if root.endswith('d0'):
            sigma = sigma_d0
        elif root.endswith('d1'):
            sigma = sigma_d1
        elif root.endswith('d2'):
            sigma = sigma_d2
        else:
            continue  # Skip if the folder does not match d0, d1, or d2

        # Iterate over all files in the current directory
        for file_name in files:
            if file_name.endswith('.png'):  # Process only .png files
                input_image_path = os.path.join(root, file_name)
                output_image_path = os.path.join(output_subfolder, file_name.replace('.png', '_bg.png'))

                # Read the input image
                original_image = read_image(input_image_path)

                # Apply Gaussian smoothing to create the background image
                background_image = gaussian_smoothing(original_image, sigma)

                # Subtract the background image from the original image
                corrected_image = background_subtraction(original_image, background_image)

                # Write the corrected image to the output folder
                write_image(corrected_image, output_image_path)

                print(f"Processed and saved: {output_image_path}")


########## Rolling Ball Algorithm ##########

def read_image(file_path):
    return cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

def write_image(image, file_path):
    cv2.imwrite(file_path, image)

def rolling_ball_smoothing(image, radius):
    """Apply rolling ball algorithm for background subtraction."""
    background = restoration.rolling_ball(image, radius=radius)
    return background

def background_subtraction(original_image, background_image):
    corrected_image = original_image.astype(float) - background_image.astype(float)
    corrected_image[corrected_image < 0] = 0  # Set negative values to zero
    return corrected_image.astype(np.uint16)

def process_images_bg_rolling_ball(input_folder, output_folder, radius_d0, radius_d1, radius_d2):
    # Walk through the directory tree
    for root, dirs, files in os.walk(input_folder):
        # Determine the relative path of the current directory
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        
        # Ensure the corresponding output directory exists
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        # Choose the sigma value based on the subfolder name
        if root.endswith('d0'):
            radius = radius_d0
        elif root.endswith('d1'):
            radius = radius_d1
        elif root.endswith('d2'):
            radius = radius_d2
        else:
            continue  # Skip if the folder does not match d0, d1, or d2

        # Iterate over all files in the current directory
        for file_name in files:
            if file_name.endswith('.png'):  # Process only .png files
                input_image_path = os.path.join(root, file_name)
                output_image_path = os.path.join(output_subfolder, file_name.replace('.png', '_bg.png'))

                # Read the input image
                original_image = read_image(input_image_path)

                # Apply Gaussian smoothing to create the background image
                background_image = rolling_ball_smoothing(original_image, radius)

                # Subtract the background image from the original image
                corrected_image = background_subtraction(original_image, background_image)

                # Write the corrected image to the output folder
                write_image(corrected_image, output_image_path)

                print(f"Processed and saved: {output_image_path}")



