# My Tools

A collection of useful tools and utilities for various development and analysis tasks.

## 📦 Tools

### cursor-usage

A Python tool for analyzing Cursor API usage data, providing comprehensive insights into context size, token distribution, costs, and cache utilization.

#### Features

- **Context Size Analysis**: Visualize actual context usage against the 200k token limit
- **Token Distribution**: Stacked bar charts showing breakdown of input tokens, cache reads, and output tokens
- **Cost Analysis**: Scatter plots with trend lines showing cost vs billable tokens relationship
- **Cache Utilization**: Track and analyze cache hit rates and utilization percentages
- **Detailed Reports**: Generate comprehensive text reports with recommendations

#### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/my-tools.git
cd my-tools
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

#### Usage

##### Basic Usage

Run the script with sample data:
```bash
python3 cursor-usage/cursor-usage-analyze.py
```

##### Using Custom Data

You can modify the script to load data from a CSV file. Edit `cursor-usage/cursor-usage-analyze.py` and replace the `SAMPLE_DATA` constant with your CSV data, or modify the `main()` function to read from a file:

```python
# In cursor-usage-analyze.py, modify the main() function:
def main(data_source: Optional[str] = None):
    if data_source is None:
        # Read from CSV file
        with open('your_data.csv', 'r') as f:
            data_source = f.read()
    # ... rest of the function
```

#### Input Data Format

The script expects CSV data with the following columns:

- `Date`: Timestamp of the request
- `Kind`: Request kind (e.g., "Included")
- `Model`: Model used (e.g., "auto")
- `Max Mode`: Maximum mode setting
- `Input (w/ Cache Write)`: Input tokens with cache write
- `Input (w/o Cache Write)`: Input tokens without cache write
- `Cache Read`: Number of tokens read from cache
- `Output Tokens`: Number of output tokens generated
- `Total Tokens`: Total tokens used
- `Cost`: Cost in dollars

Example:
```csv
Date,Kind,Model,Max Mode,Input (w/ Cache Write),Input (w/o Cache Write),Cache Read,Output Tokens,Total Tokens,Cost
2025-12-02T01:46:34.592Z,Included,auto,No,21865,0,68608,3043,93516,0.06
```

#### Output

The script generates:

1. **Visual Dashboard**: A 2x2 grid of plots showing:
   - Actual context size vs 200k limit
   - Token distribution stacked chart
   - Cost vs billable tokens scatter plot
   - Total tokens vs cache utilization comparison

2. **Detailed Analysis Report**: Text output including:
   - Summary statistics table
   - Context size analysis with status indicators
   - Cache utilization analysis
   - Cost efficiency metrics
   - Actionable recommendations

#### Metrics Explained

- **Actual Context Size**: Sum of input tokens (with/without cache write) and output tokens
- **Billable Tokens**: Tokens that contribute to cost calculation (input + output, excluding cache reads)
- **Cache Utilization (%)**: Percentage of tokens served from cache vs total tokens
- **Context Usage (%)**: Percentage of the 200k context window being used

#### Recommendations

The tool provides automatic recommendations based on:

- **Context Usage**: Warns when approaching the 200k limit (>90%) and suggests optimization
- **Cache Utilization**: Identifies low cache usage and suggests standardizing question patterns
- **Cost Efficiency**: Highlights most and least expensive requests for optimization

#### Requirements

- Python 3.7+
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pandas >= 1.3.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built for analyzing Cursor API usage patterns
- Designed to help optimize token usage and reduce costs

