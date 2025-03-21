from typing import Dict, List, Set, Tuple
import json
from pathlib import Path
import base64
from io import BytesIO, StringIO
import datetime
import logging
from collections import defaultdict
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import click

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from jinja2 import Template

# Configure plotting styles properly
sns.set_theme(style="whitegrid")  # This sets up seaborn's styling
plt.style.use('default')  # Use matplotlib's default style as a base

logger = logging.getLogger(__name__)

def get_mutations_from_haplotype(haplotype: str, reference_seq: str, count: int) -> List[dict]:
    """Extract mutations from a haplotype sequence."""
    mutations = []
    for pos, (ref, var) in enumerate(zip(reference_seq.upper(), haplotype)):
        if var.islower() or var == '-':  # Mutation or deletion
            mutations.append({
                'position': pos + 1,
                'reference_base': ref,
                'mutation': var.upper(),
                'count': count
            })
    return mutations

def fig_to_base64() -> str:
    """Convert matplotlib figure to base64 string."""
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def create_mutation_frequency_plot(results_df: pd.DataFrame, reference_seq: str) -> str:
    """Create an interactive mutation frequency plot using Plotly."""
    if results_df.empty:
        return ""
        
    # Process mutations from all haplotypes
    all_mutations = []
    total_reads = results_df['count'].sum()
    
    for _, row in results_df.iterrows():
        mutations = get_mutations_from_haplotype(row['haplotype'], reference_seq, row['count'])
        all_mutations.extend(mutations)
    
    # Aggregate mutation frequencies
    mutation_freq = defaultdict(int)
    for mut in all_mutations:
        key = f"{mut['position']} {mut['reference_base']}→{mut['mutation']}"
        mutation_freq[key] += mut['count']
    
    # Convert to percentages and sort by position
    positions = []
    frequencies = []
    labels = []
    
    for key, count in sorted(mutation_freq.items(), key=lambda x: int(x[0].split()[0])):
        positions.append(key)
        freq = (count / total_reads) * 100
        frequencies.append(freq)
        labels.append(f"{key}: {freq:.2f}%")
    
    # Create Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=positions,
        y=frequencies,
        marker_color='rgb(31, 119, 180)',
        hovertext=labels,
        name='Mutation Frequency'
    ))
    
    fig.update_layout(
        title='Mutation Frequencies',
        xaxis=dict(
            title='Position and Mutation',
            tickangle=45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title='Frequency (%)',
            range=[0, max(frequencies) * 1.1]
        ),
        margin=dict(b=100, l=60, r=20, t=40),
        width=max(800, len(positions) * 50),
        height=500,
        template='plotly_white'
    )
    
    # Convert to HTML
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': True}
    )
    
    return plot_html

def create_mutation_spectrum(results: Dict[str, pd.DataFrame], reference_seq: str) -> str:
    """Create mutation spectrum analysis."""
    mutation_types = defaultdict(int)
    total_mutations = 0
    double_mutations = defaultdict(int)
    
    # Normalize reference sequence once
    reference_seq = reference_seq.upper()
    
    for df in results.values():
        if df.empty:
            continue
            
        for _, row in df.iterrows():
            haplotype = row['haplotype']
            count = row['count']
            
            # Track positions with mutations for linked analysis
            mutation_positions = []
            
            for i, (ref, var) in enumerate(zip(reference_seq, haplotype)):
                if var.islower():  # This identifies a mutation
                    # Create mutation string with both bases in uppercase
                    mutation = f"{ref}>{var.upper()}"
                    # Only count if they're actually different after normalization
                    if ref != var.upper():
                        mutation_types[mutation] += count
                        total_mutations += count
                        mutation_positions.append((i + 1, ref, var.upper()))
            
            # Process linked mutations
            for i in range(len(mutation_positions)):
                for j in range(i + 1, len(mutation_positions)):
                    pos1, ref1, mut1 = mutation_positions[i]
                    pos2, ref2, mut2 = mutation_positions[j]
                    double_key = f"({pos1}{ref1}>{mut1}, {pos2}{ref2}>{mut2})"
                    double_mutations[double_key] += count
    
    if not mutation_types:
        return ""
        
    # Create single mutation spectrum
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    types = sorted(mutation_types.keys())
    counts = [mutation_types[t] for t in types]
    percentages = [100 * c / total_mutations for c in counts]
    
    sns.barplot(x=types, y=percentages)
    plt.title('Single Mutation Spectrum')
    plt.xlabel('Mutation Type')
    plt.ylabel('Percentage of Total Mutations')
    plt.xticks(rotation=45)
    
    # Create linked mutation spectrum (top 10 most frequent)
    plt.subplot(1, 2, 2)
    if double_mutations:
        sorted_doubles = sorted(double_mutations.items(), key=lambda x: x[1], reverse=True)[:10]
        double_types, double_counts = zip(*sorted_doubles)
        double_percentages = [100 * c / total_mutations for c in double_counts]
        
        sns.barplot(x=list(range(len(double_types))), y=double_percentages)
        plt.title('Top 10 Linked Mutations')
        plt.xlabel('Mutation Pair')
        plt.ylabel('Percentage of Total Mutations')
        plt.xticks(range(len(double_types)), double_types, rotation=45, ha='right')
    
    plt.tight_layout()
    return fig_to_base64()

