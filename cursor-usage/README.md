# cursor-usage

A Python tool for analyzing Cursor API usage data, providing comprehensive insights into context size, token distribution, costs, and cache utilization.

## Features

- **Context Size Analysis**: Visualize actual context usage against the 200k token limit
- **Token Distribution**: Stacked charts showing breakdown of input tokens, cache reads, and output tokens
- **Cost Analysis**: Scatter plots with trend lines showing cost vs billable tokens relationship
- **Cache Utilization**: Track and analyze cache hit rates and utilization percentages
- **Detailed Reports**: Generate comprehensive text reports with recommendations
- **Smart Visualization**: Automatically adapts visualization style based on data volume for optimal readability
- **Key Point Highlighting**: Automatically highlights maximum, minimum, and critical data points

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/my-tools.git
cd my-tools
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

Or if you're using a virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## VSCode Configuration

If you're using VSCode and encounter import resolution errors (e.g., "Cannot resolve import 'matplotlib.ticker'"), you can configure VSCode to properly recognize installed packages.

### Automatic Configuration

The project includes a `.vscode/settings.json` file that should automatically configure VSCode for this project. If you still see import errors:

1. **Reload VSCode Window**:
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Reload Window" and select "Developer: Reload Window"

2. **Select Python Interpreter**:
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the Python interpreter where packages are installed (usually `/usr/bin/python3` or your virtual environment)

### Manual Configuration

If automatic configuration doesn't work, you can manually configure VSCode:

1. **Find your Python user site-packages path**:

   The user site-packages path is where Python packages are installed when you use `pip install --user`. To find this path:

   ```bash
   python3 -c "import site; print(site.getusersitepackages())"
   ```

   This will output a path like `/Users/your-username/Library/Python/3.9/lib/python/site-packages` (on macOS/Linux) or `C:\Users\your-username\AppData\Roaming\Python\Python39\site-packages` (on Windows).

   **Alternative methods to find the path**:
   - Check where a package is installed:
     ```bash
     pip3 show matplotlib | grep Location
     ```
   - List all Python paths:
     ```bash
     python3 -c "import sys; print('\n'.join(sys.path))"
     ```
     Look for the path containing `site-packages` in your user directory.

2. **Create or update `.vscode/settings.json`** in the project root:
   ```json
   {
       "python.defaultInterpreterPath": "/usr/bin/python3",
       "python.analysis.extraPaths": [
           "/Users/your-username/Library/Python/3.9/lib/python/site-packages"
       ],
       "python.analysis.autoImportCompletions": true,
       "python.analysis.typeCheckingMode": "basic",
       "python.analysis.autoSearchPaths": true,
       "python.analysis.diagnosticMode": "workspace"
   }
   ```

   **Note**: Replace `/Users/your-username/Library/Python/3.9/lib/python/site-packages` with the path you got from step 1, and update the Python interpreter path if needed.

3. **For Virtual Environments**:
   If you're using a virtual environment, point to the venv's Python interpreter:
   ```json
   {
       "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python3",
       "python.analysis.extraPaths": []
   }
   ```

### Understanding the Configuration

The `.vscode/settings.json` file contains settings that help VSCode's Python extension properly resolve imports and provide IntelliSense. Here's what each configuration option does:

- **`python.defaultInterpreterPath`**:
  - Specifies which Python interpreter VSCode should use for this workspace
  - Should point to the Python executable where your packages are installed
  - Examples: `/usr/bin/python3`, `${workspaceFolder}/venv/bin/python3`
  - You can also use `${workspaceFolder}` variable for relative paths

- **`python.analysis.extraPaths`**:
  - Additional paths where VSCode should look for Python packages
  - Essential when using `pip install --user` (user-level installations)
  - Should include your user site-packages directory (found using `site.getusersitepackages()`)
  - Can include multiple paths as an array
  - Not needed if all packages are in the interpreter's default site-packages

- **`python.analysis.autoImportCompletions`**:
  - Enables automatic import suggestions in code completion
  - Helps with discovering available modules and functions
  - Set to `true` for better developer experience

