# util.py

import os
#import imagej
import numpy as np
import pandas as pd

###########
def create_directories(root_dir, sub_dirs):
    """
    Create multiple subdirectories under a root directory if they don't already exist.

    Parameters:
    root_dir (str): The root directory path.
    sub_dirs (list): A list of subdirectory names to create under the root directory.

    Returns:
    None
    """
    # Ensure the root directory exists
    try:
        os.makedirs(root_dir, exist_ok=True)
        print(f"Root directory created: {root_dir}")
    except Exception as e:
        print(f"Failed to create root directory {root_dir}: {e}")
        return

    # Loop through the list of subdirectory names and create them under the root directory
    for sub_dir in sub_dirs:
        dir_path = os.path.join(root_dir, sub_dir)
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Subdirectory created: {dir_path}")
        except Exception as e:
            print(f"Failed to create subdirectory {dir_path}: {e}")


############## Run ImageJ Macro with PyImageJ ##############
def run_imagej_macro(macro_path, input_dir, output_dir, roi_dir):
    """
    Function to run an ImageJ macro from a Python environment with parameters.

    Parameters:
    - macro_path: str, the file path to the ImageJ macro (.ijm)
    - input_dir: str, the input directory path
    - output_dir: str, the output directory path
    - roi_dir: str, the directory path for ROI files

    Returns:
    - None, runs the macro in the ImageJ environment with the given directories
    """
    # Ensure the macro file exists
    if not os.path.exists(macro_path):
        raise FileNotFoundError(f"Macro file not found: {macro_path}")
    
    # Read the macro file content
    with open(macro_path, 'r') as file:
        macro_code = file.read()

    # Format the macro code to include the directory parameters
    # You can pass the directories as macro arguments (depending on how your macro is set up to accept arguments)
    arg_string = f"{input_dir},{output_dir},{roi_dir}"

    # Run the macro with arguments in ImageJ
    ij.py.run_macro(macro_code, arg_string)

    print(f"Macro '{macro_path}' executed successfully with parameters:")
    print(f"Input Directory: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"ROI Directory: {roi_dir}")



############# Load CSV Files and data transformation ##############

def load_csv_files_from_subfolders(folder_path, subfolder_suffix, output_csv_path=None):
    """
    This function loads CSV files from subfolders ending in the specified suffix ('d0', 'd1', 'd2'), 
    processes them by extracting relevant fields, and optionally saves the resulting dataframe to a CSV file.

    Parameters:
    folder_path (str): The root folder path containing subfolders that end with the specified suffix ('d0', 'd1', 'd2').
    subfolder_suffix (str): The suffix for the subfolders (e.g., 'd0', 'd1', or 'd2').
    output_csv_path (str or None): The path to save the resulting dataframe as a CSV file. If None, no file is saved.

    Returns:
    pd.DataFrame: The processed dataframe.
    """
    
    # List to hold the dataframes
    dataframes = []

    # Walk through all subdirectories and files in the specified folder
    for root, dirs, files in os.walk(folder_path):
        # Check if the folder name ends with the specified suffix (e.g., 'd0', 'd1', 'd2')
        if root.endswith(subfolder_suffix):
            # Derive the "field" from the folder name (anything before the suffix)
            field_name = os.path.basename(root).replace(subfolder_suffix, "")
            
            # Iterate over the files in the current folder
            for file_name in files:
                # Check if the file is a CSV
                if file_name.endswith('.csv'):
                    file_path = os.path.join(root, file_name)
                    # Load the CSV file into a dataframe
                    df = pd.read_csv(file_path)
                    # Rename columns based on the suffix
                    intensity_column = f'mean_intensity_{subfolder_suffix}'
                    df.columns = ['cell', 'label', 'area', intensity_column, 'X', 'Y', 'circ.', 'ar', 'round', 'solidity']
                    
                    # Split the 'label' column by _ and : to get frame, well, and cell_ID
                    label_parts = df['label'].str.split(r'[_:]', expand=True)
                    df['frame'] = label_parts[0]  # First part as frame
                    df['well'] = label_parts[4].astype(int)  # Fifth part as well and convert to integer
                    df['cell_ID'] = label_parts[label_parts.shape[1] - 1]  # Last part as cell_ID
                    
                    # Add the 'field' column
                    df['field'] = field_name
                    
                    # Sort the columns
                    df = df[['field', 'frame', 'well', 'cell', 'X', 'Y', 'area', intensity_column, 'circ.', 'ar', 'round', 'solidity', 'cell_ID', 'label']]
                    
                    # Append the dataframe to the list
                    dataframes.append(df)
                    print(f'Loaded: {file_path} with field: {field_name}')
    
    # Concatenate all dataframes into a single dataframe
    df_combined = pd.concat(dataframes, ignore_index=True)

    # Sort the dataframe by the 'frame' column
    df_combined['frame'] = df_combined['frame'].apply(lambda x: int(x[1:]))  # Convert 'pXX' frame labels to integers
    df_combined = df_combined.sort_values(by=['field', 'well', 'frame'])

    # Save the resulting dataframe as a CSV file if a path is provided
    if output_csv_path:
        df_combined.to_csv(output_csv_path, index=False)
        print(f"Saved dataframe to {output_csv_path}")

    return df_combined



################### Merge Dataframes ############################
def merge_dataframes(df0_path, df1_path, df2_path, output_csv):
    # Load the dataframes
    df0 = pd.read_csv(df0_path)
    df1 = pd.read_csv(df1_path)
    df2 = pd.read_csv(df2_path)
    
    # Merge the dataframes by 'field', 'well', 'frame', and 'cell', adding suffixes for overlapping columns
    df_merged = pd.merge(df0, df1, on=['field', 'well', 'frame', 'cell'], suffixes=('_d0', '_d1'))
    df_merged = pd.merge(df_merged, df2, on=['field', 'well', 'frame', 'cell'], suffixes=('', '_d2'))
    
    # Remove duplicate columns (columns that have the same values across the dataframes)
    for col in df0.columns:
        if col in df1.columns and col in df2.columns and df0[col].equals(df1[col]) and df0[col].equals(df2[col]):
            # Drop the redundant columns from the merged dataframe
            df_merged.drop([f'{col}_d0', f'{col}_d1'], axis=1, inplace=True, errors='ignore')
    
    # Select the desired columns for the final merged dataframe
    df_merged = df_merged[['field', 'well', 'frame', 'cell', 'X', 'Y', 'mean_intensity_d0', 
                           'mean_intensity_d1', 'mean_intensity_d2', 'area', 'circ.', 
                           'ar', 'round', 'solidity', 'label_d0', 'label_d1', 'label', 
                           'cell_ID']]
    
    # Save the final merged dataframe to a CSV file
    df_merged.to_csv(output_csv, index=False)
    
    # Return the merged dataframe if needed
    return df_merged

#######################
def merge_and_clean_dataframes(df0, df1, df2, output_csv_path):
    """
    Merges three dataframes on the columns 'field', 'well', 'frame', and 'cell', 
    removes duplicate columns, and saves the final merged dataframe to a CSV file.
    
    Parameters:
    df0 (pd.DataFrame): The first dataframe.
    df1 (pd.DataFrame): The second dataframe.
    df2 (pd.DataFrame): The third dataframe.
    output_csv_path (str): The path where the merged dataframe will be saved.
    
    Returns:
    pd.DataFrame: The final merged dataframe.
    """
    
    # Merge the dataframes by 'field', 'well', 'frame', and 'cell', adding suffixes for overlapping columns
    df_merged = pd.merge(df0, df1, on=['field', 'well', 'frame', 'cell'], suffixes=('_d0', '_d1'))
    df_merged = pd.merge(df_merged, df2, on=['field', 'well', 'frame', 'cell'], suffixes=('', '_d2'))

    # Remove duplicate columns (columns that have the same values across the dataframes)
    for col in df0.columns:
        if col in df1.columns and col in df2.columns and df0[col].equals(df1[col]) and df0[col].equals(df2[col]):
            # Drop the redundant columns from the merged dataframe
            df_merged.drop([f'{col}_d0', f'{col}_d1'], axis=1, inplace=True, errors='ignore')
    
    # Select the desired columns
    df_merged = df_merged[['field', 'well', 'frame', 'cell', 'X', 'Y', 'mean_intensity_d0', 'mean_intensity_d1', 'mean_intensity_d2',
                           'area', 'circ.', 'ar', 'round', 'solidity', 'label_d0', 'label_d1', 'label', 'cell_ID']]
    
    # Save the final merged dataframe to a CSV file
    df_merged.to_csv(output_csv_path, index=False)
    print(f"Dataframe saved to: {output_csv_path}")
    
    return df_merged
"""
# Example usage:
# Load the dataframes
df0 = pd.read_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d0_output.csv')
df1 = pd.read_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output.csv')
df2 = pd.read_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d2_output.csv')

output_csv = '/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_merged_output.csv'

# Call the function to merge and clean the dataframes
df_merged_result = merge_and_clean_dataframes(df0, df1, df2, output_csv)
"""