# UEQanalyzer/analysis.py
import pandas as pd

def calculate_mean_scores(data):
    """
    Calculate the mean scores for each UEQ dimension and return them in a DataFrame format.
    """
    # Define the questions associated with each dimension
    dimensions = {
        "Attractiveness": ["Q1", "Q2"],
        "Perspicuity": ["Q3", "Q4"],
        "Efficiency": ["Q5", "Q6"],
        "Dependability": ["Q7", "Q8"]
    }

    # Initialize a dictionary to store the mean scores
    mean_scores = {}
    # Loop through each dimension and calculate the mean score
    for dimension, questions in dimensions.items():
        mean_scores[dimension] = data[questions].mean(axis=1).mean()

    # Convert the mean scores dictionary to a DataFrame
    # mean_scores_df = pd.DataFrame(list(mean_scores.items()), columns=["Dimension", "Mean Score"])

    return mean_scores

# def analyze_dimensions(data):
#     """
#     Perform a detailed analysis of UEQ dimensions (short version).
#     """
#     dimensions = {
#         "Attractiveness": ["Q1", "Q2"],
#         "Perspicuity": ["Q3", "Q4"],
#         "Efficiency": ["Q5", "Q6"],
#         "Dependability": ["Q7", "Q8"]
#     }

#     results = []
#     for dimension, questions in dimensions.items():
#         dimension_data = data[questions]
#         results.append({
#             "Dimension": dimension,
#             "Mean": dimension_data.mean().mean(),
#             "Median": dimension_data.median().median(),
#             "Std Dev": dimension_data.std().mean()
#         })

#     return pd.DataFrame(results)

def transform_and_calculate_scales(data):
    """
    Rescales the data to the range -3 to 3 and calculates Pragmatic Quality, Hedonic Quality, and Overall scores.
    """
    # Rescale the data from 1-7 to -3 to 3
    rescaled_data = data.apply(lambda x: x - 4)  # Subtract 4 to center around 0, then scale to -3 to 3

    # Define which items belong to Pragmatic Quality and Hedonic Quality
    pragmatic_items = [0, 1, 2, 3]  # Columns for Q1, Q2, Q3, Q4
    hedonic_items = [4, 5, 6, 7]    # Columns for Q5, Q6, Q7, Q8

    # Calculate Pragmatic Quality (mean of pragmatic items)
    rescaled_data['Pragmatic Quality'] = rescaled_data.iloc[:, pragmatic_items].mean(axis=1)

    # Calculate Hedonic Quality (mean of hedonic items)
    rescaled_data['Hedonic Quality'] = rescaled_data.iloc[:, hedonic_items].mean(axis=1)

    # Calculate Overall score (mean of all items)
    rescaled_data['Overall'] = rescaled_data.iloc[:, :8].mean(axis=1)

    return rescaled_data

def calculate_item_statistics(data):
    """
    Calculate mean, variance, and standard deviation for each item.
    """
    results = []
    for item in data.columns[:-3]:
        mean = data[item].mean()
        variance = data[item].var()
        std_dev = data[item].std()
        results.append({
            'Item': item,
            'Mean': mean,
            'Variance': variance,
            'Std. Dev.': std_dev,
            'No.': len(data)
        })
    return pd.DataFrame(results)

def calculate_scale_means(data):
    """
    Calculate the mean for Pragmatic Quality, Hedonic Quality, and Overall.
    """
    pragmatic_items = ['Q1', 'Q2', 'Q3', 'Q4']
    hedonic_items = ['Q5', 'Q6', 'Q7', 'Q8']

    pragmatic_mean = data[pragmatic_items].mean(axis=1).mean()
    hedonic_mean = data[hedonic_items].mean(axis=1).mean()
    overall_mean = data.mean(axis=1).mean()

    scale_means = pd.DataFrame({
        'Scale': ['Pragmatic Quality', 'Hedonic Quality', 'Overall'],
        'Mean': [pragmatic_mean, hedonic_mean, overall_mean]
    })
    return scale_means