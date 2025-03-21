import pandas as pd
import pytest
from UEQanalyzer.analysis import (
    calculate_mean_scores,
    transform_and_calculate_scales,
    calculate_item_statistics,
    calculate_scale_means,
)

# Fixture for sample data
@pytest.fixture
def sample_data():
    data = {
        "Q1": [4, 5, 6],
        "Q2": [3, 4, 5],
        "Q3": [2, 3, 4],
        "Q4": [1, 2, 3],
        "Q5": [5, 6, 7],
        "Q6": [4, 5, 6],
        "Q7": [3, 4, 5],
        "Q8": [2, 3, 4],
    }
    return pd.DataFrame(data)

# Fixture for edge case data (single row)
@pytest.fixture
def edge_case_data():
    data = {
        "Q1": [4],
        "Q2": [3],
        "Q3": [2],
        "Q4": [1],
        "Q5": [5],
        "Q6": [4],
        "Q7": [3],
        "Q8": [2],
    }
    return pd.DataFrame(data)

# Test calculate_mean_scores
def test_calculate_mean_scores(sample_data):
    result = calculate_mean_scores(sample_data)
    expected = {
        "Attractiveness": 4.5,  # Mean of Q1 and Q2
        "Perspicuity": 2.5,     # Mean of Q3 and Q4
        "Efficiency": 5.5,      # Mean of Q5 and Q6
        "Dependability": 3.5,   # Mean of Q7 and Q8
    }
    assert result == pytest.approx(expected, rel=1e-2)

# Test calculate_mean_scores with edge case (single row)
def test_calculate_mean_scores_edge_case(edge_case_data):
    result = calculate_mean_scores(edge_case_data)
    expected = {
        "Attractiveness": 3.5,  # Mean of Q1 and Q2
        "Perspicuity": 1.5,     # Mean of Q3 and Q4
        "Efficiency": 4.5,      # Mean of Q5 and Q6
        "Dependability": 2.5,   # Mean of Q7 and Q8
    }
    assert result == pytest.approx(expected, rel=1e-2)

# Test transform_and_calculate_scales
def test_transform_and_calculate_scales(sample_data):
    result = transform_and_calculate_scales(sample_data)
    # Check if the rescaled data is within the expected range (-3 to 3)
    assert (result.iloc[:, :8] >= -3).all().all() and (result.iloc[:, :8] <= 3).all().all()
    # Check if the new columns (Pragmatic Quality, Hedonic Quality, Overall) are added
    assert "Pragmatic Quality" in result.columns
    assert "Hedonic Quality" in result.columns
    assert "Overall" in result.columns

# Test calculate_item_statistics
def test_calculate_item_statistics(sample_data):
    rescaled_data = transform_and_calculate_scales(sample_data)
    result = calculate_item_statistics(rescaled_data)
    # Check if the result contains the expected columns
    assert set(result.columns) == {"Item", "Mean", "Variance", "Std. Dev.", "No."}
    # Check if the number of rows matches the number of items
    assert len(result) == 8  # 8 items (Q1 to Q8)

# Test calculate_scale_means
def test_calculate_scale_means(sample_data):
    result = calculate_scale_means(sample_data)
    expected = {
        "Scale": ["Pragmatic Quality", "Hedonic Quality", "Overall"],
        "Mean": [3.5, 4.5, 4.0],  # Calculated manually from sample data
    }
    expected_df = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected_df, check_exact=False, atol=0.1)

# Parameterized test for calculate_scale_means
@pytest.mark.parametrize("data, expected", [
    ({"Q1": [1], "Q2": [1], "Q3": [1], "Q4": [1], "Q5": [1], "Q6": [1], "Q7": [1], "Q8": [1]},
     {"Scale": ["Pragmatic Quality", "Hedonic Quality", "Overall"], "Mean": [1.0, 1.0, 1.0]}),
    ({"Q1": [7], "Q2": [7], "Q3": [7], "Q4": [7], "Q5": [7], "Q6": [7], "Q7": [7], "Q8": [7]},
     {"Scale": ["Pragmatic Quality", "Hedonic Quality", "Overall"], "Mean": [7.0, 7.0, 7.0]}),
])
def test_calculate_scale_means_parameterized(data, expected):
    df = pd.DataFrame(data)
    result = calculate_scale_means(df)
    expected_df = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected_df, check_exact=False, atol=0.1)