from pathlib import Path
from typing import Union, Dict, List
import logging
import pandas as pd
from Bio import SeqIO
import shutil

from .processor import AmpliconProcessor

logger = logging.getLogger(__name__)

def process_samples(
    fastq_dir: Union[str, Path],
    reference: Union[str, Path],
    output_dir: Union[str, Path, None] = None,
    threads: int = 4,
    min_base_quality: int = 20,
    min_mapping_quality: int = 30,
    min_read_count: int = 10,
    max_file_size: int = 10_000_000_000,
    bed_path: Union[str, Path, None] = None,
    max_indel_size: int = 50
) -> Dict[str, pd.DataFrame]:
    """
    Process all samples in a directory.

    Args:
        fastq_dir: Directory containing FASTQ files
        reference: Path to reference FASTA file
        output_dir: Directory for output files (default: fastq_dir/results)
        threads: Number of threads to use
        min_base_quality: Minimum base quality score
        min_mapping_quality: Minimum mapping quality score
        min_read_count: Minimum number of reads to consider a haplotype
        max_file_size: Maximum file size in bytes
        bed_path: Optional path to BED file for indel comparison
        max_indel_size: Maximum size of indels to consider as small indels

    Returns:
        Dictionary mapping sample names to their results DataFrames
    """
    fastq_dir = Path(fastq_dir)
    reference = Path(reference)
    output_dir = Path(output_dir) if output_dir else fastq_dir / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize processor
    processor = AmpliconProcessor(
        reference_path=reference,
        bed_path=bed_path,
        min_base_quality=min_base_quality,
        min_mapping_quality=min_mapping_quality,
        min_read_count=min_read_count,
        max_file_size=max_file_size,
        max_indel_size=max_indel_size
    )

    # Process each sample
    results = {}
    for r1_file in sorted(fastq_dir.glob('*_R1_001.fastq*')):  # Handle both .fastq and .fastq.gz
        # Get matching R2 file
        r2_file = r1_file.parent / r1_file.name.replace('_R1_', '_R2_')
        if not r2_file.exists():
            logger.warning(f"No R2 file found for {r1_file.name}")
            continue

        # Get sample name
        sample_name = r1_file.name.split('_R1_')[0]
        logger.info(f"Processing sample: {sample_name}")

        try:
            results[sample_name] = processor.process_sample(
                fastq_r1=r1_file,
                fastq_r2=r2_file,
                output_dir=output_dir / sample_name,
                threads=threads
            )
        except Exception as e:
            logger.error(f"Error processing sample {sample_name}: {str(e)}")
            continue

    return results

def summarize_results(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a summary of results across all samples."""
    if not results:
        return pd.DataFrame()
        
    summaries = []
    for sample, df in results.items():
        if df.empty:
            continue
            
        try:
            total_reads = df['count'].sum()
            summary = {
                'sample': sample,
                'total_reads': total_reads,
                'unique_haplotypes': len(df),
                'max_frequency': df['frequency'].max(),
                'avg_mutations': (df['mutations'] * df['count']).sum() / total_reads if total_reads > 0 else 0,
                'full_length_reads': df[df['is_full_length']]['count'].sum(),
                'full_length_percent': (df[df['is_full_length']]['count'].sum() / total_reads * 100) if total_reads > 0 else 0
            }
            
            # Add single mutation stats if available
            if 'single_mutations' in df.columns:
                single_mut_reads = df[df['mutations'] == 1]['count'].sum()
                summary.update({
                    'single_mutation_reads': single_mut_reads,
                    'single_mutation_percent': (single_mut_reads / total_reads * 100) if total_reads > 0 else 0
                })
            
            summaries.append(summary)
        except Exception as e:
            logger.error(f"Error summarizing results for {sample}: {str(e)}")
            continue
    
    summary_df = pd.DataFrame(summaries)
    
    # Format numeric columns
    if not summary_df.empty:
        # Round percentages to 2 decimal places
        for col in ['max_frequency', 'full_length_percent', 'single_mutation_percent']:
            if col in summary_df.columns:
                summary_df[col] = summary_df[col].round(2)
        
        # Round average mutations to 2 decimal places
        if 'avg_mutations' in summary_df.columns:
            summary_df['avg_mutations'] = summary_df['avg_mutations'].round(2)
    
    return summary_df

def validate_input(
    fastq_dir: Union[str, Path],
    reference: Union[str, Path]
) -> List[str]:
    """
    Validate input files and return any warnings.

    Args:
        fastq_dir: Directory containing FASTQ files
        reference: Path to reference FASTA file

    Returns:
        List of warning messages, empty if all valid
    """
    warnings = []
    
    # Check reference file
    ref_path = Path(reference)
    if not ref_path.exists():
        warnings.append(f"Reference file not found: {ref_path}")
    elif ref_path.stat().st_size == 0:
        warnings.append(f"Reference file is empty: {ref_path}")
    else:
        # Validate FASTA format
        try:
            with open(ref_path) as handle:
                records = list(SeqIO.parse(handle, "fasta"))
                if not records:
                    warnings.append(f"No valid FASTA sequences found in: {ref_path}")
        except Exception as e:
            warnings.append(f"Error reading reference file: {str(e)}")

    # Check BWA index files
    for ext in ['.amb', '.ann', '.bwt', '.pac', '.sa']:
        if not (ref_path.parent / (ref_path.name + ext)).exists():
            warnings.append(f"BWA index file missing: {ref_path}{ext}")

    # Check required executables
    for cmd in ['bwa', 'samtools']:
        if not shutil.which(cmd):
            warnings.append(f"Required program not found: {cmd}")

    # Check FASTQ directory
    fastq_dir = Path(fastq_dir)
    if not fastq_dir.is_dir():
        warnings.append(f"FASTQ directory not found: {fastq_dir}")
    else:
        # Look for both .fastq and .fastq.gz files
        r1_files = list(fastq_dir.glob('*_R1_001.fastq*'))
        if not r1_files:
            warnings.append(f"No R1 FASTQ files found in: {fastq_dir}")
        
        # Check for matching R2 files
        for r1 in r1_files:
            r2 = r1.parent / r1.name.replace('_R1_', '_R2_')
            if not r2.exists():
                warnings.append(f"No matching R2 file for: {r1.name}")
            
            # Check file sizes
            try:
                if r1.stat().st_size == 0:
                    warnings.append(f"Empty R1 file: {r1.name}")
                if r2.exists() and r2.stat().st_size == 0:
                    warnings.append(f"Empty R2 file: {r2.name}")
            except Exception as e:
                warnings.append(f"Error checking file sizes: {str(e)}")

    return warnings

def load_results(results_dir: Union[str, Path]) -> Dict[str, pd.DataFrame]:
    """Load previously generated results from CSV files."""
    results_dir = Path(results_dir)
    results = {}
    
    try:
        # Look for results in sample subdirectories
        for csv_file in results_dir.rglob('*_haplotypes.csv'):
            sample_name = csv_file.name.replace('_haplotypes.csv', '')
            try:
                df = pd.read_csv(csv_file)
                
                # Ensure required columns are present
                required_cols = ['reference', 'haplotype', 'count', 'frequency', 'mutations']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    logger.warning(f"Results file {csv_file} missing columns: {missing_cols}")
                    continue
                    
                results[sample_name] = df
                logger.debug(f"Loaded results for sample: {sample_name}")
                
            except Exception as e:
                logger.error(f"Error loading results for {sample_name}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error scanning results directory: {str(e)}")
    
    return results