- **`python.analysis.typeCheckingMode`**:
  - Controls how strict the type checking is
  - Options: `"off"`, `"basic"`, `"strict"`
  - `"basic"` provides helpful type hints without being too strict
  - `"strict"` enables full type checking (requires type annotations)

- **`python.analysis.autoSearchPaths`**:
  - Automatically searches for packages in common locations
  - Helps VSCode discover packages without manual path configuration
  - Set to `true` to enable automatic discovery

- **`python.analysis.diagnosticMode`**:
  - Controls which files are analyzed for errors and warnings
  - `"workspace"`: Only analyzes files in the current workspace (faster, recommended)
  - `"openFilesOnly"`: Only analyzes currently open files (fastest)
  - `"openFilesOnly"` is useful for large projects to improve performance

## Usage

### Basic Usage

Run the script with sample data:
```bash
python3 cursor-usage/cursor-usage-analyze.py
```

### Using Custom Data

You can analyze data from a CSV file by passing it as a command-line argument:

```bash
# Using --csv flag
python3 cursor-usage/cursor-usage-analyze.py --csv usage-events-2025-12-02.csv

# Using short form -c flag
python3 cursor-usage/cursor-usage-analyze.py -c usage-events-2025-12-02.csv

# Using relative or absolute paths
python3 cursor-usage/cursor-usage-analyze.py -c cursor-usage/usage-events-2025-12-02-composer-1.csv
python3 cursor-usage/cursor-usage-analyze.py -c /path/to/your/data.csv
```

If no CSV file is provided, the script will use the default sample data (`SAMPLE_DATA`).

### Command-Line Options

```bash
python3 cursor-usage/cursor-usage-analyze.py --help
```

**Options:**
- `-c, --csv CSV_FILE`: Path to CSV file containing usage data. If not provided, uses default sample data.
- `-h, --help`: Show help message and exit

## Input Data Format

The script expects CSV data with the following columns:

- `Date`: Timestamp of the request (ISO 8601 format)
- `Kind`: Request kind (e.g., "Included")
- `Model`: Model used (e.g., "auto", "composer-1")
- `Max Mode`: Maximum mode setting (e.g., "No", "Yes")
- `Input (w/ Cache Write)`: Input tokens with cache write
- `Input (w/o Cache Write)`: Input tokens without cache write
- `Cache Read`: Number of tokens read from cache
- `Output Tokens`: Number of output tokens generated
- `Total Tokens`: Total tokens used
- `Cost`: Cost in dollars

**Example CSV:**
```csv
Date,Kind,Model,Max Mode,Input (w/ Cache Write),Input (w/o Cache Write),Cache Read,Output Tokens,Total Tokens,Cost
2025-12-02T01:46:34.592Z,Included,auto,No,21865,0,68608,3043,93516,0.06
2025-12-01T13:15:54.637Z,Included,auto,No,26134,0,404992,9107,440233,0.19
```

## Output

The script generates:

### 1. Visual Dashboard

A 2x2 grid of plots showing:

- **Actual Context Size vs 200k Limit**:
  - Line plot (for >20 data points) or bar chart (for ≤20 points)
  - Highlights maximum and minimum values
  - Shows percentage of context limit used

- **Token Distribution Chart**:
  - Area plot (for >20 data points) or stacked bar chart (for ≤20 points)
  - Breakdown of input tokens, cache reads, and output tokens

- **Cost vs Billable Tokens**:
  - Scatter plot with trend line
  - Highlights key points (max cost, min cost, max tokens)
  - Shows average statistics
  - Point size adjusts based on data volume

- **Total Tokens vs Cache Utilization**:
  - Dual y-axis line plot (for >20 points) or bar chart (for ≤20 points)
  - Compares total tokens and cache utilization percentage

### 2. Detailed Analysis Report

Text output including:

- **Summary Statistics Table**: Complete data table with calculated metrics
- **Context Size Analysis**: Status indicators for each request (✅ Safe, ⚠️ Approaching Limit, ❌ Exceeded Limit)
- **Cache Utilization Analysis**: Utilization status for each request
- **Cost Efficiency Metrics**: Average cost per 1k tokens, most/least expensive requests
- **Actionable Recommendations**:
  - Context usage optimization suggestions
  - Cache optimization recommendations

