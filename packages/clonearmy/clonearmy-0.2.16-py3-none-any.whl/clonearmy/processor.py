from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
from typing import List, Dict, Generator, Tuple, Set, Union
import logging
from collections import Counter, defaultdict
import shutil
import click

import pysam
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Align import PairwiseAligner
from rich.progress import track
import pyranges as pr

logger = logging.getLogger(__name__)

@dataclass
class AmpliconRead:
    """Represents a processed amplicon read pair."""
    sequence: str
    mutations: int
    quality: float
    indels: List[Dict]  # Add indels field

class AmpliconProcessor:
    """Process amplicon sequencing data."""
    
    def __init__(self, 
                 reference_path: Union[str, Path],
                 bed_path: Union[str, Path, None] = None,
                 min_base_quality: int = 20,
                 min_mapping_quality: int = 30,
                 min_read_count: int = 10,
                 max_file_size: int = 10_000_000_000,
                 max_indel_size: int = 50):  # Add max_indel_size parameter
        """
        Initialize the processor.
        
        Args:
            reference_path: Path to reference FASTA file
            bed_path: Optional path to BED file for indel comparison
            min_base_quality: Minimum base quality score
            min_mapping_quality: Minimum mapping quality score
            min_read_count: Minimum number of reads to consider a haplotype
            max_file_size: Maximum file size in bytes
            max_indel_size: Maximum size of indels to consider as "small" indels
        """
        self.reference_path = Path(reference_path)
        self.bed_path = Path(bed_path) if bed_path else None
        self.min_base_quality = min_base_quality
        self.min_mapping_quality = min_mapping_quality
        self.min_read_count = min_read_count
        self.max_file_size = max_file_size
        self.max_indel_size = max_indel_size
        
        # Load reference sequences
        self.reference = {}
        try:
            for record in SeqIO.parse(self.reference_path, "fasta"):
                self.reference[record.id] = str(record.seq)
        except Exception as e:
            logger.error(f"Error loading reference sequences: {str(e)}")
            raise
            
        # Load BED regions if provided
        self.bed_regions = None
        if self.bed_path:
            try:
                self.bed_regions = pr.read_bed(str(self.bed_path))
            except Exception as e:
                logger.error(f"Error loading BED file: {str(e)}")
                raise
        
        # Initialize aligner for indel detection
        self.aligner = PairwiseAligner()
        self.aligner.mode = 'global'
        self.aligner.match_score = 2
        self.aligner.mismatch_score = -1
        self.aligner.open_gap_score = -2
        self.aligner.extend_gap_score = -0.5
        
        # Check for required executables and index files
        self._check_dependencies()
        self._check_and_create_bwa_index()

    def _load_reference(self) -> Dict[str, str]:
        """Load reference sequences."""
        try:
            reference_dict = {}
            with open(self.reference_path) as handle:
                for record in SeqIO.parse(handle, "fasta"):
                    reference_dict[record.id] = str(record.seq)
            if not reference_dict:
                raise ValueError(f"No sequences found in reference file: {self.reference_path}")
            return reference_dict
        except Exception as e:
            logger.error(f"Error loading reference sequence: {str(e)}")
            raise

    def _check_dependencies(self):
        """Check if required external programs are available."""
        for cmd in ['bwa', 'samtools', 'seqtk']:
            if not shutil.which(cmd):
                raise RuntimeError(f"{cmd} not found in PATH. Please install {cmd}.")

    def _check_and_create_bwa_index(self):
        """Check if BWA index files exist, create them if they don't."""
        index_extensions = ['.amb', '.ann', '.bwt', '.pac', '.sa']
        missing_indices = [ext for ext in index_extensions 
                         if not (self.reference_path.parent / f"{self.reference_path.name}{ext}").exists()]
        
        if missing_indices:
            logger.info(f"Creating BWA index for {self.reference_path}")
            with click.progressbar(length=1, label='Indexing reference', show_eta=True) as bar:
                try:
                    # First check if reference file exists
                    if not self.reference_path.exists():
                        raise RuntimeError(f"Reference file not found: {self.reference_path}")
                    
                    # Check if reference file is empty
                    if self.reference_path.stat().st_size == 0:
                        raise RuntimeError(f"Reference file is empty: {self.reference_path}")
                    
                    # Run BWA index with detailed error capture
                    result = subprocess.run(
                        ['bwa', 'index', str(self.reference_path)],
                        check=True,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        text=True
                    )
                    
                    # Verify index creation
                    still_missing = [ext for ext in index_extensions 
                                   if not (self.reference_path.parent / f"{self.reference_path.name}{ext}").exists()]
                    
                    if still_missing:
                        raise RuntimeError(f"BWA indexing failed to create files: {', '.join(still_missing)}")
                    
                    bar.update(1)
                    logger.info("BWA index created successfully")
                    
                except subprocess.CalledProcessError as e:
                    error_msg = f"BWA indexing failed: {e.stderr}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                except Exception as e:
                    error_msg = f"Error during BWA indexing: {str(e)}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

    def _align_sequence_to_reference(self, sequence: str, ref_seq: str) -> str:
        """Align a sequence to reference to detect indels and mutations."""
        try:
            # Get the best alignment
            alignments = self.aligner.align(ref_seq, sequence)
            if len(alignments) == 0:
                logger.warning("No alignment found, returning original sequence")
                return sequence
                
            alignment = alignments[0]
            
            # Get the target and query sequences from the alignment
            target_seq = str(alignment.target)
            query_seq = str(alignment.query)
            
            # Process the alignment to mark mutations and gaps
            result = []
            for t, q in zip(target_seq, query_seq):
                if t == '-':  # Insertion relative to reference
                    result.append(q.lower())
                elif q == '-':  # Deletion relative to reference
                    result.append('-')
                elif t.upper() != q.upper():  # Mismatch
                    result.append(q.lower())
                else:  # Match
                    result.append(q.upper())
            
            return ''.join(result)
            
        except Exception as e:
            logger.error(f"Error in sequence alignment: {str(e)}")
            return sequence

    def _reconstruct_sequence(self,
                            read1: pysam.AlignedSegment,
                            read2: pysam.AlignedSegment,
                            ref_seq: str) -> str:
        """Reconstruct the amplicon sequence from paired reads."""
        sequence = list(ref_seq.upper())
        
        for read in (read1, read2):
            read_seq = read.query_sequence
            ref_pos = read.reference_start
            
            query_pos = 0
            for op, length in read.cigartuples:
                if op == 0:  # Match or mismatch
                    for i in range(length):
                        if (read.query_qualities[query_pos + i] >= self.min_base_quality and
                            ref_pos + i < len(sequence)):
                            base = read_seq[query_pos + i].upper()
                            if base != ref_seq[ref_pos + i].upper():
                                sequence[ref_pos + i] = base.lower()
                            else:
                                sequence[ref_pos + i] = base.upper()
                    query_pos += length
                    ref_pos += length
                elif op == 1:  # Insertion
                    if ref_pos < len(sequence):
                        sequence[ref_pos] = '-'
                    query_pos += length
                elif op == 2:  # Deletion
                    for i in range(length):
                        if ref_pos + i < len(sequence):
                            sequence[ref_pos + i] = '-'
                    ref_pos += length
                elif op == 4:  # Soft clip
                    query_pos += length
        
        reconstructed = ''.join(sequence)
        return self._align_sequence_to_reference(reconstructed, ref_seq)

    def _is_full_length(self, sequence: str, ref_seq: str) -> bool:
        """Check if a sequence covers the full reference length."""
        seq_no_indels = sequence.replace('-', '')
        ref_no_indels = ref_seq.replace('-', '')
        
        if len(seq_no_indels) != len(ref_no_indels):
            return False
            
        if sequence.startswith('-') or sequence.endswith('-'):
            return False
        if sequence.startswith('N') or sequence.endswith('N'):
            return False
            
        return True

    def _get_read_pairs(self, 
                       bam: pysam.AlignmentFile,
                       ref_name: str) -> Generator[Tuple[pysam.AlignedSegment, pysam.AlignedSegment], None, None]:
        """Generate properly paired reads."""
        reads = {}
        for read in bam.fetch(ref_name):
            if (not read.is_proper_pair or 
                read.is_secondary or 
                read.is_supplementary or 
                read.mapping_quality < self.min_mapping_quality):
                continue
                
            qname = read.query_name
            if qname in reads:
                pair = reads.pop(qname)
                yield (read, pair) if read.is_read1 else (pair, read)
            else:
                reads[qname] = read

    def _align_reads(self, 
                    fastq_r1: Path,
                    fastq_r2: Path, 
                    temp_dir: Path,
                    output_dir: Path,
                    threads: int) -> Path:
        """Align reads using BWA-MEM and convert to sorted BAM."""
        sample_name = fastq_r1.stem.replace("_R1_001.fastq", "")
        temp_sam = temp_dir / f"{sample_name}.sam"
        temp_bam = temp_dir / f"{sample_name}.temp.bam"
        final_bam = output_dir / f"{sample_name}.bam"
        
        try:
            with click.progressbar(length=4, label='Aligning and processing reads') as bar:
                # Run BWA-MEM
                bwa_cmd = [
                    'bwa', 'mem',
                    '-t', str(threads),
                    str(self.reference_path),
                    str(fastq_r1),
                    str(fastq_r2)
                ]
                
                with open(temp_sam, 'w') as sam_out:
                    click.echo("\nRunning BWA alignment...")
                    logger.debug(f"Running BWA: {' '.join(bwa_cmd)}")
                    subprocess.run(
                        bwa_cmd,
                        stdout=sam_out,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                bar.update(1)
                
                # Convert SAM to BAM
                click.echo("Converting SAM to BAM...")
                subprocess.run(
                    ['samtools', 'view', '-b', '-@', str(threads), '-o', str(temp_bam), str(temp_sam)],
                    check=True,
                    stderr=subprocess.PIPE
                )
                bar.update(1)
                
                # Sort BAM
                click.echo("Sorting BAM file...")
                subprocess.run(
                    [
                        'samtools', 'sort',
                        '-@', str(threads),
                        '-m', '1G',
                        '-T', str(temp_dir / f"{sample_name}.sort"),
                        '-o', str(final_bam),
                        str(temp_bam)
                    ],
                    check=True,
                    stderr=subprocess.PIPE
                )
                bar.update(1)
                
                # Index BAM
                click.echo("Indexing BAM file...")
                subprocess.run(
                    ['samtools', 'index', str(final_bam)],
                    check=True,
                    stderr=subprocess.PIPE
                )
                bar.update(1)
            
            return final_bam
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Alignment failed: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Alignment failed: {str(e)}")
        finally:
            for temp_file in [temp_sam, temp_bam]:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except:
                    pass

    def _process_alignments(self, 
                          bam_path: Path,
                          ref_name: str) -> Generator[AmpliconRead, None, None]:
        """Process aligned reads for a reference sequence."""
        try:
            bam = pysam.AlignmentFile(bam_path, "rb")
            ref_seq = self.reference[ref_name]
            
            # First count total read pairs
            total_pairs = 0
            reads = {}
            for read in bam.fetch(ref_name):
                if (not read.is_proper_pair or 
                    read.is_secondary or 
                    read.is_supplementary or 
                    read.mapping_quality < self.min_mapping_quality):
                    continue
                    
                qname = read.query_name
                if qname in reads:
                    total_pairs += 1
                    reads.pop(qname)
                else:
                    reads[qname] = read
            
            # Reset file pointer
            bam.reset()
            reads.clear()
            
            if total_pairs == 0:
                click.echo(f"No valid read pairs found for {ref_name}")
                return
                
            with click.progressbar(length=total_pairs, 
                                 label=f'Processing reads for {ref_name}') as bar:
                for read in bam.fetch(ref_name):
                    if (not read.is_proper_pair or 
                        read.is_secondary or 
                        read.is_supplementary or 
                        read.mapping_quality < self.min_mapping_quality):
                        continue
                        
                    qname = read.query_name
                    if qname in reads:
                        pair = reads.pop(qname)
                        read1, read2 = (read, pair) if read.is_read1 else (pair, read)
                        
                        sequence = self._reconstruct_sequence(read1, read2, ref_seq)
                        mutations = sum(1 for base in sequence if base.islower() or base == '-')
                        quality = (read1.mapping_quality + read2.mapping_quality) / 2
                        
                        bar.update(1)
                        yield AmpliconRead(sequence=sequence, mutations=mutations, quality=quality, indels=[])
                    else:
                        reads[qname] = read
            
        except Exception as e:
            logger.error(f"Error processing alignments for {ref_name}: {str(e)}")
            raise
        finally:
            if 'bam' in locals():
                bam.close()

    def _analyze_amplicons(self,
                          amplicon_reads: List[AmpliconRead],
                          ref_name: str) -> List[Dict]:
        """Analyze processed amplicon reads."""
        results = []
        
        if not amplicon_reads:
            logger.warning(f"No valid reads found for reference {ref_name}")
            return results
        
        # Count total reads and calculate initial statistics
        haplotype_counts = Counter(read.sequence for read in amplicon_reads)
        total_reads = sum(haplotype_counts.values())
        ref_seq = self.reference[ref_name].upper()
        
        logger.info(f"Found {len(haplotype_counts)} unique haplotypes from {total_reads} total reads for {ref_name}")
        
        # Filter by minimum read count
        filtered_haplotypes = {seq: count for seq, count in haplotype_counts.items() 
                             if count >= self.min_read_count}
        
        if not filtered_haplotypes:
            logger.warning(f"No haplotypes met minimum read count threshold ({self.min_read_count}) for {ref_name}")
            return results
            
        # Calculate statistics for filtered haplotypes
        filtered_total = sum(filtered_haplotypes.values())
        filtered_count = len(haplotype_counts) - len(filtered_haplotypes)
        filtered_reads = total_reads - filtered_total
        
        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} low-count haplotypes "
                f"({filtered_reads:,} reads, {(filtered_reads/total_reads)*100:.1f}%) "
                f"for {ref_name}"
            )
        
        # Process each haplotype that passed the filter
        for haplotype, count in sorted(filtered_haplotypes.items(), key=lambda x: x[1], reverse=True):
            # Calculate frequency based on total reads (not just filtered)
            # This gives a more accurate representation of the haplotype abundance
            frequency = (count / total_reads) * 100
            
            # Count mutations (lowercase bases indicate mutations, '-' indicates indels)
            mutations = sum(1 for base in haplotype if base.islower() or base == '-')
            
            # Validate sequence length and composition
            is_full_length = self._is_full_length(haplotype, ref_seq)
            
            results.append({
                'reference': ref_name,
                'haplotype': haplotype,
                'count': count,
                'frequency': frequency,
                'mutations': mutations,
                'is_full_length': is_full_length
            })
        
        return results

    def _is_indel_in_bed(self, ref_name: str, position: int, indel_size: int) -> bool:
        """Check if an indel overlaps with regions in the BED file.
        
        Args:
            ref_name: Reference sequence name
            position: 1-based position of the indel
            indel_size: Size of the indel
            
        Returns:
            bool: True if indel overlaps with BED regions
        """
        if not self.bed_regions:
            return False
            
        # Convert to 0-based position for pyranges
        pos_0based = position - 1
        
        # Create a small range for the indel
        indel_range = pr.PyRanges(
            chromosomes=[ref_name],
            starts=[pos_0based],
            ends=[pos_0based + abs(indel_size)]
        )
        
        # Check for overlap
        overlap = self.bed_regions.intersect(indel_range)
        return len(overlap) > 0

    def _get_mutation_positions(self, haplotype: str, ref_seq: str, ref_name: str) -> List[Dict[str, str]]:
        """Analyze mutation positions in a haplotype compared to reference.
        
        Args:
            haplotype: The haplotype sequence with mutations in lowercase
            ref_seq: The reference sequence
            ref_name: Name of the reference sequence
            
        Returns:
            List of dictionaries containing mutation information
        """
        mutations = []
        pos = 0  # 0-based position in reference
        hap_pos = 0  # 0-based position in haplotype
        
        while hap_pos < len(haplotype):
            if haplotype[hap_pos] == '-':  # Deletion
                # Calculate deletion size
                del_size = 1
                next_pos = hap_pos + 1
                while next_pos < len(haplotype) and haplotype[next_pos] == '-':
                    del_size += 1
                    next_pos += 1
                
                if del_size <= self.max_indel_size:
                    in_bed = self._is_indel_in_bed(ref_name, pos + 1, del_size)
                    mutations.append({
                        'position': pos + 1,  # Convert to 1-based
                        'ref': ref_seq[pos:pos+del_size].upper(),
                        'alt': '-',
                        'type': 'deletion',
                        'size': del_size,
                        'in_bed': in_bed
                    })
                pos += del_size
                hap_pos += 1
            elif pos < len(ref_seq) and ref_seq[pos].upper() == '-':  # Insertion
                # Calculate insertion size
                ins_size = 1
                next_pos = pos + 1
                while next_pos < len(ref_seq) and ref_seq[next_pos].upper() == '-':
                    ins_size += 1
                    next_pos += 1
                
                if ins_size <= self.max_indel_size:
                    in_bed = self._is_indel_in_bed(ref_name, pos + 1, ins_size)
                    mutations.append({
                        'position': pos + 1,  # Convert to 1-based
                        'ref': '-',
                        'alt': haplotype[hap_pos:hap_pos+ins_size].upper(),
                        'type': 'insertion',
                        'size': ins_size,
                        'in_bed': in_bed
                    })
                hap_pos += ins_size
                pos += 1
            elif haplotype[hap_pos].islower():  # Substitution
                mutations.append({
                    'position': pos + 1,  # Convert to 1-based
                    'ref': ref_seq[pos].upper(),
                    'alt': haplotype[hap_pos].upper(),
                    'type': 'substitution'
                })
                pos += 1
                hap_pos += 1
            else:
                pos += 1
                hap_pos += 1
        
        return mutations

    def _downsample_fastq(self, 
                        input_fastq: Path, 
                        output_fastq: Path,
                        target_size: int) -> None:
        """Downsample a FASTQ file to approximately target size."""
        input_size = input_fastq.stat().st_size
        if input_size <= target_size:
            # If file is smaller than target, just create a symlink
            output_fastq.symlink_to(input_fastq)
            return
            
        # Calculate sampling fraction
        fraction = target_size / input_size
        
        logger.info(f"Downsampling {input_fastq.name} to {fraction:.2%} of original size")
        
        # Use seqtk to downsample
        try:
            seed = 100  # Fixed seed for reproducibility
            subprocess.run(
                [
                    'seqtk', 'sample',
                    '-s', str(seed),
                    str(input_fastq),
                    str(fraction)
                ],
                stdout=open(output_fastq, 'w'),
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Downsampling failed: {error_msg}")

    def process_sample(self, 
                      fastq_r1: Path,
                      fastq_r2: Path,
                      output_dir: Path,
                      threads: int = 4) -> pd.DataFrame:
        """Process a single sample's FASTQ files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            try:
                click.echo("Starting sample processing...")
                # Downsample FASTQ files if needed
                r1_size = fastq_r1.stat().st_size
                r2_size = fastq_r2.stat().st_size
                total_size = r1_size + r2_size
                
                if total_size > self.max_file_size:
                    click.echo(
                        f"Input files total size ({total_size:,} bytes) exceeds target size "
                        f"({self.max_file_size:,} bytes), downsampling..."
                    )
                    
                    # Calculate target size for each file proportionally
                    r1_target = int(self.max_file_size * (r1_size / total_size))
                    r2_target = int(self.max_file_size * (r2_size / total_size))
                    
                    # Create downsampled files
                    temp_r1 = temp_dir / "downsampled_R1.fastq"
                    temp_r2 = temp_dir / "downsampled_R2.fastq"
                    
                    with click.progressbar(length=2, label='Downsampling files') as bar:
                        self._downsample_fastq(fastq_r1, temp_r1, r1_target)
                        bar.update(1)
                        self._downsample_fastq(fastq_r2, temp_r2, r2_target)
                        bar.update(1)
                    
                    # Use downsampled files for processing
                    fastq_r1 = temp_r1
                    fastq_r2 = temp_r2
                
                click.echo("Aligning reads...")
                bam_path = self._align_reads(fastq_r1, fastq_r2, temp_dir, output_dir, threads)
                click.echo("Alignment complete. Processing references...")
                
                results = []
                ref_count = len(self.reference)
                with click.progressbar(self.reference.items(), 
                                     length=ref_count,
                                     label='Processing references') as refs:
                    for ref_name, _ in refs:
                        click.echo(f"\nProcessing reference: {ref_name}")
                        amplicon_reads = list(self._process_alignments(bam_path, ref_name))
                        if amplicon_reads:
                            click.echo(f"Found {len(amplicon_reads)} valid reads for {ref_name}")
                            results.extend(self._analyze_amplicons(amplicon_reads, ref_name))
                
                if not results:
                    click.echo("No results found for any reference sequences")
                    return pd.DataFrame(columns=['reference', 'haplotype', 'count', 'frequency', 
                                              'mutations', 'is_full_length'])
                
                df = pd.DataFrame(results)
                
                # Filter by minimum read count
                df = df[df['count'] >= self.min_read_count].copy()
                
                if df.empty:
                    click.echo(f"No haplotypes met minimum read count threshold ({self.min_read_count})")
                    return pd.DataFrame(columns=['reference', 'haplotype', 'count', 'frequency', 
                                              'mutations', 'is_full_length'])
                
                # Recalculate frequencies after filtering
                total_reads = df['count'].sum()
                df['frequency'] = (df['count'] / total_reads) * 100
                
                # Save results
                sample_name = fastq_r1.stem.replace("_R1_001.fastq", "")
                csv_path = output_dir / f"{sample_name}_haplotypes.csv"
                df.to_csv(csv_path, index=False)
                click.echo(f"Results saved to {csv_path}")
                
                return df
                
            except Exception as e:
                logger.error(f"Error processing sample: {str(e)}")
                return pd.DataFrame(columns=['reference', 'haplotype', 'count', 'frequency', 
                                          'mutations', 'is_full_length'])