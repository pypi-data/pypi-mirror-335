# Plan for Implementing Interactive Website Generation in Kompot

## Overview
The prototype notebook currently generates an interactive HTML report that includes:
1. Interactive gene expression tables and plots
2. Cell annotation visualizations on UMAP
3. Correlation plots for comparing different analysis methods
4. Gene-specific detail pages with multiple visualizations
5. Various interactive elements like dropdowns, sliders, and clickable plots

The goal is to integrate this functionality into the Kompot Python package, making it easy for users to generate similar interactive reports for their data.

## Implementation Plan

### 1. Create New Module Structure

```
kompot/
  ├── __init__.py
  ├── differential.py
  ├── utils.py
  ├── version.py
  └── reporter/
      ├── __init__.py
      ├── html_generator.py     # Main class for generating HTML reports
      ├── components/           # Individual UI components
      │   ├── __init__.py
      │   ├── gene_table.py     # Top genes table
      │   ├── gene_plot.py      # Gene-specific plots
      │   ├── umap_plot.py      # UMAP visualizations
      │   ├── correlation.py    # Method correlation plots
      │   └── thresholds.py     # Threshold comparison plots
      └── templates/            # HTML/JS templates
          ├── base.html         # Base HTML template
          ├── js/               # JavaScript utilities
          │   ├── plotly.min.js # Plotly.js for static version
          │   ├── datatables.js # DataTables for tables
          │   └── utilities.js  # Shared JS utilities
          └── css/              # CSS styles
              └── styles.css    # Custom styles
```

### 2. HTML Report Generator Class

Create a main `HTMLReporter` class that will:

```python
class HTMLReporter:
    """Generate interactive HTML reports from differential expression analysis."""
    
    def __init__(
        self,
        output_dir: str = "kompot_report",
        title: str = "Kompot Analysis Report",
        subtitle: str = None,
        template_dir: str = None,
        use_cdn: bool = False,  # Whether to use CDN for JS libraries
    ):
        """Initialize the HTML reporter."""
        self.output_dir = output_dir
        self.title = title
        self.subtitle = subtitle
        self.template_dir = template_dir or get_default_template_dir()
        self.use_cdn = use_cdn
        self.components = []
        
    def add_differential_expression(
        self, 
        diff_expr: DifferentialExpression,
        condition1_name: str,
        condition2_name: str,
        gene_names: Optional[List[str]] = None,
        top_n: int = 100,
    ):
        """Add differential expression results to the report."""
        # Store results for report generation
        pass
        
    def add_anndata(
        self, 
        adata: "AnnData",
        groupby: str,
        embedding_key: str = "X_umap",
        cell_annotations: List[str] = None,
    ):
        """Add AnnData object with cell annotations for visualizations."""
        pass
        
    def add_comparison(
        self,
        kompot_results: DifferentialExpression,
        other_results: Dict[str, pd.DataFrame],
        comparison_name: str = "Method Comparison",
    ):
        """Add comparison between Kompot and other methods (e.g., DESeq2, Scanpy)."""
        pass
        
    def generate(self, open_browser: bool = True):
        """Generate the HTML report."""
        # 1. Create output directory structure
        # 2. Process data for each component
        # 3. Generate HTML from templates
        # 4. Copy static assets
        # 5. Open browser if requested
        pass
```

### 3. Data Processing Utilities

Create utilities to handle data processing and ensure compatibility with both AnnData objects and numpy arrays:

```python
# In kompot/reporter/utils.py

def prepare_gene_data(
    diff_expr: DifferentialExpression,
    gene_names: Optional[List[str]] = None,
    top_n: int = 100,
) -> pd.DataFrame:
    """Prepare gene expression data for the report."""
    pass
    
def prepare_cell_data(
    adata: "AnnData",
    embedding_key: str = "X_umap",
    groupby: str = None,
) -> Dict[str, np.ndarray]:
    """Prepare cell data for UMAP visualization."""
    pass
    
def generate_plotly_figure(
    x: np.ndarray,
    y: np.ndarray,
    color: np.ndarray = None,
    hover_data: pd.DataFrame = None,
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
) -> Dict:
    """Generate a Plotly figure as JSON."""
    pass
```

### 4. JavaScript Components

Develop JavaScript utilities similar to those in the prototype notebooks:

1. **Plotly Integration**
   - Functions to create and update plots
   - Interaction handlers

2. **Gene Selection Functionality**
   - Search and highlight genes
   - Update multiple plots when a gene is selected

3. **Data Fetching Utilities**
   - Handle loading JSON data for plots and tables
   - Support both standalone HTML and Jupyter notebook environments

### 5. Component Templates

Create HTML/JS templates for each component:

1. **Gene Table Template**
   - Interactive DataTable with customizable columns
   - Filtering, sorting, and searching functionality

2. **UMAP Plot Template**
   - Cell annotation visualization
   - Color selection and scale adjustment controls

3. **Gene Plot Template**
   - Matrix layout for condition comparisons
   - Diagonal/off-diagonal organization

4. **Correlation Plot Template**
   - Method comparison views
   - Interactive point selection

5. **Base Page Template**
   - Overall page structure
   - Navigation between sections

### 6. API Integration

Add the reporting functionality to the main Kompot API:

