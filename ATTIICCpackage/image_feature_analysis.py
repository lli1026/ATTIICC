import os
import pandas as pd

########### process_and_save_cell_count ############
def process_and_save_cell_count(df, output_csv_path):
    """
    This function adds a new column 'cell_count' to the dataframe, calculates the total number of cells in each well,
    sorts the dataframe by 'field', 'well', and 'frame', and saves the updated dataframe to a CSV file.
    
    Parameters:
    df (pd.DataFrame): The input dataframe that contains 'field', 'frame', 'well', and 'cell' columns.
    output_csv_path (str): The path where the updated CSV file will be saved.
    
    Returns:
    pd.DataFrame: The updated dataframe with the 'cell_count' column.
    """
    
    # Add the new column 'cell_count', calculating the total number of cells in each well for each frame
    df['cell_count'] = df.groupby(['field', 'frame', 'well'])['cell'].transform('max')
    
    # Sort the dataframe by 'field', 'well', and 'frame'
    df = df.sort_values(by=['field', 'well', 'frame'])
    
    # Save the updated dataframe to the specified CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Saved updated dataframe to {output_csv_path}")
    
    return df
##################### fill_missing_frames ################
def fill_missing_frames(df, frames_required=None, output_csv_path=None):
    """
    This function fills in missing frames for each well within each field by adding rows with Cell_Count=0
    and filling other fields with 'na' where frames are missing.
    
    Parameters:
    df (pd.DataFrame): The input dataframe that contains 'field', 'well', 'frame', and other relevant columns.
    frames_required (list or None): A list of frames that each well should contain. If None, the function will
                                    use the unique frames from the dataframe.
    output_csv_path (str or None): The path to save the filled dataframe as a CSV file. If None, no file is saved.
    
    Returns:
    pd.DataFrame: The dataframe with missing frames filled.
    """
    
    # Make a copy of the dataframe
    df_filled = df.copy()

    # List of frames that each well should contain
    if frames_required is None:
        frames_required = sorted(df['frame'].unique())  # Use the frames already present in the data if not provided

    # Create an empty list to hold all the new rows
    new_rows = []

    # Iterate over each unique field in the data
    for field in df_filled['field'].unique():
        
        # Iterate over each unique well in this field
        for well in df_filled[df_filled['field'] == field]['well'].unique():
            print(f"Processing Field: {field}, Well: {well}")
        
            # Get the frames that are currently present for this well in the specific field
            frames_present = df_filled[(df_filled['well'] == well) & (df_filled['field'] == field)]['frame'].unique()
            print(f"Frames present for Well {well} in Field {field}: {frames_present}")
        
            # Determine which frames are missing
            frames_missing = [frame for frame in frames_required if frame not in frames_present]
            print(f"Frames missing for Well {well} in Field {field}: {frames_missing}")
        
            # For each missing frame, add a new row with Cell_Count = 0 and other fields set to 'na'
            for frame in frames_missing:
                new_row = {'frame': frame, 'well': well, 'field': field, 'cell': 'na', 'mean_intensity_d0': 'na', 
                           'X': 'na', 'Y': 'na', 'area': 'na', 'circ.': 'na', 'ar': 'na', 'round': 'na', 
                           'rolidity': 'na', 'label': 'na', 'cell_ID': 'na', 'cell_count': 0}
                new_rows.append(new_row)

    # Convert the list of new rows into a DataFrame
    new_rows_df = pd.DataFrame(new_rows)

    # Concatenate the new rows with the original DataFrame
    df_filled = pd.concat([df_filled, new_rows_df], ignore_index=True)

    # Sort the dataframe by 'field', 'well', and 'frame'
    df_filled = df_filled.sort_values(by=['field', 'well', 'frame']).reset_index(drop=True)

    # Save the filled dataframe as a CSV file if a path is provided
    if output_csv_path:
        df_filled.to_csv(output_csv_path, index=False)

    # Return the filled dataframe
    return df_filled

