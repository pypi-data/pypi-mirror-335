import matplotlib.pyplot as plt
import pandas as pd

def plot_dimension_scores(mean_scores):
    """
    Plot the mean scores for each UEQ dimension.
    """
    dimensions = list(mean_scores.keys())
    scores = list(mean_scores.values())

    plt.figure(figsize=(10, 6))
    plt.bar(dimensions, scores, color="skyblue")
    plt.xlabel("UEQ Dimensions")
    plt.ylabel("Mean Score")
    plt.title("Mean Scores for UEQ Dimensions")
    plt.ylim(-3, 3)  # UEQ scores range from 1 to 7
    plt.show()

def plot_item_means(item_stats):
    """
    Plot the mean value per item.
    """
    colors = ['blue' if i < 4 else 'red' for i in range(len(item_stats))]
    plt.figure(figsize=(10, 6))
    plt.bar(item_stats['Item'], item_stats['Mean'], color=colors)
    plt.xlabel('Item')
    plt.ylabel('Mean Value')
    plt.title('Mean Value per Item')
    # plt.axhline(y=0.8, color='green', linestyle='--', label='Positive Threshold (0.8)')
    # plt.axhline(y=-0.8, color='red', linestyle='--', label='Negative Threshold (-0.8)')
    plt.ylim(-3, 3)
    plt.legend()
    plt.show()

def plot_scale_means(scale_means):
    """
    Plot the mean value for Short UEQ Scales.
    """
    plt.figure(figsize=(8, 5))
    plt.bar(scale_means['Scale'], scale_means['Mean'], color='lightgreen')
    plt.xlabel('Scale')
    plt.ylabel('Mean Value')
    plt.title('Short UEQ Scales')
    # plt.axhline(y=0.8, color='green', linestyle='--', label='Positive Threshold (0.8)')
    # plt.axhline(y=-0.8, color='red', linestyle='--', label='Negative Threshold (-0.8)')
    plt.ylim(-3, 3)
    plt.legend()
    plt.show()

def plot_scale_means_with_benchmark(scale_means):
    # Benchmark categories and their borders
    benchmark_borders = {
        'Pragmatic Quality': {'Bad': 0.72, 'Below Average': 1.17, 'Above Average': 1.55, 'Good': 1.74, 'Excellent': 2.5},
        'Hedonic Quality': {'Bad': 0.35, 'Below Average': 0.85, 'Above Average': 1.2, 'Good': 1.59, 'Excellent': 2.5},
        'Overall': {'Bad': 0.59, 'Below Average': 0.98, 'Above Average': 1.31, 'Good': 1.58, 'Excellent': 2.5}
    }

    # Colors for benchmark categories in the desired order
    colors = {
        'Excellent': 'green',
        'Good': 'lightgreen',
        'Above Average': 'yellow',
        'Below Average': 'orange',
        'Bad': 'red'
    }

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    scales = scale_means['Scale']
    means = scale_means['Mean']

    # Plot benchmark categories
    for i, scale in enumerate(scales):
        borders = benchmark_borders[scale]
        previous_border = -1.00
        for category, border in borders.items():
            ax.fill_between([i - 0.4, i + 0.4], previous_border, border, color=colors[category], alpha=0.5)
            previous_border = border

    # Plot the means as dots
    ax.scatter(scales, means, color='blue', s=100, label='Mean Scores', zorder=5)

    # Draw a line connecting the mean scores
    ax.plot(scales, means, color='blue', linestyle='--', marker='o', label='Mean Line', zorder=5)

    # Add labels and title
    ax.set_ylabel('Mean Score')
    ax.set_title('Scale Means with Benchmark Comparison')

    # Create a custom legend in the desired order
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.5, label='Excellent'),
        Patch(facecolor='lightgreen', alpha=0.5, label='Good'),
        Patch(facecolor='yellow', alpha=0.5, label='Above Average'),
        Patch(facecolor='orange', alpha=0.5, label='Below Average'),
        Patch(facecolor='red', alpha=0.5, label='Bad')
    ]

    # Add the legend to the right side of the plot
    ax.legend(handles=legend_elements, title="Benchmark Categories", loc='center left', bbox_to_anchor=(1, 0.5))

    # Set y-axis limits and ticks
    ax.set_ylim(-1.00, 2.50)
    ax.set_yticks([-1.00, -0.50, 0.00, 0.50, 1.00, 1.50, 2.00, 2.50])

    # Adjust layout to make room for the legend
    plt.tight_layout()

    plt.show()