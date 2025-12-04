#!/usr/bin/env python3
"""
Cursor Usage Analysis Script
Analyzes Cursor API usage data including context size, token distribution, costs, and cache utilization.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import pandas as pd
from io import StringIO
from typing import Optional
import argparse
import sys

# Constants
CONTEXT_LIMIT = 200000  # 200k context window limit
WARNING_THRESHOLD = 180000  # Warning threshold (90% of limit)
SAFE_THRESHOLD = 150000  # Safe threshold (75% of limit)
CACHE_WARNING_THRESHOLD = 20  # Cache utilization warning threshold (%)

# Color scheme
COLORS = {
    'primary': '#3498db',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'bar_colors': ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
}

# Sample data (can be replaced with file reading)
SAMPLE_DATA = """Date,Kind,Model,Max Mode,Input (w/ Cache Write),Input (w/o Cache Write),Cache Read,Output Tokens,Total Tokens,Cost
2025-12-02T01:46:34.592Z,Included,auto,No,21865,0,68608,3043,93516,0.06
2025-12-01T13:15:54.637Z,Included,auto,No,26134,0,404992,9107,440233,0.19
2025-12-01T12:56:34.058Z,Included,auto,No,136654,0,853248,26477,1016379,0.54
2025-12-01T12:49:10.345Z,Included,auto,No,26323,0,190720,4617,221660,0.11
"""


def load_data(data_source: Optional[str] = None, csv_file: Optional[str] = None) -> pd.DataFrame:
    """
    Load and process the usage data.

    Args:
        data_source: CSV data as string or None to use sample data
        csv_file: Path to CSV file to read from

    Returns:
        Processed DataFrame with calculated metrics
    """
    if csv_file:
        # Read from CSV file
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading CSV file '{csv_file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif data_source:
        # Use provided CSV data string
        df = pd.read_csv(StringIO(data_source))
    else:
        # Use default sample data
        df = pd.read_csv(StringIO(SAMPLE_DATA))

    # Calculate derived metrics
    df['Actual Context Size'] = (
        df['Input (w/ Cache Write)'] +
        df['Input (w/o Cache Write)'] +
        df['Output Tokens']
    )
    df['Billable Tokens'] = (
        df['Input (w/ Cache Write)'] +
        df['Input (w/o Cache Write)'] +
        df['Output Tokens']
    )

    # Calculate cache utilization (handle division by zero)
    total_with_cache = df['Cache Read'] + df['Billable Tokens']
    df['Cache Utilization (%)'] = np.where(
        total_with_cache > 0,
        df['Cache Read'] / total_with_cache * 100,
        0
    )

    df['Request Number'] = range(1, len(df) + 1)

    return df


def setup_plot_style():
    """Configure matplotlib for better visualization."""
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False


def _set_smart_xticks(ax, x_values, n_points):
    """
    Set smart x-axis ticks to avoid overcrowding.

    Args:
        ax: Matplotlib axis object
        x_values: Series or array of x values
        n_points: Number of data points
    """
    if n_points <= 10:
        # Show all ticks for small datasets
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_values, rotation=0, fontsize=9)
    elif n_points <= 50:
        # Show every 5th tick
        step = max(1, n_points // 10)
        ticks = x_values[::step]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks, rotation=45, ha='right', fontsize=8)
    else:
        # Show approximately 10-15 ticks
        step = max(1, n_points // 12)
        ticks = x_values[::step]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks, rotation=45, ha='right', fontsize=8)

    # Ensure x-axis labels don't overlap with subplot
    ax.tick_params(axis='x', pad=8)


def plot_context_size_vs_limit(ax, df):
    """Plot actual context size vs 200k limit."""
    n_points = len(df)
    use_line_plot = n_points > 20  # Use line plot for many data points

    if use_line_plot:
        # Use line plot with markers for better visibility
        ax.plot(df['Request Number'], df['Actual Context Size'],
                marker='o', markersize=3, linewidth=1.5, alpha=0.7,
                color=COLORS['primary'], label='Actual Context Size')
        # Highlight key points
        max_idx = df['Actual Context Size'].idxmax()
        min_idx = df['Actual Context Size'].idxmin()
        ax.scatter([df.loc[max_idx, 'Request Number']],
                  [df.loc[max_idx, 'Actual Context Size']],
                  s=200, color=COLORS['danger'], zorder=5,
                  label=f'Max: {df.loc[max_idx, "Actual Context Size"]:,.0f}')
        ax.scatter([df.loc[min_idx, 'Request Number']],
                  [df.loc[min_idx, 'Actual Context Size']],
                  s=200, color=COLORS['success'], zorder=5,
                  label=f'Min: {df.loc[min_idx, "Actual Context Size"]:,.0f}')
    else:
        # Use bar chart for small datasets
        bars = ax.bar(df['Request Number'], df['Actual Context Size'],
                      color=COLORS['bar_colors'][:len(df)])
        # Add value labels on bars only for small datasets
        for bar in bars:
            height = bar.get_height()
            percentage = height / CONTEXT_LIMIT * 100
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:,.0f}\n({percentage:.1f}%)',
                    ha='center', va='bottom', fontsize=9)

    ax.axhline(y=CONTEXT_LIMIT, color='r', linestyle='--', alpha=0.7,
               label='200k Context Limit', linewidth=2)
    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Token Count', fontsize=10)
    ax.set_title('Actual Context Size vs 200k Limit', fontsize=12, fontweight='bold', pad=10)

    # Smart x-axis labels
    _set_smart_xticks(ax, df['Request Number'], n_points)

    ax.legend(fontsize=9, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)


def plot_token_distribution(ax, df):
    """Plot stacked bar chart of token distribution."""
    n_points = len(df)
    categories = ['Input (w/ Cache Write)', 'Input (w/o Cache Write)',
                  'Cache Read', 'Output Tokens']

    if n_points > 20:
        # Use area plot for many data points
        ax.stackplot(df['Request Number'],
                    df['Input (w/ Cache Write)'],
                    df['Input (w/o Cache Write)'],
                    df['Cache Read'],
                    df['Output Tokens'],
                    labels=categories,
                    colors=COLORS['bar_colors'],
                    alpha=0.7)
    else:
        # Use stacked bar chart for small datasets
        bottom = np.zeros(len(df))
        for i, category in enumerate(categories):
            values = df[category]
            ax.bar(df['Request Number'], values, bottom=bottom,
                   color=COLORS['bar_colors'][i], label=category, alpha=0.8)
            bottom += values

    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Token Count', fontsize=10)
    ax.set_title('Token Distribution Stacked Chart', fontsize=12, fontweight='bold', pad=10)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x/1000:.0f}k'))

    # Smart x-axis labels
    _set_smart_xticks(ax, df['Request Number'], n_points)

    ax.grid(True, alpha=0.3, axis='y')


def plot_cost_vs_billable_tokens(ax, df):
    """Plot cost vs billable tokens with trend line."""
    n_points = len(df)

    # Adjust scatter point size based on data volume
    point_size = max(20, min(150, 5000 / n_points))
    scatter = ax.scatter(df['Billable Tokens'], df['Cost'], s=point_size,
                         alpha=0.6, c=df['Request Number'], cmap='viridis',
                         edgecolors='black', linewidths=0.5)
    ax.set_xlabel('Billable Tokens', fontsize=10)
    ax.set_ylabel('Cost ($)', fontsize=10)
    ax.set_title('Cost vs Billable Tokens', fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.3)

    # Add regression line
    z = np.polyfit(df['Billable Tokens'], df['Cost'], 1)
    p = np.poly1d(z)
    ax.plot(df['Billable Tokens'], p(df['Billable Tokens']), "r--", alpha=0.7,
            linewidth=2, label=f'Trend: y={z[0]:.6f}x+{z[1]:.3f}')

    # Only annotate key points for large datasets
    if n_points <= 20:
        # Add data labels for small datasets
        for x, y in zip(df['Billable Tokens'], df['Cost']):
            ax.annotate(f'{x/1000:.0f}k\n${y:.2f}',
                       (x, y),
                       textcoords="offset points",
                       xytext=(0, 10),
                       ha='center',
                       fontsize=8)
    else:
        # Highlight key points: max cost, min cost, max tokens, min tokens
        max_cost_idx = df['Cost'].idxmax()
        min_cost_idx = df['Cost'].idxmin()
        max_tokens_idx = df['Billable Tokens'].idxmax()

        key_indices = [max_cost_idx, min_cost_idx, max_tokens_idx]
        for idx in set(key_indices):
            x, y = df.loc[idx, 'Billable Tokens'], df.loc[idx, 'Cost']
            ax.scatter([x], [y], s=300, color='red', marker='*',
                      zorder=5, edgecolors='black', linewidths=1)
            ax.annotate(f'${y:.2f}\n{x/1000:.0f}k',
                       (x, y),
                       textcoords="offset points",
                       xytext=(15, 15),
                       ha='left',
                       fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # Add statistics text
    avg_cost = df['Cost'].mean()
    avg_tokens = df['Billable Tokens'].mean()
    stats_text = f'Avg: ${avg_cost:.2f} / {avg_tokens/1000:.0f}k tokens'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.legend(fontsize=9, loc='best', framealpha=0.9)


def plot_cache_utilization(ax, df):
    """Plot total tokens and cache utilization comparison."""
    n_points = len(df)

    # Use dual y-axis for better visualization
    ax2 = ax.twinx()

    if n_points > 20:
        # Use line plots for many data points
        line1 = ax.plot(df['Request Number'], df['Total Tokens'] / 1000,
                       marker='o', markersize=3, linewidth=1.5,
                       label='Total Tokens (k)', color=COLORS['primary'], alpha=0.7)
        line2 = ax2.plot(df['Request Number'], df['Cache Utilization (%)'],
                        marker='s', markersize=3, linewidth=1.5,
                        label='Cache Utilization (%)', color=COLORS['danger'], alpha=0.7)
    else:
        # Use bar charts for small datasets
        ax.bar(df['Request Number'] - 0.2, df['Total Tokens'] / 1000, width=0.4,
               label='Total Tokens (k)', color=COLORS['primary'], alpha=0.7)
        ax2.bar(df['Request Number'] + 0.2, df['Cache Utilization (%)'], width=0.4,
                label='Cache Utilization (%)', color=COLORS['danger'], alpha=0.7)
        # Add value labels only for small datasets
        for i, val in enumerate(df['Total Tokens'] / 1000):
            ax.text(i + 1 - 0.2, val, f'{val:.0f}k', ha='center', va='bottom', fontsize=8)
        for i, val in enumerate(df['Cache Utilization (%)']):
            ax2.text(i + 1 + 0.2, val, f'{val:.1f}%', ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Total Tokens (k)', fontsize=10, color=COLORS['primary'])
    ax2.set_ylabel('Cache Utilization (%)', fontsize=10, color=COLORS['danger'])
    ax.set_title('Total Tokens vs Cache Utilization', fontsize=12, fontweight='bold', pad=10)

    # Smart x-axis labels
    _set_smart_xticks(ax, df['Request Number'], n_points)

    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9, framealpha=0.9)

    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelcolor=COLORS['primary'], pad=5)
    ax2.tick_params(axis='y', labelcolor=COLORS['danger'], pad=5)


def create_visualizations(df):
    """Create all visualization plots."""
    n_points = len(df)
    # Adjust figure size based on data volume
    if n_points > 100:
        figsize = (20, 14)
    elif n_points > 50:
        figsize = (18, 13)
    else:
        figsize = (16, 12)

    fig = plt.figure(figsize=figsize)
    title = f'Cursor Usage Key Metrics Analysis\n(200k Context Window Limit) - {n_points} Requests'
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Create subplots with increased spacing
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3,
                          left=0.08, right=0.95, top=0.93, bottom=0.08)

    # Plot 1: Context size vs limit
    ax1 = fig.add_subplot(gs[0, 0])
    plot_context_size_vs_limit(ax1, df)

    # Plot 2: Token distribution
    ax2 = fig.add_subplot(gs[0, 1])
    plot_token_distribution(ax2, df)

    # Plot 3: Cost vs billable tokens
    ax3 = fig.add_subplot(gs[1, 0])
    plot_cost_vs_billable_tokens(ax3, df)

    # Plot 4: Cache utilization
    ax4 = fig.add_subplot(gs[1, 1])
    plot_cache_utilization(ax4, df)

    plt.show()


def create_summary_table(df):
    """Create and return summary statistics DataFrame."""
    summary_df = df[['Request Number', 'Actual Context Size', 'Billable Tokens',
                     'Total Tokens', 'Cost', 'Cache Utilization (%)']].copy()
    summary_df['Context Usage (%)'] = summary_df['Actual Context Size'] / CONTEXT_LIMIT * 100
    summary_df['Cost per 1k Tokens'] = summary_df['Cost'] / (summary_df['Billable Tokens'] / 1000)

    return summary_df


def print_detailed_analysis(df, summary_df):
    """Print detailed analysis report."""
    print("=" * 100)
    print("Cursor Usage Detailed Data Analysis Table")
    print("=" * 100)
    print(summary_df.to_string(index=False))

    print("\n" + "=" * 100)
    print("Key Findings Analysis")
    print("=" * 100)

    # 1. Context size analysis
    print("\n1. Actual Context Size Analysis:")
    for idx, row in df.iterrows():
        ctx_size = row['Actual Context Size']
        percentage = ctx_size / CONTEXT_LIMIT * 100

        if ctx_size <= CONTEXT_LIMIT:
            if ctx_size > WARNING_THRESHOLD:
                status = "⚠️ Approaching Limit"
            elif ctx_size > SAFE_THRESHOLD:
                status = "✅ Good"
            else:
                status = "✅ Safe"
        else:
            status = "❌ Exceeded Limit"

        print(f"   Request {idx + 1}: {ctx_size:,.0f} tokens ({percentage:.1f}% of 200k) - {status}")

    # 2. Cache utilization analysis
    print("\n2. Cache Utilization Analysis:")
    for idx, row in df.iterrows():
        cache_util = row['Cache Utilization (%)']
        if cache_util == 0:
            status = "❌ Not Utilized"
        elif cache_util < CACHE_WARNING_THRESHOLD:
            status = "⚠️ Low Utilization"
        else:
            status = "✅ Good"
        print(f"   Request {idx + 1}: {cache_util:.1f}% - {status}")

    # 3. Cost efficiency analysis
    print("\n3. Cost Efficiency Analysis:")
    avg_cost_per_k = summary_df['Cost per 1k Tokens'].mean()
    max_idx = summary_df['Cost per 1k Tokens'].idxmax()
    min_idx = summary_df['Cost per 1k Tokens'].idxmin()

    print(f"   Average Cost per 1k Tokens: ${avg_cost_per_k:.4f}")
    print(f"   Most Expensive Request: Request {max_idx + 1} "
          f"(${summary_df['Cost per 1k Tokens'].max():.4f}/k)")
    print(f"   Cheapest Request: Request {min_idx + 1} "
          f"(${summary_df['Cost per 1k Tokens'].min():.4f}/k)")

    # 4. Context usage recommendations
    print("\n4. Context Usage Recommendations:")
    max_ctx = summary_df['Actual Context Size'].max()
    max_percentage = max_ctx / CONTEXT_LIMIT * 100

    if max_ctx > WARNING_THRESHOLD:
        print(f"   ⚠️ Maximum Usage: {max_percentage:.1f}%, approaching 200k limit")
        print("   Recommendation: Consider compressing input or reducing output length")
    elif max_ctx > SAFE_THRESHOLD:
        print(f"   ✅ Maximum Usage: {max_percentage:.1f}%, still room for optimization")
        print("   Recommendation: Current usage is reasonable, can maintain")
    else:
        print(f"   ✅ Maximum Usage: {max_percentage:.1f}%, sufficient context available")
        print("   Recommendation: Consider increasing output length or including more context")

    # 5. Cache optimization recommendations
    print("\n5. Cache Optimization Recommendations:")
    max_cache_util = summary_df['Cache Utilization (%)'].max()

    if max_cache_util == 0:
        print("   ❌ Cache is not being utilized at all!")
        print("   Recommendation: Standardize question phrasing, reuse similar question patterns")
    else:
        print(f"   Highest Cache Utilization: {max_cache_util:.1f}%")
        print("   Recommendation: Continue optimizing question phrasing to improve cache hit rate")


def main(data_source: Optional[str] = None, csv_file: Optional[str] = None):
    """
    Main function to run the analysis.

    Args:
        data_source: Optional CSV data string. If None, uses sample data.
        csv_file: Optional path to CSV file. If provided, reads from file.
    """
    # Load and process data
    df = load_data(data_source, csv_file)

    # Setup plotting style
    setup_plot_style()

    # Create visualizations
    create_visualizations(df)

    # Generate summary statistics
    summary_df = create_summary_table(df)

    # Print detailed analysis
    print_detailed_analysis(df, summary_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Cursor API usage data including context size, token distribution, costs, and cache utilization.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default sample data
  python3 cursor-usage-analyze.py

  # Analyze data from CSV file
  python3 cursor-usage-analyze.py --csv usage-events-2025-12-02.csv
  python3 cursor-usage-analyze.py -c usage-events-2025-12-02.csv
        """
    )
    parser.add_argument(
        '-c', '--csv',
        type=str,
        dest='csv_file',
        help='Path to CSV file containing usage data. If not provided, uses default sample data.'
    )

    args = parser.parse_args()
    main(csv_file=args.csv_file)