################### add_trends_to_dataframe ################
def add_trends_to_dataframe(df, frames_required, output_csv_path=None):
    """
    This function calculates trends of Cell_Count values across frames for each well within each field.
    Cleans the dataframe by removing rows where 'Trend_1' or 'Trend_2' is NaN.
    
    Parameters:
    df (pd.DataFrame): The filled dataframe that contains 'field', 'well', 'frame', and 'cell_count' columns.
    frames_required (list): A list of required frames (e.g., ['p00', 'p01', ..., 'p15']).
    output_csv_path (str): If provided, the function will save the updated dataframe to this CSV path.
    
    Returns:
    pd.DataFrame: The updated dataframe with 'Trend_1' and 'Trend_2' columns added.
    """
    
    # Function to calculate Trend_1 and Trend_2 for each well within each field
    def calculate_trends(group):
        trend_1 = []
        trend_2 = []
        
        # Get the well and field for labeling
        well = group['well'].iloc[0]
        field = group['field'].iloc[0]
        
        # Track the last Cell_Count to identify trends
        last_count = None
        
        # Iterate over the frames for this well within the field
        for frame in frames_required:
            row = group[group['frame'] == frame]
            
            if not row.empty:
                current_count = row['cell_count'].values[0]
                
                # Check if the Cell_Count has changed compared to the last frame
                if last_count is None or current_count != last_count:
                    # Add to Trend_1 in the format frame_count
                    trend_1.append(f"{frame}_{int(current_count)}")
                    
                    # If last_count is not None, calculate the trend (increase or decrease)
                    if last_count is not None:
                        if current_count > last_count:
                            trend_2.append(f"{frame}_increase")
                        elif current_count < last_count:
                            trend_2.append(f"{frame}_decrease")
                    
                    # Update last_count to the current value
                    last_count = current_count
        
        # Join the trends into strings with Well and Field number prefixed
        trend_1_str = f"{field}_well_{well}_" + "_".join(trend_1)
        trend_2_str = f"{field}_well_{well}_" + "_".join(trend_2)
        
        return pd.Series([trend_1_str, trend_2_str], index=['Trend_1', 'Trend_2'])
    
    # Apply the trend calculation function to each well within each field
    df[['trend_1', 'trend_2']] = df.groupby(['field', 'well']).apply(calculate_trends).reset_index(drop=True)
    
    # Sort the dataframe by 'field', 'well', and 'frame'
    df = df.sort_values(by=['field', 'well', 'frame']).reset_index(drop=True)        
    # delete the rows where na in trend_1 and trend_2
    df = df[(pd.notna(df['trend_1'])) & (pd.notna(df['trend_2']))]
    # only keep the columns 'trend_1' and 'trend_2'
    df=df[['trend_1','trend_2']]
    # extract the well and field from the trend_1 column
    df['well'] = df['trend_1'].str.extract(r'well_(\d+)_')
    df['field'] = df['trend_1'].str.extract(r'f(\d+)_')
    # sort the columns
    df = df[['field','well','trend_1', 'trend_2']]
    
    # Save to CSV if an output path is provided
    if output_csv_path:
        df.to_csv(output_csv_path, index=False)
    # save the cleaned dataframe as a csv file
    df.to_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output_filled_trends_cleaned.csv', index=False)
    
    return df
"""
# Example usage:

# Load the filled dataframe
df_filled = pd.read_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output_filled.csv')
print(df_filled.columns)

# List of frames 
frames_required = df_filled['frame'].unique()

# Call the function to add trends
df_with_trends = add_trends_to_dataframe(df_filled, frames_required, output_csv_path='/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output_trends.csv')
"""

######################## add_event_column ################

def add_event_column(df, output_csv_path=None):
    """
    This function takes a dataframe, classifies cell events based on the 'trend_2' column, 
    adds a new column 'event', and optionally saves the updated dataframe to a CSV file.
    
    Parameters:
    df (pd.DataFrame): The input dataframe containing the 'trend_2' column.
    output_csv_path (str or None): The path to save the updated dataframe as a CSV file. If None, the dataframe is not saved.
    
    Returns:
    pd.DataFrame: The dataframe with the new 'event' column.
    """
    
    # Function to classify events based on the trend_2 column
    def classify_event(trend):
        if 'decrease' in trend and 'increase' not in trend:
            return 'Cell Death'
        elif 'increase' in trend and 'decrease' not in trend:
            return 'Cell Division'
        elif 'stable' in trend:
            return 'No Event'
        else:
            return 'Mixed Event'
    
    # Apply the function to create the 'event' column
    df['event'] = df['trend_2'].apply(classify_event)
    
    # If an output path is provided, save the dataframe as a CSV file
    if output_csv_path:
        df.to_csv(output_csv_path, index=False)
        print(f"Dataframe saved to: {output_csv_path}")
    
    # Return the updated dataframe
    return df
