# OpenFastTrace Analysis Tool

A Python tool for analyzing and visualizing OpenFastTrace aspec reports, with a focus on identifying broken chains, dependencies, and version issues.

Learn more about OpenFastTrace at: [itsallcode/openfasttrace](https://github.com/itsallcode/openfasttrace)

## Features

- 🔍 **Trace Chain Analysis**: Visualize and analyze chains of dependent specification items
- 🚨 **Failure Detection**: Identify broken chains and the reasons for failures
- 🎨 **Rich Terminal Output**: Beautiful console visualizations with colors and Unicode symbols
- 🧠 **Intelligent Analysis**: Detects orphaned items, shallow coverage, and outdated versions

## Installation

```bash
pip install oft-trace
```

## Usage
### Command Line Interface
The tool provides several commands:

#### Overview Analysis

```bash
oft-trace trace path/to/report.aspec
```

#### Analyzing a Specific Item

```bash
oft-trace trace path/to/report.aspec ITEM-123
```


#### Finding Broken Chains

```bash
oft-trace trace-failures path/to/report.aspec
```
#### Listing Items with Filtering

```bash
oft-trace list-items path/to/report.aspec --doctype req --coverage UNCOVERED
```

#### Common Options
- `--output/-o`: Path to output file (HTML or text)
- `--limit/-l`: Limit the number of items to analyze
- `--doctype/-t`: Filter by document type
- `--coverage/-c`: Filter by coverage status (`COVERED`, `UNCOVERED`, `ORPHANED`, `SHALLOW`, `OUTDATED`)
- `--direction/-d`: Direction of links to trace (`both`, `incoming`, `outgoing`)

## Understanding the Reports
### Coverage Types

✅ `COVERED` - Item is fully covered
🔍 `ORPHANED` - Item is not covered by any other items
⚠️ `SHALLOW` - Item has shallow coverage but misses deep coverage
♻️ `OUTDATED` - Item has version mismatch issues
❌ `UNCOVERED` - Item is completely uncovered

#### Example Terminal Output

```bash
FAILURE 1/5: req~payment-processing~2 [req]
Title: System must process payments securely

Failure reasons:
- ♻️ Version mismatch: arch-payment-module covers v1 but v2 is expected
- ❌ Missing coverage for types: impl

Trace chain visualization:
└── ❌ req~payment-processing~2 (v2) [req] (/specs/requirements.md:45)
    └── ♻️ VERSION MISMATCH: Covering v1 but v2 expected
        └── ⚠️ arch-payment-module~1 (v1) [arch] (/specs/architecture.md:67)
```


## Advanced Usage

### Programmatic Usage
You can also use the library programmatically in your Python code:

```python
from oft_trace.analyzer import TraceAnalyzer
from oft_trace.parser import parse_aspec_file

# Parse the file
result = parse_aspec_file("path/to/report.aspec")
spec_items, id_map, covering_map, covered_by_map, broken_chains = result

# Create analyzer
analyzer = TraceAnalyzer(spec_items, id_map, covering_map, covered_by_map, broken_chains)

```


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


**This tool was generated with the assistance of AI technology.**

