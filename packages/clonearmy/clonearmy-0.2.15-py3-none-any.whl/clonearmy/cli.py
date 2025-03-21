import sys
from pathlib import Path
from typing import Optional
import time
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint
from Bio import SeqIO

from . import process_samples, summarize_results, validate_input, __version__
from .report import generate_report
from .comparison import run_comparative_analysis

console = Console()

def load_reference_sequence(reference_path: Path) -> str:
    """Load the reference sequence from a FASTA file."""
    try:
        with open(reference_path) as handle:
            record = next(SeqIO.parse(handle, "fasta"))
            return str(record.seq)
    except Exception as e:
        console.print(f"[bold red]Error loading reference sequence:[/] {str(e)}")
        sys.exit(1)

def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"CloneArmy version [bold cyan]{__version__}[/]")
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version and exit.")
@click.option('--debug/--no-debug', default=False, help="Enable debug logging.")
def cli(debug: bool):
    """
    CloneArmy: Analyze haplotypes from Illumina paired-end amplicon sequencing.
    
    This tool processes FASTQ files to identify and quantify sequence variants
    and haplotypes in amplicon sequencing data.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

@cli.command()
@click.argument('fastq_dir', type=click.Path(exists=True))
@click.argument('reference', type=click.Path(exists=True))
@click.option('--threads', '-t', default=8, help='Number of threads to use')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--min-base-quality', '-q', default=20, 
              help='Minimum base quality score')
@click.option('--min-mapping-quality', '-Q', default=30,
              help='Minimum mapping quality score')
@click.option('--min-read-count', '-r', default=10,
              help='Minimum number of reads to consider a haplotype')
@click.option('--max-file-size', '-m', default=10_000_000_000,
              help='Maximum file size in bytes (default: 10GB)')
@click.option('--report/--no-report', default=True,
              help='Generate HTML report')
@click.option('--bed', '-b', type=click.Path(exists=True),
              help='BED file for comparing indel positions')
@click.option('--max-indel-size', '-i', default=50,
              help='Maximum size of indels to consider as small indels')
def run(fastq_dir: str, reference: str, threads: int, output: Optional[str],
        min_base_quality: int, min_mapping_quality: int, min_read_count: int,
        max_file_size: int, report: bool, bed: Optional[str], max_indel_size: int):
    """Process FASTQ files and analyze mutations.

    FASTQ_DIR: Directory containing paired FASTQ files (_R1.fastq.gz and _R2.fastq.gz)
    REFERENCE: Reference sequence in FASTA format
    """
    start_time = time.time()
    
    # Validate input files
    fastq_dir = Path(fastq_dir)
    reference = Path(reference)
    output_dir = Path(output) if output else fastq_dir / 'results'
    bed_path = Path(bed) if bed else None
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Validating input files...", total=None)
        try:
            validate_input(fastq_dir, reference)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            sys.exit(1)
        progress.update(task, completed=True)
        
        # Load reference sequence
        task = progress.add_task("Loading reference sequence...", total=None)
        ref_seq = load_reference_sequence(reference)
        progress.update(task, completed=True)
        
        # Process samples
        task = progress.add_task("Processing samples...", total=None)
        try:
            results = process_samples(
                fastq_dir=fastq_dir,
                reference=reference,
                output_dir=output_dir,
                threads=threads,
                min_base_quality=min_base_quality,
                min_mapping_quality=min_mapping_quality,
                min_read_count=min_read_count,
                max_file_size=max_file_size,
                bed_path=bed_path,
                max_indel_size=max_indel_size
            )
        except Exception as e:
            console.print(f"[bold red]Error processing samples:[/] {str(e)}")
            sys.exit(1)
        progress.update(task, completed=True)
        
        # Generate summary
        task = progress.add_task("Generating summary...", total=None)
        summary = summarize_results(results)
        progress.update(task, completed=True)
        
        # Generate report
        if report:
            task = progress.add_task("Generating report...", total=None)
            try:
                report_path = output_dir / 'report.html'
                generate_report(results, summary, report_path, ref_seq)
                progress.update(task, completed=True)
            except Exception as e:
                console.print(f"[bold red]Error generating report:[/] {str(e)}")
                sys.exit(1)
    
    # Print summary table
    if summary is not None and not summary.empty:
        table = Table(title="Analysis Summary")
        for col in summary.columns:
            table.add_column(col)
        for _, row in summary.iterrows():
            table.add_row(*[str(x) for x in row])
        console.print(table)
    
    elapsed = time.time() - start_time
    console.print(f"\n[green]Analysis completed in {elapsed:.1f} seconds[/]")

@cli.command()
@click.argument('fastq_dir1', type=click.Path(exists=True))
@click.argument('fastq_dir2', type=click.Path(exists=True))
@click.argument('reference', type=click.Path(exists=True))
@click.option('--threads', '-t', default=8, help='Number of threads to use')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--min-base-quality', '-q', default=20, 
              help='Minimum base quality score')
@click.option('--min-mapping-quality', '-Q', default=30,
              help='Minimum mapping quality score')
@click.option('--min-read-count', '-r', default=10,
              help='Minimum number of reads to consider a haplotype')
@click.option('--max-file-size', '-m', default=10_000_000_000,
              help='Maximum file size in bytes (default: 10GB)')
@click.option('--full-length-only', '-f', is_flag=True,
              help='Only consider sequences that cover the entire reference')
@click.option('--bed', '-b', type=click.Path(exists=True),
              help='BED file for comparing indel positions')
@click.option('--max-indel-size', '-i', default=50,
              help='Maximum size of indels to consider as small indels')
def compare(fastq_dir1: str, fastq_dir2: str, reference: str, threads: int, 
           output: Optional[str], min_base_quality: int, min_mapping_quality: int,
           min_read_count: int, max_file_size: int, full_length_only: bool,
           bed: Optional[str], max_indel_size: int):
    """Compare two sets of FASTQ files and analyze differences.

    FASTQ_DIR1: First directory containing paired FASTQ files
    FASTQ_DIR2: Second directory containing paired FASTQ files
    REFERENCE: Reference sequence in FASTA format
    """
    start_time = time.time()
    
    # Validate input files
    fastq_dir1 = Path(fastq_dir1)
    fastq_dir2 = Path(fastq_dir2)
    reference = Path(reference)
    output_dir = Path(output) if output else Path('comparison_results')
    bed_path = Path(bed) if bed else None
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Validating input files...", total=None)
        try:
            validate_input(fastq_dir1, reference)
            validate_input(fastq_dir2, reference)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            sys.exit(1)
        progress.update(task, completed=True)
        
        # Load reference sequence
        task = progress.add_task("Loading reference sequence...", total=None)
        ref_seq = load_reference_sequence(reference)
        progress.update(task, completed=True)
        
        # Run comparison
        task = progress.add_task("Running comparison...", total=None)
        try:
            results = run_comparative_analysis(
                fastq_dir1=fastq_dir1,
                fastq_dir2=fastq_dir2,
                reference_path=reference,
                output_dir=output_dir,
                threads=threads,
                min_base_quality=min_base_quality,
                min_mapping_quality=min_mapping_quality,
                min_read_count=min_read_count,
                max_file_size=max_file_size,
                full_length_only=full_length_only,
                bed_path=bed_path,
                max_indel_size=max_indel_size
            )
        except Exception as e:
            console.print(f"[bold red]Error running comparison:[/] {str(e)}")
            sys.exit(1)
        progress.update(task, completed=True)
    
    elapsed = time.time() - start_time
    console.print(f"\n[green]Comparison completed in {elapsed:.1f} seconds[/]")

if __name__ == '__main__':
    cli()