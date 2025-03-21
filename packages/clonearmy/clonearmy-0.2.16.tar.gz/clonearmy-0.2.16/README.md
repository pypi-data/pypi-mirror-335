# CloneArmy

CloneArmy is a modern Python package for analyzing haplotypes from Illumina paired-end amplicon sequencing data. It provides a streamlined workflow for processing FASTQ files, aligning reads, identifying sequence variants, and performing comparative analyses between samples.

## Features

- Fast paired-end read processing using BWA-MEM
- Quality-based filtering of bases and alignments
- Haplotype identification and frequency analysis
- Statistical comparison between samples with FDR correction
- Interactive visualization of mutation frequencies
- Rich command-line interface with progress tracking and tabular output
- Comprehensive HTML reports
- Multi-threading support
- Support for full-length sequence analysis
- Real-time progress monitoring with progress bars
- Automatic downsampling of large FASTQ files
- Exportable results in multiple formats (CSV, JSON, Excel)

## Installation

```bash
pip install clonearmy
```

### Requirements

- Python ≥ 3.8
- BWA (must be installed and available in PATH)
- Samtools (must be installed and available in PATH)
- Seqtk (must be installed and available in PATH)

You can install the required tools using conda:
```bash
conda install -c bioconda bwa samtools seqtk
```

## Usage

### Command Line Interface

#### Basic Analysis

```bash
# Basic usage with progress tracking
clonearmy run /path/to/fastq/directory reference.fasta

# With all options
clonearmy run /path/to/fastq/directory reference.fasta \
    --threads 8 \
    --output results \
    --min-base-quality 20 \
    --min-mapping-quality 30 \
    --min-read-count 10 \
    --max-file-size 100000000 \  # Target size for downsampling (100MB)
    --report  # Generate HTML report (default: true)
```

The `--max-file-size` option specifies the target size for downsampling large FASTQ files. If your input files are larger than this size, they will be automatically downsampled while maintaining paired-end relationships. This is useful for quick testing or when working with very large datasets. The size is specified in bytes (e.g., 100000000 for 100MB).

#### Comparative Analysis

```bash
# Compare two samples
clonearmy compare \
    /path/to/sample1/fastq \
    /path/to/sample2/fastq \
    reference.fasta \
    --threads 8 \
    --output comparison_results \
    --min-base-quality 20 \
    --min-mapping-quality 30 \
    --min-read-count 10 \
    --max-file-size 100000000 \  # Target size for downsampling (100MB)
    --full-length-only  # Only consider full-length sequences
```

### Output Examples

#### Sample Analysis Results
```
╒════════════════╤══════════╤════════════╤══════════════╕
│ Sample         │ Reads    │ Haplotypes │ Mutations    │
╞════════════════╪══════════╪════════════╪══════════════╡
│ sample1        │ 10000    │ 45         │ 2.3 avg      │
│ sample2        │ 12000    │ 52         │ 1.8 avg      │
╘════════════════╧══════════╧════════════╧══════════════╛
```

#### Comparative Analysis Results
```
╒══════════╤════════════╤════════════╤═══════════╤═══════════╕
│ Position │ Sample 1 % │ Sample 2 % │ P-value   │ FDR       │
╞══════════╪════════════╪════════════╪═══════════╪═══════════╡
│ 123 A>T  │ 45.2      │ 12.3       │ 0.001     │ 0.003     │
│ 456 G>C  │ 33.1      │ 28.9       │ 0.042     │ 0.063     │
╘══════════╧════════════╧════════════╧═══════════╧═══════════╛
```

### Python API

```python
from pathlib import Path
from clone_army.processor import AmpliconProcessor
from clone_army.comparison import run_comparative_analysis

# Initialize processor with automatic downsampling
processor = AmpliconProcessor(
    reference_path="reference.fasta",
    min_base_quality=20,
    min_mapping_quality=30,
    min_read_count=10,
    max_file_size=100_000_000  # 100MB target size
)

# Process samples
results1 = processor.process_sample(
    fastq_r1="sample1_R1.fastq.gz",
    fastq_r2="sample1_R2.fastq.gz",
    output_dir="results/sample1",
    threads=4
)

results2 = processor.process_sample(
    fastq_r1="sample2_R1.fastq.gz",
    fastq_r2="sample2_R2.fastq.gz",
    output_dir="results/sample2",
    threads=4
)

# Perform comparative analysis
comparison_results = run_comparative_analysis(
    results1=results1,
    results2=results2,
    reference_seq=ref_seq,
    output_path="comparison_results.csv",
    full_length_only=False
)
```

## Output Files

### Single Sample Analysis
- Sorted BAM file with alignments
- `{sample}_haplotypes.csv` containing:
  - Sequence
  - Read count
  - Frequency
  - Number of mutations
  - Full-length status
  - Quality metrics
- Interactive HTML report with:
  - Summary statistics
  - Mutation frequency plots
  - Position-based mutation diversity plots
  - Mutation spectrum analysis
- Console output with summary statistics

### Comparative Analysis
- `comparison_results.csv` with statistical comparisons:
  - Mutation positions and types
  - Frequencies in each sample
  - Statistical significance (p-values)
  - FDR-corrected p-values
- Interactive HTML plots:
  - Mutation frequency comparison
  - Position-based mutation diversity
- Console output with significant mutations