import pandas as pd
import numpy as np

def object_matching(data_frames, distance_threshold=50):
    """
    Combines a list of data frames, adds frame indices, and assigns groups based on proximity across frames.

    Args:
    data_frames (list): A list of pandas data frames to be combined and processed.
    distance_threshold (float): The maximum distance between points to be considered part of the same group.

    Returns:
    pandas.DataFrame: A combined data frame with assigned group labels based on proximity.
    """
    
    # Initialize a list to store all the data along with the frame index
    all_points = []

    # Collect all points with their respective frame index
    for i, df in enumerate(data_frames):
        df['frame_index'] = i  # Add a frame index to each point
        all_points.append(df)

    # Combine all the data frames into one for easier processing
    combined_df = pd.concat(all_points, ignore_index=True)

    # Sort by X and Y to ensure that neighboring points are close in the sorted list
    combined_df = combined_df.sort_values(['X', 'Y']).reset_index(drop=True)

    # Initialize a group counter and a column for group labels
    group_counter = 0
    combined_df['Group'] = None

    # Loop through each point and assign groups based on proximity to points from different frames
    for i in range(len(combined_df)):
        if combined_df.loc[i, 'Group'] is None:  # If the point doesn't have a group yet
            # Create a new group
            group_name = f'group_{group_counter}'
            group_counter += 1
            combined_df.loc[i, 'Group'] = group_name

            # Compare with all subsequent points and assign to the same group if within the threshold
            for j in range(i + 1, len(combined_df)):
                # Only compare points from different frames
                if combined_df.loc[i, 'frame_index'] != combined_df.loc[j, 'frame_index']:
                    # Compute the distance between the current point and the next point
                    distance = np.sqrt((combined_df.loc[i, 'X'] - combined_df.loc[j, 'X']) ** 2 + (combined_df.loc[i, 'Y'] - combined_df.loc[j, 'Y']) ** 2)

                    # If the points are close enough, assign the same group
                    if distance <= distance_threshold:
                        combined_df.loc[j, 'Group'] = group_name

    return combined_df