"""
# Example usage:

df= pd.read_csv('/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output_trends.csv') 
output_csv = '/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/cropped_d1_output_trends_events.csv'
df0_trends_with_event = add_event_column(df, output_csv_path=output_csv)
"""
###################### calculate_moving_speed_and_mean ################
def calculate_moving_speed_and_mean(df, output_single_cells_csv, output_mean_moving_csv):
    """
    This function calculates the moving speed for single cells in each well within each field, adds a new column 'moving_speed',
    and calculates the mean moving speed for each well within each field. Both resulting dataframes are saved to CSV files.
    
    Parameters:
    df (pd.DataFrame): The input dataframe containing 'cell_count', 'X', 'Y', 'frame', 'field', and 'well' columns.
    output_single_cells_csv (str): The path where the dataframe with the new 'moving_speed' column will be saved.
    output_mean_moving_csv (str): The path where the dataframe with mean moving speed for each well within each field will be saved.
    
    Returns:
    df_single_cells (pd.DataFrame): The dataframe with the added 'moving_speed' column.
    df_mean_moving (pd.DataFrame): The dataframe with the mean moving speed for each well within each field.
    """
    
    # Filter for single cells (where cell_count is 1)
    df_single_cells = df[df['cell_count'] == 1].copy()
    
    # Initialize the 'moving_speed' column with NaN values
    df_single_cells['moving_speed'] = np.nan

    # Sort the DataFrame by field, well, and frame
    df_single_cells = df_single_cells.sort_values(by=['field', 'well', 'frame'])

    # Loop through each field and well, and calculate the distance between sequential frames
    for field in df_single_cells['field'].unique():
        for well in df_single_cells['well'].unique():
            well_df = df_single_cells[(df_single_cells['field'] == field) & (df_single_cells['well'] == well)].sort_values('frame')
            
            # Loop through frames sequentially to calculate the distance (Euclidean)
            for i in range(1, len(well_df)):
                x1, y1 = well_df.iloc[i - 1][['X', 'Y']]
                x2, y2 = well_df.iloc[i][['X', 'Y']]
                
                # Calculate the Euclidean distance
                distance = round((np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)), 2)
                
                # Update the moving_speed for the current frame
                df_single_cells.loc[well_df.index[i], 'moving_speed'] = distance

    # Save the updated dataframe with 'moving_speed' column
    df_single_cells.to_csv(output_single_cells_csv, index=False)
    print(f"Dataframe with moving speeds saved to: {output_single_cells_csv}")

    # Calculate the mean moving speed for each well within each field
    df_mean_moving = df_single_cells.groupby(['field', 'well'])['moving_speed'].mean().reset_index()
    df_mean_moving = round(df_mean_moving, 2)

    # Save the dataframe with mean moving speed
    df_mean_moving.to_csv(output_mean_moving_csv, index=False)
    print(f"Dataframe with mean moving speeds saved to: {output_mean_moving_csv}")
    
    return df_single_cells, df_mean_moving

######################
def classify_cell_types(df,thresholds_d0,thresholds_d1,thresholds_d2):
    """
    Classifies cell types based on mean_intensity_d0, mean_intensity_d1, and mean_intensity_d2.
    
    Parameters:
    df (pd.DataFrame): The input dataframe containing 'mean_intensity_d0', 'mean_intensity_d1', and 'mean_intensity_d2' columns.
    
    Returns:
    pd.DataFrame: The dataframe with added 'effector', 'target', and 'death' columns.
    """
    
    # Classify as 'effector' if mean_intensity_d0 > 1, otherwise 0
    df['effector'] = df['mean_intensity_d0'].apply(lambda x: 1 if x > thresholds_d0 else 0)
    
    # Classify as 'target' if mean_intensity_d1 > 1, otherwise 0
    df['target'] = df['mean_intensity_d1'].apply(lambda x: 1 if x > thresholds_d1 else 0)
    
    # Classify as 'death' if mean_intensity_d2 > 0.5, otherwise 0
    df['death'] = df['mean_intensity_d2'].apply(lambda x: 1 if x > thresholds_d2 else 0)
    
    return df
