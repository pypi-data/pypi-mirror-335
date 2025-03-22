import argparse
import pandas as pd
from UEQanalyzer.data_loader import load_ueq_data
from UEQanalyzer.analysis import (
    calculate_mean_scores,
    transform_and_calculate_scales,
    calculate_item_statistics,
    calculate_scale_means,
)
from UEQanalyzer.visualization import (
    plot_dimension_scores,
    plot_item_means,
    plot_scale_means,
    plot_scale_means_with_benchmark,
)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="UEQ Analysis Tool: Analyze and visualize UEQ data.")

    # Add arguments
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input Excel file containing UEQ data."
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to save the analysis results (optional)."
    )
    parser.add_argument(
        "-p", "--plot",
        action="store_true",
        help="Generate and display plots for UEQ dimensions, item means, and scale means."
    )

    # Parse arguments
    args = parser.parse_args()

    # Load data
    print(f"Loading data from {args.input}...")
    data = load_ueq_data(args.input)
    if data is None:
        print("Failed to load data. Exiting.")
        return

    # Transform and calculate scales
    print("Transforming and calculating scales...")
    transformed_data = transform_and_calculate_scales(data)

    # Perform analysis
    print("Calculating mean scores for UEQ dimensions...")
    mean_scores = calculate_mean_scores(transformed_data)
    print("Mean Scores:")
    for dimension, score in mean_scores.items():
        print(f"{dimension}: {score:.2f}")

    # Calculate item statistics
    print("Calculating item statistics...")
    item_stats = calculate_item_statistics(transformed_data)
    print("Item Statistics:")
    print(item_stats)

    # Calculate scale means
    print("Calculating scale means...")
    scale_means = calculate_scale_means(transformed_data)
    print("Scale Means:")
    print(scale_means)

    # Save results (if output path is provided)
    if args.output:
        results = pd.concat([
            pd.DataFrame({"Dimension": list(mean_scores.keys()), "Mean Score": list(mean_scores.values())}),
            item_stats,
            scale_means,
        ], axis=1)
        results.to_csv(args.output, index=False)
        print(f"Analysis results saved to {args.output}.")

    # Generate plots (if --plot is specified)
    if args.plot:
        print("Generating plots...")
        plot_dimension_scores(mean_scores)
        plot_item_means(item_stats)
        plot_scale_means(scale_means)
        plot_scale_means_with_benchmark(scale_means)

if __name__ == "__main__":
    main()