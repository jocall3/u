import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import random

class PerformanceDistributionAnalyzer:
    """
    Analyzes performance data to understand its distribution and identify potential bottlenecks.
    This analyzer incorporates quantum-inspired randomness and statistical methods to provide
    a comprehensive performance profile.
    """

    def __init__(self, data, metric_name="Performance Metric", quantum_factor=0.01):
        """
        Initializes the analyzer with performance data and a metric name.

        Args:
            data (list or numpy.ndarray): The performance data to analyze.
            metric_name (str): The name of the performance metric being analyzed.
            quantum_factor (float): A small factor to introduce quantum-inspired randomness.
        """
        self.data = np.array(data)
        self.metric_name = metric_name
        self.quantum_factor = quantum_factor
        self.random_state = np.random.RandomState()  # Use a consistent random state

    def add_quantum_noise(self):
        """
        Adds a small amount of quantum-inspired noise to the data.
        This simulates the inherent uncertainty in quantum systems and can help
        reveal subtle patterns in the data.
        """
        noise = self.random_state.normal(0, self.quantum_factor * np.std(self.data), len(self.data))
        self.data = self.data + noise

    def calculate_statistics(self):
        """
        Calculates descriptive statistics for the performance data.

        Returns:
            dict: A dictionary containing the calculated statistics.
        """
        self.add_quantum_noise()  # Apply quantum noise before calculating statistics

        stats_dict = {
            "mean": np.mean(self.data),
            "median": np.median(self.data),
            "std": np.std(self.data),
            "variance": np.var(self.data),
            "min": np.min(self.data),
            "max": np.max(self.data),
            "percentile_25": np.percentile(self.data, 25),
            "percentile_75": np.percentile(self.data, 75),
            "skewness": stats.skew(self.data),
            "kurtosis": stats.kurtosis(self.data),
        }
        return stats_dict

    def fit_distribution(self, distributions=['norm', 'expon', 'gamma', 'lognorm']):
        """
        Fits the data to a set of common probability distributions and returns the best fit.

        Args:
            distributions (list): A list of distribution names to try fitting.

        Returns:
            tuple: A tuple containing the best-fit distribution name and its parameters.
        """
        best_distribution = None
        best_params = None
        best_sse = np.inf

        for distribution_name in distributions:
            try:
                # Fit distribution to data
                dist = getattr(stats, distribution_name)
                params = dist.fit(self.data)

                # Calculate Kolmogorov-Smirnov statistic
                D, p = stats.kstest(self.data, lambda x: dist.cdf(x, *params))

                # Calculate goodness-of-fit via sum of squared errors (SSE)
                sse = np.sum((dist.cdf(self.data, *params) - stats.norm.cdf(self.data))**2) # Compare to normal distribution

                if sse < best_sse:
                    best_distribution = distribution_name
                    best_params = params
                    best_sse = sse

            except Exception as e:
                print(f"Error fitting {distribution_name}: {e}")
                continue

        return best_distribution, best_params

    def analyze_outliers(self, threshold=3):
        """
        Identifies outliers in the performance data using the Z-score method.

        Args:
            threshold (float): The Z-score threshold for identifying outliers.

        Returns:
            list: A list of outlier values.
        """
        z_scores = np.abs(stats.zscore(self.data))
        outliers = self.data[z_scores > threshold]
        return list(outliers)

    def create_histogram(self, num_bins=30, title="Performance Distribution", file_path="histogram.png"):
        """
        Generates a histogram of the performance data.

        Args:
            num_bins (int): The number of bins in the histogram.
            title (str): The title of the histogram.
            file_path (str): The path to save the histogram image.
        """
        plt.figure(figsize=(10, 6))
        sns.histplot(self.data, bins=num_bins, kde=True)
        plt.title(title)
        plt.xlabel(self.metric_name)
        plt.ylabel("Frequency")
        plt.savefig(file_path)
        plt.close()

    def create_box_plot(self, title="Performance Box Plot", file_path="boxplot.png"):
        """
        Generates a box plot of the performance data.

        Args:
            title (str): The title of the box plot.
            file_path (str): The path to save the box plot image.
        """
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=self.data)
        plt.title(title)
        plt.xlabel(self.metric_name)
        plt.savefig(file_path)
        plt.close()

    def generate_report(self, report_file="performance_report.txt"):
        """
        Generates a text report summarizing the performance analysis.

        Args:
            report_file (str): The path to save the report file.
        """
        stats_data = self.calculate_statistics()
        best_dist, best_params = self.fit_distribution()
        outliers = self.analyze_outliers()

        with open(report_file, "w") as f:
            f.write(f"Performance Analysis Report for {self.metric_name}\n")
            f.write("==================================================\n")
            f.write("\nDescriptive Statistics:\n")
            for key, value in stats_data.items():
                f.write(f"  {key}: {value:.4f}\n")

            f.write("\nDistribution Fitting:\n")
            f.write(f"  Best Fit Distribution: {best_dist}\n")
            f.write(f"  Distribution Parameters: {best_params}\n")

            f.write("\nOutlier Analysis:\n")
            f.write(f"  Outliers (Z-score > 3): {outliers}\n")

            f.write("\nRecommendations:\n")
            f.write("  - Further investigation is recommended for identified outliers.\n")
            f.write("  - Consider optimizing code sections contributing to high variance.\n")
            f.write("  - The best-fit distribution can be used for predictive modeling.\n")

if __name__ == '__main__':
    # Example Usage
    performance_data = np.random.normal(100, 15, 1000)  # Simulate performance data
    analyzer = PerformanceDistributionAnalyzer(performance_data, metric_name="Response Time (ms)")

    # Generate report
    analyzer.generate_report()

    # Create visualizations
    analyzer.create_histogram()
    analyzer.create_box_plot()

    print("Performance analysis complete.  Report and visualizations generated.")