def create_position_mutation_plot(results_df: pd.DataFrame, reference_seq: str) -> str:
    """Create a plot showing number of different mutations at each position."""
    if results_df.empty:
        return ""
    
    # Track unique mutations at each position
    position_mutations = defaultdict(set)
    
    # Process each haplotype
    for _, row in results_df.iterrows():
        haplotype = row['haplotype']
        for pos, (ref, var) in enumerate(zip(reference_seq.upper(), haplotype)):
            if var.islower():  # This is a mutation
                mutation = f"{ref}>{var.upper()}"
                position_mutations[pos + 1].add(mutation)  # 1-based position
    
    # Convert to plot data
    positions = sorted(position_mutations.keys())
    mutation_counts = [len(position_mutations[pos]) for pos in positions]
    
    # Create Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=positions,
        y=mutation_counts,
        marker_color='rgb(158,202,225)',
        hovertemplate="Position: %{x}<br>" +
                     "Different mutations: %{y}<br>" +
                     "Mutations: %{customdata}<extra></extra>",
        customdata=[list(position_mutations[pos]) for pos in positions]
    ))
    
    fig.update_layout(
        title='Mutation Diversity by Position',
        xaxis=dict(
            title='Position in Sequence',
            tickmode='linear'
        ),
        yaxis=dict(
            title='Number of Different Mutations',
            range=[0, max(mutation_counts) * 1.1]
        ),
        margin=dict(b=50, l=60, r=20, t=40),
        width=800,
        height=400,
        template='plotly_white'
    )
    
    # Convert to HTML
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': True}
    )
    
    return plot_html

def create_indel_summary(results_df: pd.DataFrame) -> pd.DataFrame:
    """Create a summary of indels found in the results.
    
    Args:
        results_df: DataFrame containing mutation results
        
    Returns:
        DataFrame with indel summary statistics
    """
    if results_df.empty:
        return pd.DataFrame()
        
    indel_data = []
    for _, row in results_df.iterrows():
        for mut in row.get('mutations', []):
            if mut['type'] in ['insertion', 'deletion']:
                indel_data.append({
                    'position': mut['position'],
                    'type': mut['type'],
                    'size': mut['size'],
                    'ref': mut['ref'],
                    'alt': mut['alt'],
                    'in_bed': mut['in_bed'],
                    'frequency': row['frequency'],
                    'count': row['count']
                })
    
    if not indel_data:
        return pd.DataFrame()
        
    indel_df = pd.DataFrame(indel_data)
    
    # Create summary table with rich formatting
    summary = []
    for (type_name, in_bed), group in indel_df.groupby(['type', 'in_bed']):
        summary.append({
            'Type': type_name.capitalize(),
            'In BED': 'Yes' if in_bed else 'No',
            'Count': len(group),
            'Avg Size': f"{group['size'].mean():.1f}",
            'Max Size': group['size'].max(),
            'Avg Frequency': f"{group['frequency'].mean():.2%}",
            'Positions': ', '.join(map(str, sorted(group['position'].unique())))
        })
    
    return pd.DataFrame(summary)