```python
# In kompot/__init__.py

from kompot.reporter import HTMLReporter

# Example usage:
def generate_report(
    diff_expr: DifferentialExpression,
    output_dir: str = "kompot_report",
    adata: Optional["AnnData"] = None,
    condition1_name: str = "Condition 1",
    condition2_name: str = "Condition 2",
    **kwargs
) -> str:
    """Generate an interactive HTML report for differential expression results.
    
    Returns the path to the generated report.
    """
    reporter = HTMLReporter(output_dir=output_dir, **kwargs)
    reporter.add_differential_expression(
        diff_expr, 
        condition1_name=condition1_name,
        condition2_name=condition2_name
    )
    
    if adata is not None:
        reporter.add_anndata(adata)
        
    report_path = reporter.generate()
    return report_path
```

### 7. Example Script

Create a detailed example script in `examples/generate_report.py`:

```python
#!/usr/bin/env python

"""
Example demonstrating how to use Kompot's interactive HTML report generation.
"""

import numpy as np
import scanpy as sc
import pandas as pd
import kompot
from kompot.reporter import HTMLReporter

# Load existing AnnData or create synthetic data
# ...

# Run Kompot analysis
diff_abundance = kompot.DifferentialAbundance(n_landmarks=200)
diff_abundance.fit(X_condition1, X_condition2)

diff_expression = kompot.DifferentialExpression(
    n_landmarks=200,
    differential_abundance=diff_abundance
)
diff_expression.fit(
    X_condition1, y_condition1, 
    X_condition2, y_condition2
)

# Generate report
reporter = HTMLReporter(
    output_dir="kompot_report",
    title="Differential Expression Analysis",
    subtitle="Condition A vs Condition B"
)

# Add Kompot results
reporter.add_differential_expression(
    diff_expression,
    condition1_name="Condition A",
    condition2_name="Condition B",
    gene_names=gene_names,
    top_n=100
)

# Add AnnData object for cell annotations
reporter.add_anndata(
    adata,
    groupby="cell_type",
    embedding_key="X_umap",
    cell_annotations=["cell_type", "sample", "condition"]
)

# Add comparison with other methods
scanpy_results = pd.DataFrame({
    "gene": gene_names,
    "log2FoldChange": scanpy_log2fc,
    "pvalue": scanpy_pvals,
})

reporter.add_comparison(
    diff_expression,
    {"Scanpy": scanpy_results},
    comparison_name="Kompot vs Scanpy"
)

# Generate the report
report_path = reporter.generate(open_browser=True)
print(f"Report generated at: {report_path}")
```

### 8. File Structure for Generated Reports

```
kompot_report/
  ├── index.html              # Main HTML page
  ├── data/                   # Data files 
  │   ├── gene_data.json      # Gene expression data
  │   ├── cell_data.json      # Cell annotation data
  │   └── method_data.json    # Method comparison data
  ├── plots/                  # Pregenerated plot data
  │   ├── umap_plots/         # UMAP visualizations
  │   ├── gene_plots/         # Gene-specific plots
  │   └── correlation_plots/  # Method comparison plots
  ├── js/                     # JavaScript files
  │   ├── kompot_report.js    # Main report JS
  │   ├── plotly.min.js       # Plotly library
  │   └── datatables.min.js   # DataTables library
  ├── css/                    # CSS stylesheets
  │   └── styles.css          # Main stylesheet
  └── assets/                 # Other assets
      └── favicon.ico         # Favicon
```

## Implementation Details

### 1. Data Handling

1. **Static vs. Dynamic**: The implementation will need to balance between:
   - Precomputing data/plots for better performance
   - Allowing dynamic interaction with the data

2. **File Size Management**:
   - For large datasets, implement data chunking
   - Allow lazy loading of plots and tables

3. **Format Compatibility**:
   - Support multiple input formats (AnnData, numpy arrays, pandas DataFrames)
   - Provide conversion utilities

### 2. JavaScript Implementation

The JavaScript will need to:

1. **Maintain state** across components (selected gene, current view)
2. **Handle events** (clicks, hovers, selections)
3. **Load data** efficiently (chunking, progress indicators)
4. **Render visualizations** responsively

### 3. Extensions and Customization

Allow for customization through:

1. **Custom templates**: Let users provide their own HTML/JS templates
2. **Component selection**: Enable users to include/exclude specific components
3. **Theming**: Support custom CSS or color schemes

## Implementation Steps

1. **Phase 1: Core Components**
   - Implement HTMLReporter class
   - Create basic templates
   - Support for differential expression visualization

2. **Phase 2: Advanced Visualization**
   - Add interactive UMAP plots
   - Add correlation plots
   - Implement gene detail pages

3. **Phase 3: Performance Optimization**
   - Improve data loading with chunking
   - Add caching mechanisms
   - Optimize large dataset handling

4. **Phase 4: Extension API**
   - Define customization interfaces
   - Add plugin system for custom visualizations
   - Document extension points

## Example Implementation File: Reporter Class

The `html_generator.py` file would implement the `HTMLReporter` class with methods for:

1. Processing differential expression results
2. Handling AnnData objects and cell annotations
3. Comparing different analysis methods
4. Generating plot data
5. Creating the final HTML report

## Example Base HTML Template

A basic HTML template would include:

1. Sections for top genes, cell annotations, gene search, and method comparisons
2. Interactive controls (dropdowns, sliders, search inputs)
3. Containers for plots and tables
4. JavaScript initialization code

This implementation plan provides a comprehensive roadmap for adding interactive HTML report generation to the Kompot package, making it easy for users to explore and share their differential expression analysis results.