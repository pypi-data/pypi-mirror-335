import pandas as pd

def load_ueq_data(file_path):
    """
    Load UEQ data from an Excel file.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: DataFrame containing the UEQ data.
    """
    try:
        data = pd.read_excel(file_path)
        print("Data loaded successfully!")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None