def create_indel_plot(results_df: pd.DataFrame) -> str:
    """Create an interactive plot showing indel distribution.
    
    Args:
        results_df: DataFrame containing mutation results
        
    Returns:
        HTML string of the plot
    """
    if results_df.empty:
        return ""
        
    indel_data = []
    for _, row in results_df.iterrows():
        for mut in row.get('mutations', []):
            if mut['type'] in ['insertion', 'deletion']:
                indel_data.append({
                    'position': mut['position'],
                    'type': mut['type'],
                    'size': mut['size'],
                    'in_bed': mut['in_bed'],
                    'frequency': row['frequency']
                })
    
    if not indel_data:
        return ""
        
    indel_df = pd.DataFrame(indel_data)
    
    # Create scatter plot
    fig = go.Figure()
    
    colors = {'insertion': 'blue', 'deletion': 'red'}
    symbols = {True: 'star', False: 'circle'}
    
    for type_name in ['insertion', 'deletion']:
        for in_bed in [True, False]:
            mask = (indel_df['type'] == type_name) & (indel_df['in_bed'] == in_bed)
            if mask.any():
                data = indel_df[mask]
                fig.add_trace(go.Scatter(
                    x=data['position'],
                    y=data['size'],
                    mode='markers',
                    name=f"{type_name.capitalize()} {'(in BED)' if in_bed else ''}",
                    marker=dict(
                        size=10,
                        symbol=symbols[in_bed],
                        color=colors[type_name],
                        line=dict(width=2, color='black') if in_bed else dict(width=0)
                    ),
                    text=[f"Size: {s}<br>Frequency: {f:.2%}" for s, f in zip(data['size'], data['frequency'])],
                    hoverinfo='text+x+y'
                ))
    
    fig.update_layout(
        title='Indel Distribution',
        xaxis_title='Position',
        yaxis_title='Indel Size',
        showlegend=True,
        height=500
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def format_summary_table(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Format complete summary table with all mutation statistics."""
    summary_data = []
    
    for sample, df in results.items():
        if df.empty:
            continue
            
        # Basic stats
        total_reads = df['count'].sum()
        unique_haplotypes = len(df)
        max_freq = (df['count'].max() / total_reads * 100) if total_reads > 0 else 0.0
        avg_mutations = (df['mutations'] * df['count']).sum() / total_reads if total_reads > 0 else 0.0
        
        # Full length statistics
        full_length_reads = df[df['is_full_length']]['count'].sum()
        full_length_percent = (full_length_reads / total_reads * 100) if total_reads > 0 else 0.0
        
        # Single mutation statistics
        single_mut_reads = df[df['mutations'] == 1]['count'].sum()
        single_mut_percent = (single_mut_reads / total_reads * 100) if total_reads > 0 else 0.0
        
        # Full length single mutations
        full_length_single = df[(df['mutations'] == 1) & (df['is_full_length'])]['count'].sum()
        full_length_single_percent = (full_length_single / total_reads * 100) if total_reads > 0 else 0.0
        
        summary_data.append({
            'sample': sample,
            'total_reads': total_reads,
            'unique_haplotypes': unique_haplotypes,
            'max_frequency': max_freq,
            'avg_mutations': avg_mutations,
            'full_length_reads': full_length_reads,
            'full_length_percent': full_length_percent,
            'single_mutations': single_mut_reads,
            'single_mutation_percent': single_mut_percent,
            'full_length_single_mutations': full_length_single,
            'full_length_single_percent': full_length_single_percent
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Format for display
    if not summary_df.empty:
        # Round percentages to 2 decimal places
        percentage_cols = ['max_frequency', 'full_length_percent', 
                         'single_mutation_percent', 'full_length_single_percent']
        summary_df[percentage_cols] = summary_df[percentage_cols].round(2)
        
        # Round avg_mutations to 2 decimal places
        summary_df['avg_mutations'] = summary_df['avg_mutations'].round(2)
    
    return summary_df


def generate_report(results: Dict[str, pd.DataFrame], 
                   summary: pd.DataFrame, 
                   output_path: Path,
                   reference_seq: str):
    """Generate HTML report with results.
    
    Args:
        results: Dictionary of results DataFrames
        summary: Summary DataFrame
        output_path: Path to save report
        reference_seq: Reference sequence
    """
    # Create plots
    with click.progressbar(length=5, label='Generating plots') as bar:
        mutation_freq_plot = create_mutation_frequency_plot(
            pd.concat(results.values()) if results else pd.DataFrame(), 
            reference_seq
        )
        bar.update(1)
        
        mutation_spectrum = create_mutation_spectrum(results, reference_seq)
        bar.update(1)
        
        position_plot = create_position_mutation_plot(
            pd.concat(results.values()) if results else pd.DataFrame(),
            reference_seq
        )
        bar.update(1)
        
        # Create indel-specific visualizations
        all_results = pd.concat(results.values()) if results else pd.DataFrame()
        indel_plot = create_indel_plot(all_results)
        bar.update(1)
        
        indel_summary = create_indel_summary(all_results)
        bar.update(1)
    
    # Format tables
    summary_table = summary.to_html(
        classes=['table', 'table-striped', 'table-hover'],
        index=False,
        float_format=lambda x: f'{x:.2f}' if isinstance(x, float) else str(x)
    )
    
    indel_table = indel_summary.to_html(
        classes=['table', 'table-striped', 'table-hover'],
        index=False
    ) if not indel_summary.empty else "No indels found"

    # Calculate additional statistics
    stats_data = {}
    for sample, df in results.items():
        if df.empty:
            continue
            
        mutation_rates = df.groupby('mutations')['count'].sum() / df['count'].sum() * 100
        stats_data[sample] = {
            'mutation_rates': mutation_rates.to_dict(),
            'total_reads': df['count'].sum(),
            'unique_haplotypes': len(df),
            'full_length_percent': (df[df['is_full_length']]['count'].sum() / df['count'].sum() * 100)
        }
    
    # Generate HTML
    template = Template(HTML_TEMPLATE)
    report_html = template.render(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        summary=summary_table,
        mutation_spectrum=mutation_spectrum,
        mutation_freq_plot=mutation_freq_plot,
        position_plot=position_plot,
        indel_plot=indel_plot,
        indel_summary=indel_table,
        stats=stats_data,
        has_data=bool(results and any(not df.empty for df in results.values()))
    )
    
    # Write report
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w') as f:
        f.write(report_html)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mutation Analysis Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .plot-container { margin-bottom: 30px; }
        .plot-description { 
            font-style: italic;
            color: #666;
            margin-top: 10px;
        }
        .stats-box {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .table-responsive {
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Mutation Analysis Report</h1>
        <p class="text-muted">Generated on {{ date }}</p>

        {% if has_data %}
            <!-- Summary Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>Summary</h2>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        {{ summary | safe }}
                    </div>
                </div>
            </div>

            <!-- Indel Analysis Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>Indel Analysis</h2>
                </div>
                <div class="card-body">
                    <h3>Indel Summary</h3>
                    <div class="table-responsive">
                        {{ indel_summary | safe }}
                    </div>
                    
                    {% if indel_plot %}
                    <h3 class="mt-4">Indel Distribution</h3>
                    <div class="plot-container">
                        {{ indel_plot | safe }}
                        <p class="plot-description">
                            Distribution of insertions and deletions across the sequence.
                            Stars indicate indels that overlap with regions in the provided BED file.
                            Hover over points to see detailed information.
                        </p>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- Mutation Analysis Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>Mutation Analysis</h2>
                </div>
                <div class="card-body">
                    <!-- Mutation Spectrum -->
                    {% if mutation_spectrum %}
                    <div class="plot-container">
                        {{ mutation_spectrum | safe }}
                        <p class="plot-description">
                            Distribution of mutation types across all samples.
                            Shows the frequency of different types of base changes.
                        </p>
                    </div>
                    {% endif %}
                    
                    <!-- Mutation Frequency Plot -->
                    {% if mutation_freq_plot %}
                    <div class="plot-container">
                        {{ mutation_freq_plot | safe }}
                        <p class="plot-description">
                            Distribution of individual mutation frequencies across the sequence.
                            Each point represents a unique mutation and its frequency.
                        </p>
                    </div>
                    {% endif %}
                    
                    <!-- Position Mutation Plot -->
                    {% if position_plot %}
                    <div class="plot-container">
                        {{ position_plot | safe }}
                        <p class="plot-description">
                            Number of different mutations observed at each position.
                            Hover over bars to see the specific mutations at each position.
                        </p>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- Statistics Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>Statistics</h2>
                </div>
                <div class="card-body">
                    {% for sample, stat in stats.items() %}
                    <div class="stats-box">
                        <h3>{{ sample }}</h3>
                        <ul class="list-unstyled">
                            <li><strong>Total Reads:</strong> {{ "{:,}".format(stat.total_reads) }}</li>
                            <li><strong>Unique Haplotypes:</strong> {{ "{:,}".format(stat.unique_haplotypes) }}</li>
                            <li><strong>Full Length Reads:</strong> {{ "{:.2f}%".format(stat.full_length_percent) }}</li>
                        </ul>
                        <h4>Mutation Rates:</h4>
                        <ul class="list-unstyled">
                        {% for mutations, rate in stat.mutation_rates.items() %}
                            <li>{{ mutations }} mutations: {{ "{:.2f}%".format(rate) }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endfor %}
                </div>
            </div>
        {% else %}
            <div class="alert alert-warning">
                No mutation data available for analysis.
            </div>
        {% endif %}
    </div>
</body>
</html>
"""