## Visualization Optimizations

The tool automatically adapts its visualization style based on data volume:

### Small Datasets (≤20 data points)
- Uses bar charts with all labels visible
- Shows individual data point annotations
- Displays all x-axis labels

### Medium Datasets (21-50 data points)
- Uses line plots for time-series data
- Shows key point annotations only
- Displays every 5th x-axis label

### Large Datasets (>50 data points)
- Uses line plots and area plots for better clarity
- Highlights only critical points (max, min, outliers)
- Shows approximately 10-15 x-axis labels
- Dynamically adjusts chart size (up to 20×14 inches for >100 points)

### Key Features
- **Smart X-axis Labels**: Automatically reduces label density to prevent overcrowding
- **Adaptive Point Sizing**: Scatter plot points resize based on data volume
- **Key Point Highlighting**: Automatically identifies and highlights important data points
- **Dual Y-axis Support**: Used for comparing metrics with different scales

## Metrics Explained

- **Actual Context Size**: Sum of input tokens (with/without cache write) and output tokens
- **Billable Tokens**: Tokens that contribute to cost calculation (input + output, excluding cache reads)
- **Cache Utilization (%)**: Percentage of tokens served from cache vs total tokens
- **Context Usage (%)**: Percentage of the 200k context window being used

## Thresholds and Warnings

The tool uses the following thresholds for analysis:

- **Context Limit**: 200,000 tokens
- **Warning Threshold**: 180,000 tokens (90% of limit) - ⚠️ Approaching Limit
- **Safe Threshold**: 150,000 tokens (75% of limit) - ✅ Good
- **Cache Warning Threshold**: 20% - Warns if cache utilization is below this

## Recommendations

The tool provides automatic recommendations based on:

- **Context Usage**:
  - Warns when approaching the 200k limit (>90%) and suggests optimization
  - Suggests compressing input or reducing output length when near limit
  - Recommends increasing context when usage is low

- **Cache Utilization**:
  - Identifies low cache usage and suggests standardizing question patterns
  - Recommends optimizing question phrasing to improve cache hit rate

- **Cost Efficiency**:
  - Highlights most and least expensive requests for optimization
  - Shows average cost per 1k tokens for cost planning

## Requirements

- Python 3.7+
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pandas >= 1.3.0

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'matplotlib'**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Or if using virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

**2. File not found error**
```bash
# Make sure you're using the correct path
# Use absolute path or relative path from project root
python3 cursor-usage/cursor-usage-analyze.py -c cursor-usage/usage-events-2025-12-02.csv
```

**3. Charts not displaying**
- Make sure you have a display available (for GUI environments)
- On headless servers, consider saving plots to files instead of showing them

**4. CSV parsing errors**
- Ensure your CSV file has the correct column headers
- Check that all required columns are present
- Verify CSV encoding (should be UTF-8)

**5. VSCode import resolution errors (Cannot resolve import)**
If VSCode shows import errors even though packages are installed:

1. Check that the Python extension is installed and enabled
2. Reload the VSCode window (`Cmd+Shift+P` → "Reload Window")
3. Select the correct Python interpreter (`Cmd+Shift+P` → "Python: Select Interpreter")
4. Verify the `.vscode/settings.json` file exists and has the correct paths (see [VSCode Configuration](#vscode-configuration) section)
5. If using `pip install --user`, make sure the user site-packages path is in `python.analysis.extraPaths`

To find your user site-packages path:
```bash
python3 -c "import site; print(site.getusersitepackages())"
```

## Examples

### Example 1: Analyze a single CSV file
```bash
python3 cursor-usage/cursor-usage-analyze.py -c usage-events-2025-12-02-composer-1.csv
```

### Example 2: Use default sample data
```bash
python3 cursor-usage/cursor-usage-analyze.py
```

### Example 3: Analyze different model data
```bash
# Analyze composer-1 model usage
python3 cursor-usage/cursor-usage-analyze.py -c usage-events-2025-12-02-composer-1.csv

# Analyze auto model usage
python3 cursor-usage/cursor-usage-analyze.py -c usage-events-2025-12-02-auto.csv
```