######################
def correct_cell_types(df, area_threshold_d0, area_threshold_d1, output_path):
    """
    Corrects 'effector' values based on area in the double positive group (effector=1, target=1),
    and corrects 'target' values based on area in the double negative group (effector=0, target=0).
    
    Parameters:
    df (pd.DataFrame): The input dataframe containing 'area', 'effector', and 'target' columns.
    area_threshold_d0 (float): The threshold to correct 'effector' in the double positive group.
    area_threshold_d1 (float): The threshold to correct 'target' in the double negative group.
    
    Returns:
    pd.DataFrame: The dataframe with corrected 'effector' and 'target' values.
    """
    
    # Before correction check
    print("Before correction:")
    print("Double Positive Group (effector=1, target=1):", df[(df['effector'] == 1) & (df['target'] == 1)].shape)
    print("Effector Group (effector=1, target=0):", df[(df['effector'] == 1) & (df['target'] == 0)].shape)
    print("Double Negative Group (effector=0, target=0):", df[(df['effector'] == 0) & (df['target'] == 0)].shape)
    print("Target Group (effector=0, target=1):", df[(df['effector'] == 0) & (df['target'] == 1)].shape)

    # Correct effector in double positive group (where effector=1 and target=1)
    # Rows where area < area_threshold_d0 should no longer be double positive (set effector=0)
    mask_double_positive = (df['effector'] == 1) & (df['target'] == 1)
    df.loc[mask_double_positive & (df['area'] < area_threshold_d0), 'target'] = 0

    # Rows with area > area_threshold_d0 are moved to effector group (effector=1, target=0)
    #df.loc[mask_double_positive & (df['area'] > area_threshold_d0), 'target'] = 0

    # Correct target in double negative group (where effector=0 and target=0)
    mask_double_negative = (df['effector'] == 0) & (df['target'] == 0)
    df.loc[mask_double_negative & (df['area'] > area_threshold_d1), 'target'] = 1

    # After correction check
    print("After correction:")
    print("Double Positive Group (effector=1, target=1):", df[(df['effector'] == 1) & (df['target'] == 1)].shape)
    print("Effector Group (effector=1, target=0):", df[(df['effector'] == 1) & (df['target'] == 0)].shape)
    print("Double Negative Group (effector=0, target=0):", df[(df['effector'] == 0) & (df['target'] == 0)].shape)
    print("Target Group (effector=0, target=1):", df[(df['effector'] == 0) & (df['target'] == 1)].shape)
    
    # Save corrected dataframe to CSV
    df.to_csv(output_path, index=False)
    return df
######################
import numpy as np
def process_classified_data(df, output_csv_path):
    """
    This function adds several conditional columns to the dataframe based on effector, target, and death status.
    It also saves the updated dataframe to a CSV file.

    Parameters:
    df (pd.DataFrame): The input dataframe that contains the columns 'effector', 'target', and 'death'.
    output_csv_path (str): The path where the output CSV file will be saved.

    Returns:
    pd.DataFrame: The dataframe with the new columns added.
    """

    # Create conditional columns
    df['death_effector'] = np.where((df['effector'] == 1) & (df['death'] == 1), 1, 0)
    df['death_target'] = np.where((df['target'] == 1) & (df['death'] == 1), 1, 0)
    df['defined_effector'] = np.where((df['effector'] == 1) & (df['target'] == 0), 1, 0)
    df['defined_target'] = np.where((df['target'] == 1) & (df['effector'] == 0), 1, 0)
    df['double_pos'] = np.where((df['target'] == 1) & (df['effector'] == 1), 1, 0)
    df['double_neg'] = np.where((df['target'] == 0) & (df['effector'] == 0), 1, 0)
    
    # Create 'cell_type' column based on defined conditions
    conditions = [
        (df['defined_effector'] == 1),  # Effector
        (df['defined_target'] == 1),    # Target
        (df['double_pos'] == 1),        # Double positive
        (df['double_neg'] == 1)         # Double negative
    ]
    choices = ['E', 'T', 'dp', 'dn']
    
    df['cell_type'] = np.select(conditions, choices, default='Unknown')

    # Save the dataframe to a CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")
    print(f"DataFrame shape: {df.shape}")

    return df

##############


def calculate_proximity(df):
    """
    Calculate the proximity between E (effector) and T (target) cells within a well.
    Only considers wells that contain both E and T cell types.

    Parameters:
    df (pd.DataFrame): The input dataframe containing columns including 'well', 'cell_type', 'X', 'Y'.

    Returns:
    pd.DataFrame: A dataframe containing well-wise proximity calculations between E and T cells.
    """

    # Initialize a list to store results
    proximity_results = []

    # Group the data by 'field' and 'well'
    for (field, frame, well), group in df.groupby(['field', 'frame','well']):
        # Filter the group to get E (effector) and T (target) cells
        E_cells = group[group['cell_type'] == 'E']
        T_cells = group[group['cell_type'] == 'T']

        # Only proceed if both E and T cells are present in the well
        if not E_cells.empty and not T_cells.empty:
            # Calculate proximity (Euclidean distance) between each E and T cell
            for _, e_row in E_cells.iterrows():
                e_x, e_y = e_row['X'], e_row['Y']
                
                # Calculate the Euclidean distance to each T cell
                for _, t_row in T_cells.iterrows():
                    t_x, t_y = t_row['X'], t_row['Y']
                    distance = np.sqrt((e_x - t_x)**2 + (e_y - t_y)**2)
                    
                    # Store the results
                    proximity_results.append({
                        'field': field,
                        'frame': frame,
                        'well': well,
                        'E_cell_ID': e_row['cell'],
                        'T_cell_ID': t_row['cell'],
                        'E-T_distance': distance
                    })

    # Convert the proximity results into a DataFrame
    proximity_df = pd.DataFrame(proximity_results)

    return proximity_df

