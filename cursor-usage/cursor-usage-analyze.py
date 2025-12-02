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


def load_data(data_source: Optional[str] = None) -> pd.DataFrame:
    """
    Load and process the usage data.

    Args:
        data_source: CSV data as string or None to use sample data

    Returns:
        Processed DataFrame with calculated metrics
    """
    data = data_source if data_source else SAMPLE_DATA
    df = pd.read_csv(StringIO(data))

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


def plot_context_size_vs_limit(ax, df):
    """Plot actual context size vs 200k limit."""
    bars = ax.bar(df['Request Number'], df['Actual Context Size'],
                  color=COLORS['bar_colors'][:len(df)])
    ax.axhline(y=CONTEXT_LIMIT, color='r', linestyle='--', alpha=0.7,
               label='200k Context Limit')
    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Token Count', fontsize=10)
    ax.set_title('Actual Context Size vs 200k Limit', fontsize=12, fontweight='bold')
    ax.legend()

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        percentage = height / CONTEXT_LIMIT * 100
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{height:,.0f}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9)


def plot_token_distribution(ax, df):
    """Plot stacked bar chart of token distribution."""
    categories = ['Input (w/ Cache Write)', 'Input (w/o Cache Write)',
                  'Cache Read', 'Output Tokens']
    bottom = np.zeros(len(df))

    for i, category in enumerate(categories):
        values = df[category]
        ax.bar(df['Request Number'], values, bottom=bottom,
               color=COLORS['bar_colors'][i], label=category, alpha=0.8)
        bottom += values

    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Token Count', fontsize=10)
    ax.set_title('Token Distribution Stacked Chart', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x/1000:.0f}k'))


def plot_cost_vs_billable_tokens(ax, df):
    """Plot cost vs billable tokens with trend line."""
    scatter = ax.scatter(df['Billable Tokens'], df['Cost'], s=150, alpha=0.7,
                         c=df['Request Number'], cmap='viridis')
    ax.set_xlabel('Billable Tokens', fontsize=10)
    ax.set_ylabel('Cost ($)', fontsize=10)
    ax.set_title('Cost vs Billable Tokens', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add regression line
    z = np.polyfit(df['Billable Tokens'], df['Cost'], 1)
    p = np.poly1d(z)
    ax.plot(df['Billable Tokens'], p(df['Billable Tokens']), "r--", alpha=0.7,
            label=f'Trend Line: y={z[0]:.6f}x+{z[1]:.3f}')
    ax.legend()

    # Add data labels
    for x, y in zip(df['Billable Tokens'], df['Cost']):
        ax.annotate(f'{x/1000:.0f}k\n${y:.2f}',
                   (x, y),
                   textcoords="offset points",
                   xytext=(0, 10),
                   ha='center',
                   fontsize=8)


def plot_cache_utilization(ax, df):
    """Plot total tokens and cache utilization comparison."""
    ax.bar(df['Request Number'] - 0.2, df['Total Tokens'] / 1000, width=0.4,
           label='Total Tokens (k)', color=COLORS['primary'], alpha=0.7)
    ax.bar(df['Request Number'] + 0.2, df['Cache Utilization (%)'], width=0.4,
           label='Cache Utilization (%)', color=COLORS['danger'], alpha=0.7)

    ax.set_xlabel('Request Number', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_title('Total Tokens vs Cache Utilization', fontsize=12, fontweight='bold')
    ax.set_xticks(df['Request Number'])
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for i, val in enumerate(df['Total Tokens'] / 1000):
        ax.text(i + 1 - 0.2, val, f'{val:.0f}k', ha='center', va='bottom', fontsize=8)
    for i, val in enumerate(df['Cache Utilization (%)']):
        ax.text(i + 1 + 0.2, val, f'{val:.1f}%', ha='center', va='bottom', fontsize=8)


def create_visualizations(df):
    """Create all visualization plots."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Cursor Usage Key Metrics Analysis\n(200k Context Window Limit)',
                 fontsize=16, fontweight='bold', y=0.98)

    # Plot 1: Context size vs limit
    ax1 = plt.subplot(2, 2, 1)
    plot_context_size_vs_limit(ax1, df)

    # Plot 2: Token distribution
    ax2 = plt.subplot(2, 2, 2)
    plot_token_distribution(ax2, df)

    # Plot 3: Cost vs billable tokens
    ax3 = plt.subplot(2, 2, 3)
    plot_cost_vs_billable_tokens(ax3, df)

    # Plot 4: Cache utilization
    ax4 = plt.subplot(2, 2, 4)
    plot_cache_utilization(ax4, df)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
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


def main(data_source: Optional[str] = None):
    """
    Main function to run the analysis.

    Args:
        data_source: Optional CSV data string. If None, uses sample data.
    """
    # Load and process data
    df = load_data(data_source)

    # Setup plotting style
    setup_plot_style()

    # Create visualizations
    create_visualizations(df)

    # Generate summary statistics
    summary_df = create_summary_table(df)

    # Print detailed analysis
    print_detailed_analysis(df, summary_df)


if __name__ == "__main__":
    main()
