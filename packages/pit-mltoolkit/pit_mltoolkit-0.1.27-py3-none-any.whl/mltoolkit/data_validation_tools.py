import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec


def nan_report(df, enable_graph=False) -> pd.DataFrame:
    """
    # Overview:

    This function creates a detailed report on the null/nan values present within the dataframe,
    when graph is enabled it can generate a graph to visualy view the amount of null/nan values
    within the dataframe.

    ## Parameters:

    `df` (pd.Dataframe) - this parameter expects a pandas dataframe 

    `enable_graph` (bool) - the defualt is false, but when set to true this will return in the output a graph that visually represents the null/nan values present

    ## Example Usage:
    ```python

    data = pd.read_csv('data.csv')
    nan_report(df=data)

    ```
    ## Author(s):
    - Tyron Lambrechts
    
    """

    if not isinstance(df, pd.DataFrame):
        raise Exception('df should be a pandas dataframe')

    if df.isna().any().any():
        
        # The columns that will be created in the nan report dataframe
        nan_report_columns = ['count', 'percentage_missing']

        # Checking for the total length of the dataframe
        total_data = len(df)

        # Calculating the nan counts and creating a subset of the dataframe which only contains nan the rest is discarded
        nan_counts = df.isna().sum()
        nan_count_subset = nan_counts > 0
        containing_nan_names = nan_counts[nan_count_subset].index.tolist()
        containing_nan_values = nan_counts[nan_count_subset].values

        # Creating the nan report dataframe
        nan_report_df = pd.DataFrame(columns=nan_report_columns, index=containing_nan_names)
        nan_report_df['count'] = containing_nan_values
        nan_report_df['percentage_missing'] = nan_report_df['count'] / total_data

        # If the enable graph is True plot a heatmap 
        if enable_graph:
            plt.title('Null/NaN values present in Dataframe')
            sns.heatmap(data=df.isnull())
            plt.show()

        # Print the report df and return it to the user as well
        print("\n" + "="*55)
        print(f" Missing Value Summary")
        print("="*55 + "\n")
        print(nan_report_df.to_string(index=False))
        print("\n" + "="*55) 

        return(nan_report_df)

    else:
        print('No NaN/Null Values Found')

def iqr_outlier_report(df, k = 1.5, enable_graph = False, columns_to_ignore: list = None):
    """
    # Overview
    A outlier detection function that uses the interquartile range (IQR) method to identify outlier.
    This function generates a report or creates a graph for each feature. The graph will consist of 
    a feauter distribution and a boxplot.

    ## Parameter:
    **df** (`pandas.core.DataFrame`): input data frame.

    **k** (`float`): scalar value to determine the strengt of the outlier detection.

    **enable_graph** (`bool`): boolean value to determine if a graph should be created or not. If enable_graph = True a graph
    will be created. If enable_graph = Flase a report will be generated listing the number of detected 
    oultiers for each feature. 

    **columns_to_ignore** (`list`): columns that should be ignored in the analysis (i.e. 'target', 'id')

    ## Example usage:
    ```python

    df = pandas.read_csv('path/to/data.csv')
    iqr_outlier_report(df=df)

    ```

    ## Important to Note:
    If the value for `k` is not equal to 1.5 the Wiskers of the boxplot are not standard.
    The value ranges are correct, however the representation of the wiskers on the graph is displayed as the first data point less than 
    the upper bound and one data point more than the lower bound.

    ## Author(s):
    - Thomas Verryne

    """

    def adjusted_box_plot_fences(column, k):
        """
        Function to calculate new bounds based on the scalar input value
        """
        q1 = np.percentile(column, 25)
        q3 = np.percentile(column, 75)
        iqr = q3 - q1
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        return lower_bound, upper_bound

    if not isinstance(df, pd.DataFrame):
        raise Exception('df should be a pandas dataframe')
    
    # Add condition to check if the number of columns is below 15 

    if df.shape[1] >= 15:
        enable_graph = False
     

    outlier_summary = []
    columns = [col for col in df.columns if col not in columns_to_ignore]
    
    if enable_graph:
        c_df = df.copy()

        # Drop specific columns (if needed)
        c_df.drop(columns=columns_to_ignore, inplace=True)

        # Set number of rows and columns for subplots
        num_columns = len(c_df.columns)
        rows = 2 * ((num_columns // 3) + (1 if num_columns % 3 != 0 else 0))  # Ensure enough rows for histograms and box plots
        cols = min(num_columns, 3)  # Ensure a maximum of 3 columns per row

        # Create a figure with subplots
        fig = plt.figure(figsize=(15, 5 * (rows // 2)))
        # Define the height ratios
        height_ratios = [3 if i % 2 == 0 else 1 for i in range(rows)]
        gs = gridspec.GridSpec(rows, cols, figure=fig, height_ratios=height_ratios)

        # Loop through columns and create histograms with KDE and box plots
        for i, (column_name, column) in enumerate(c_df.items()):
  
            # Calculate grid position
            row = (i // cols) * 2
            col = i % cols
            
            # Distribution plot
            ax_hist = fig.add_subplot(gs[row, col])

            sns.histplot(column, bins=30, stat="density", fill=False, color ='gray')
            sns.kdeplot(column, color="b")
            ax_hist.set_xlabel('Value')
            ax_hist.set_ylabel('Density')
            ax_hist.set_title(f'{column_name} Distribution')
            
            # Box plot directly underneath
            ax_box = fig.add_subplot(gs[row + 1, col])
            sns.boxplot(x=column, ax=ax_box, orient='h', color='white', whis=k)
            ax_box.set_xlabel('Value')
            ax_box.set_title(f'{column_name} Box Plot')

        # Adjust layout
        plt.tight_layout()
        plt.show() 
    else:

         # Iterate through each feature
        for column in columns:
            
            feature_data = df[column].values.reshape(-1, 1)
            
            # Apply adjusted box plot for outlier detection
            lower_bound, upper_bound = adjusted_box_plot_fences(feature_data, k = k)
            
            # Identify outliers
            outliers = (feature_data < lower_bound) | (feature_data > upper_bound)
            num_outliers = outliers.sum()
            if num_outliers > 0:
                outlier_summary.append([column, lower_bound, upper_bound, num_outliers])
        
            # Functionality to implement outlier clamping
            # Clamp outliers to the boundary values
            # feature_data[outliers] = np.clip(feature_data[outliers], lower_bound, upper_bound)
            
            # Update the original DataFrame with the clamped data
            # df.loc[df[target_column] == class_label, column] = feature_data.flatten()

        outlier_summary_df = pd.DataFrame(outlier_summary, columns=["Feature", "Lower Bound", "Upper Bound", "Number of Outliers"])
        if outlier_summary_df.shape[0] == 0:
            print("DataFrame does not contain any oultiers.")
        else:
            print("\n" + "="*55)
            print(f" Outlier Summary for k = {k}")
            print("="*55 + "\n")
            print(outlier_summary_df.to_string(index=False))
            print("\n" + "="*55) 
