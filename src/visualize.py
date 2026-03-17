"""Visualization module for NC Medicaid Managed Care Savings Analysis."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

from .analysis import (
    analyze_savings,
    get_summary_by_sfy,
    get_summary_by_region,
    get_summary_by_category,
    get_summary_by_rate_cell,
    generate_summary_text,
    analyze_contributions,
    get_contribution_summary_by_sfy,
    get_contribution_summary_by_region,
    get_contribution_summary_by_category,
    generate_contribution_summary_text,
)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Custom color palette - professional blue/green scheme
COLORS = {
    'primary': '#1e3a5f',      # Dark navy blue
    'secondary': '#3d7ea6',    # Medium blue
    'accent': '#5fb49c',       # Teal green
    'highlight': '#f39c12',    # Gold/orange for emphasis
    'light': '#89c4f4',        # Light blue
    'neutral': '#95a5a6',      # Gray
}

SFY_COLORS = {
    2022: '#0d1f2d',  # Darkest navy
    2023: '#1e3a5f',  # Dark navy
    2024: '#3d7ea6',  # Medium blue
    2025: '#5fb49c',  # Teal green
    2026: '#89c4f4',  # Light blue
}


def format_currency(x, pos=None):
    """Format currency values in millions."""
    if x >= 1e9:
        return f'${x/1e9:.1f}B'
    elif x >= 1e6:
        return f'${x/1e6:.1f}M'
    elif x >= 1e3:
        return f'${x/1e3:.0f}K'
    else:
        return f'${x:.0f}'


def create_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_savings_by_year(save: bool = True) -> plt.Figure:
    """Create bar chart of total savings by fiscal year."""
    df = get_summary_by_sfy()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = df['SFY'].astype(int).tolist()
    savings = df['Total Savings'].tolist()
    colors = [SFY_COLORS.get(y, COLORS['primary']) for y in years]
    
    bars = ax.bar(years, savings, color=colors, edgecolor='white', linewidth=1.5)
    
    # Add value labels on bars
    for bar, val in zip(bars, savings):
        height = bar.get_height()
        ax.annotate(f'${val/1e6:.1f}M',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
    
    ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Savings ($)', fontsize=12, fontweight='bold')
    ax.set_title('NC Medicaid Managed Care Savings by Fiscal Year', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.set_xticks(years)
    ax.set_xticklabels([f'SFY {y}' for y in years])
    
    # Add subtle grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'savings_by_year.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def plot_savings_by_region(sfy: int = 2026, save: bool = True) -> plt.Figure:
    """Create horizontal bar chart of savings by region."""
    df = get_summary_by_region(sfy)
    df = df.sort_values('Total Savings', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    regions = df['Region'].tolist()
    savings = df['Total Savings'].tolist()
    
    # Create gradient colors
    colors = plt.cm.Blues(0.4 + 0.6 * (df['Total Savings'] / df['Total Savings'].max()))
    
    bars = ax.barh(regions, savings, color=colors, edgecolor='white', linewidth=1)
    
    # Add value labels
    for bar, val in zip(bars, savings):
        width = bar.get_width()
        ax.annotate(f'${val/1e6:.1f}M',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center',
                    fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Total Savings ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Region', fontsize=12, fontweight='bold')
    ax.set_title(f'NC Medicaid Managed Care Savings by Region (SFY {sfy})', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'savings_by_region.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def plot_savings_by_category(sfy: int = 2026, top_n: int = 10, save: bool = True) -> plt.Figure:
    """Create horizontal bar chart of top savings categories."""
    df = get_summary_by_category(sfy)
    
    # Filter out near-zero values and get top N
    df = df[df['Total Savings'] > 1000]  # Filter out essentially zero values
    df = df.head(top_n)
    df = df.sort_values('Total Savings', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    categories = df['Category'].tolist()
    savings = df['Total Savings'].tolist()
    
    # Create gradient colors
    colors = plt.cm.Greens(0.4 + 0.6 * (df['Total Savings'] / df['Total Savings'].max()))
    
    bars = ax.barh(categories, savings, color=colors, edgecolor='white', linewidth=1)
    
    # Add value labels
    for bar, val in zip(bars, savings):
        width = bar.get_width()
        ax.annotate(f'${val/1e6:.1f}M',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center',
                    fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Total Savings ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Category of Service', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Managed Care Savings by Category (SFY {sfy})', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'savings_by_category.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def plot_savings_trend(save: bool = True) -> plt.Figure:
    """Create line chart showing savings trend over fiscal years."""
    df = get_summary_by_sfy()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = df['SFY'].astype(int).tolist()
    savings = df['Total Savings'].tolist()
    
    # Plot line
    ax.plot(years, savings, marker='o', markersize=12, linewidth=3, 
            color=COLORS['primary'], markerfacecolor=COLORS['accent'],
            markeredgecolor='white', markeredgewidth=2)
    
    # Fill area under curve
    ax.fill_between(years, savings, alpha=0.2, color=COLORS['primary'])
    
    # Add value labels
    for x, y in zip(years, savings):
        ax.annotate(f'${y/1e6:.1f}M',
                    xy=(x, y),
                    xytext=(0, 15),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
    
    ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Savings ($)', fontsize=12, fontweight='bold')
    ax.set_title('NC Medicaid Managed Care Savings Trend', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.set_xticks(years)
    ax.set_xticklabels([f'SFY {y}' for y in years])
    
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Set y-axis to start from 0
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'savings_trend.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def plot_regional_comparison_by_year(save: bool = True) -> plt.Figure:
    """Create grouped bar chart comparing regional savings across years."""
    # Get data for all years
    all_data = []
    sfy_list = [2022, 2023, 2024, 2025, 2026]
    for sfy in sfy_list:
        df = get_summary_by_region(sfy)
        if len(df) > 0:
            df['SFY'] = sfy
            all_data.append(df)
    
    combined = pd.concat(all_data, ignore_index=True)
    
    # Get unique SFYs that have data
    available_sfys = sorted(combined['SFY'].unique())
    
    # Pivot for grouped bar chart
    pivot = combined.pivot(index='Region', columns='SFY', values='Total Savings')
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = range(len(pivot.index))
    width = 0.15  # Narrower bars for 5 years
    
    for i, sfy in enumerate(available_sfys):
        offset = (i - len(available_sfys) / 2 + 0.5) * width
        bars = ax.bar([xi + offset for xi in x], pivot[sfy], width, 
                      label=f'SFY {sfy}', color=SFY_COLORS.get(sfy, COLORS['primary']),
                      edgecolor='white', linewidth=1)
    
    ax.set_xlabel('Region', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Savings ($)', fontsize=12, fontweight='bold')
    ax.set_title('Managed Care Savings by Region Across Fiscal Years', 
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.legend(title='Fiscal Year', loc='upper right')
    
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'regional_comparison.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def create_summary_dashboard(save: bool = True) -> plt.Figure:
    """Create a summary dashboard with key metrics."""
    fig = plt.figure(figsize=(16, 12))
    
    # Create grid for subplots
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Total savings by year (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    df_year = get_summary_by_sfy()
    years = df_year['SFY'].astype(int).tolist()
    savings = df_year['Total Savings'].tolist()
    colors = [SFY_COLORS.get(y, COLORS['primary']) for y in years]
    bars = ax1.bar(years, savings, color=colors, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, savings):
        ax1.annotate(f'${val/1e6:.1f}M',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax1.set_title('Total Savings by Fiscal Year', fontsize=12, fontweight='bold')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax1.set_xticks(years)
    ax1.set_xticklabels([f'SFY {y}' for y in years])
    ax1.yaxis.grid(True, linestyle='--', alpha=0.5)
    
    # Savings by region for latest year (top right)
    ax2 = fig.add_subplot(gs[0, 1])
    df_region = get_summary_by_region(2026).sort_values('Total Savings', ascending=True)
    colors2 = plt.cm.Blues(0.4 + 0.6 * (df_region['Total Savings'] / df_region['Total Savings'].max()))
    ax2.barh(df_region['Region'], df_region['Total Savings'], color=colors2, edgecolor='white')
    ax2.set_title('Savings by Region (SFY 2026)', fontsize=12, fontweight='bold')
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax2.xaxis.grid(True, linestyle='--', alpha=0.5)
    
    # Top categories (bottom left)
    ax3 = fig.add_subplot(gs[1, 0])
    df_cat = get_summary_by_category(2026)
    df_cat = df_cat[df_cat['Total Savings'] > 1000].head(5).sort_values('Total Savings', ascending=True)
    colors3 = plt.cm.Greens(0.4 + 0.6 * (df_cat['Total Savings'] / df_cat['Total Savings'].max()))
    ax3.barh(df_cat['Category'], df_cat['Total Savings'], color=colors3, edgecolor='white')
    ax3.set_title('Top 5 Savings Categories (SFY 2026)', fontsize=12, fontweight='bold')
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax3.xaxis.grid(True, linestyle='--', alpha=0.5)
    
    # Trend over time (bottom right)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(years, savings, marker='o', markersize=10, linewidth=2.5,
             color=COLORS['primary'], markerfacecolor=COLORS['accent'],
             markeredgecolor='white', markeredgewidth=2)
    ax4.fill_between(years, savings, alpha=0.2, color=COLORS['primary'])
    ax4.set_title('Savings Trend Over Time', fontsize=12, fontweight='bold')
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax4.set_xticks(years)
    ax4.set_xticklabels([f'SFY {y}' for y in years])
    ax4.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax4.set_ylim(bottom=0)
    
    # Add overall title
    fig.suptitle('NC Medicaid Managed Care Savings Dashboard', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'savings_dashboard.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    return fig


def save_summary_text():
    """Save the text summary to a file."""
    create_output_dir()
    summary = generate_summary_text()
    
    output_path = OUTPUT_DIR / 'savings_summary.txt'
    with open(output_path, 'w') as f:
        f.write(summary)
    
    print(f"Summary saved to {output_path}")


def generate_all_visualizations():
    """Generate all visualizations and save to output directory."""
    create_output_dir()
    
    print("Generating visualizations...")
    
    # Generate each plot
    print("  - Savings by year...")
    plot_savings_by_year()
    
    print("  - Savings by region...")
    plot_savings_by_region()
    
    print("  - Savings by category...")
    plot_savings_by_category()
    
    print("  - Savings trend...")
    plot_savings_trend()
    
    print("  - Regional comparison...")
    plot_regional_comparison_by_year()
    
    print("  - Summary dashboard...")
    create_summary_dashboard()
    
    print("  - Summary text...")
    save_summary_text()

    # NEW: Cost factor contribution plots
    print("\nGenerating cost factor contribution analysis...")

    print("  - Factor contributions by year...")
    plot_factor_contributions_by_year()

    print("  - Percentage contributions by year...")
    plot_percentage_contributions_by_year()

    print("  - Factor waterfall (SFY 2026)...")
    plot_factor_waterfall(2026)

    print("  - Regional factor contributions (SFY 2026)...")
    plot_regional_factor_contributions(2026)

    print("  - Trend percentage change year-over-year...")
    plot_trend_percentage_change_yoy()

    print("  - Contribution dashboard...")
    create_contribution_dashboard()

    print("  - Contribution summary text...")
    save_contribution_summary_text()

    print(f"\nAll visualizations saved to: {OUTPUT_DIR}")

    # Close all figures to free memory
    plt.close('all')


def plot_factor_contributions_by_year(save: bool = True) -> plt.Figure:
    """
    Create stacked bar chart showing contribution of Trend, PC, and MCS by fiscal year.

    Bars show the dollar impact of each factor, with positive values stacked upward
    and negative values (MCS) shown separately to illustrate cost offsets.
    """
    df = get_contribution_summary_by_sfy()

    fig, ax = plt.subplots(figsize=(14, 8))

    years = df['SFY'].astype(int).tolist()
    trend_impact = df['Trend Impact ($)'].tolist()
    pc_impact = df['PC Impact ($)'].tolist()
    mcs_impact = df['MCS Impact ($)'].tolist()

    # Colors for each factor
    color_trend = '#e74c3c'      # Red - cost increase
    color_pc = '#f39c12'          # Orange - cost increase/decrease
    color_mcs = '#27ae60'         # Green - cost savings

    x = np.arange(len(years))
    width = 0.6

    # Stack positive contributors (Trend, PC if positive)
    bars_trend = ax.bar(x, trend_impact, width, label='Cost Trend',
                        color=color_trend, edgecolor='white', linewidth=2)

    # PC stacked on trend
    bars_pc = ax.bar(x, pc_impact, width, bottom=trend_impact,
                     label='Program Changes', color=color_pc,
                     edgecolor='white', linewidth=2)

    # MCS shown separately (negative values)
    bars_mcs = ax.bar(x, mcs_impact, width, label='Managed Care Savings',
                      color=color_mcs, edgecolor='white', linewidth=2)

    # Add net change line
    net_change = df['Net Change ($)'].tolist()
    ax.plot(x, net_change, marker='D', markersize=10, linewidth=2.5,
            color='#2c3e50', markerfacecolor='white', markeredgewidth=2,
            label='Net Change', zorder=10)

    # Value labels on each segment
    for i, (trend, pc, mcs, net) in enumerate(zip(trend_impact, pc_impact, mcs_impact, net_change)):
        # Trend label
        ax.text(i, trend/2, f'${trend/1e6:.0f}M', ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

        # PC label
        if abs(pc) > 1e6:  # Only label if significant
            ax.text(i, trend + pc/2, f'${pc/1e6:.0f}M', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')

        # MCS label
        ax.text(i, mcs/2, f'${mcs/1e6:.0f}M', ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

        # Net change label (position above the point)
        label_y = net + (max(net_change) - min(net_change)) * 0.02  # Offset by 2% of range
        ax.text(i, label_y, f'${net/1e6:.0f}M', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color='#2c3e50')

    # Formatting
    ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dollar Impact ($)', fontsize=12, fontweight='bold')
    ax.set_title('Cost Factor Contributions to NC Medicaid Capitation Rates\n' +
                 'Trend vs. Program Changes vs. Managed Care Savings',
                 fontsize=14, fontweight='bold', pad=20)

    ax.set_xticks(x)
    ax.set_xticklabels([f'SFY {y}' for y in years])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))

    # Add horizontal line at y=0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.3)

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95)

    plt.tight_layout()

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'factor_contributions_by_year.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


def plot_percentage_contributions_by_year(save: bool = True) -> plt.Figure:
    """
    Create 100% stacked bar chart showing relative percentage contribution
    of each factor by fiscal year.
    """
    df = get_contribution_summary_by_sfy()

    fig, ax = plt.subplots(figsize=(12, 7))

    years = df['SFY'].astype(int).tolist()
    trend_pct = df['Trend %'].tolist()
    pc_pct = df['PC %'].tolist()
    mcs_pct = df['MCS %'].tolist()

    # Colors
    color_trend = '#e74c3c'
    color_pc = '#f39c12'
    color_mcs = '#27ae60'

    x = np.arange(len(years))
    width = 0.6

    # Stacked bars (100% total)
    bars_trend = ax.bar(x, trend_pct, width, label='Cost Trend',
                        color=color_trend, edgecolor='white', linewidth=2)
    bars_pc = ax.bar(x, pc_pct, width, bottom=trend_pct,
                     label='Program Changes', color=color_pc,
                     edgecolor='white', linewidth=2)
    bars_mcs = ax.bar(x, mcs_pct, width, bottom=[t+p for t,p in zip(trend_pct, pc_pct)],
                      label='Managed Care Savings', color=color_mcs,
                      edgecolor='white', linewidth=2)

    # Percentage labels
    for i, (t, p, m) in enumerate(zip(trend_pct, pc_pct, mcs_pct)):
        # Trend
        ax.text(i, t/2, f'{t:.1f}%', ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')

        # PC (only if significant)
        if p > 5:
            ax.text(i, t + p/2, f'{p:.1f}%', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='white')

        # MCS
        ax.text(i, t + p + m/2, f'{m:.1f}%', ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')

    # Formatting
    ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage Contribution (%)', fontsize=12, fontweight='bold')
    ax.set_title('Relative Contribution of Cost Factors to Capitation Rate Changes\n' +
                 '(Percentage of Total Absolute Impact)',
                 fontsize=14, fontweight='bold', pad=20)

    ax.set_xticks(x)
    ax.set_xticklabels([f'SFY {y}' for y in years])
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='upper right', fontsize=11, framealpha=0.95)

    plt.tight_layout()

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'percentage_contributions_by_year.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


def plot_factor_waterfall(sfy: int = 2026, save: bool = True) -> plt.Figure:
    """
    Create waterfall chart showing how factors build from base PMPM to final PMPM
    for a specific fiscal year.
    """
    df = get_contribution_summary_by_sfy()
    df_year = df[df['SFY'] == sfy]

    if len(df_year) == 0:
        raise ValueError(f"No data for SFY {sfy}")

    row = df_year.iloc[0]

    # Calculate average PMPMs
    base_pmpm = row['Avg Base PMPM']
    trend_impact_pmpm = row['Trend Impact ($)'] / row['Member Months']
    pc_impact_pmpm = row['PC Impact ($)'] / row['Member Months']
    mcs_impact_pmpm = row['MCS Impact ($)'] / row['Member Months']
    final_pmpm = row['Avg Final PMPM']

    # Waterfall data
    categories = ['Base\nPMPM', 'Cost\nTrend', 'Program\nChanges', 'Managed\nCare\nSavings', 'Final\nPMPM']
    values = [base_pmpm, trend_impact_pmpm, pc_impact_pmpm, mcs_impact_pmpm, final_pmpm]

    # Calculate bar positions for waterfall effect
    cumulative = [base_pmpm,
                  base_pmpm + trend_impact_pmpm,
                  base_pmpm + trend_impact_pmpm + pc_impact_pmpm,
                  base_pmpm + trend_impact_pmpm + pc_impact_pmpm + mcs_impact_pmpm,
                  final_pmpm]

    fig, ax = plt.subplots(figsize=(12, 7))

    x = np.arange(len(categories))

    # Colors
    color_base = '#34495e'
    color_increase = '#e74c3c'
    color_decrease = '#27ae60'
    color_final = '#2c3e50'

    # Base bar
    ax.bar(0, base_pmpm, color=color_base, edgecolor='white', linewidth=2, width=0.6)
    ax.text(0, base_pmpm/2, f'${base_pmpm:.2f}', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

    # Trend (increase)
    bottom_trend = base_pmpm
    ax.bar(1, trend_impact_pmpm, bottom=bottom_trend,
           color=color_increase, edgecolor='white', linewidth=2, width=0.6)
    ax.text(1, bottom_trend + trend_impact_pmpm/2, f'+${trend_impact_pmpm:.2f}',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # PC (could be positive or negative)
    bottom_pc = cumulative[1]
    pc_color = color_increase if pc_impact_pmpm > 0 else color_decrease
    ax.bar(2, pc_impact_pmpm, bottom=bottom_pc,
           color=pc_color, edgecolor='white', linewidth=2, width=0.6)
    sign = '+' if pc_impact_pmpm > 0 else ''
    ax.text(2, bottom_pc + pc_impact_pmpm/2, f'{sign}${pc_impact_pmpm:.2f}',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # MCS (typically negative/savings)
    bottom_mcs = cumulative[2]
    ax.bar(3, mcs_impact_pmpm, bottom=bottom_mcs,
           color=color_decrease, edgecolor='white', linewidth=2, width=0.6)
    ax.text(3, bottom_mcs + mcs_impact_pmpm/2, f'${mcs_impact_pmpm:.2f}',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Final
    ax.bar(4, final_pmpm, color=color_final, edgecolor='white', linewidth=2, width=0.6)
    ax.text(4, final_pmpm/2, f'${final_pmpm:.2f}', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')

    # Connecting lines
    for i in range(len(x)-1):
        ax.plot([i+0.3, i+0.7], [cumulative[i], cumulative[i+1]],
                'k--', linewidth=1, alpha=0.5)

    # Formatting
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel('PMPM ($)', fontsize=12, fontweight='bold')
    ax.set_title(f'Waterfall Analysis: Base to Final PMPM (SFY {sfy})\n' +
                 'Sequential Impact of Cost Factors',
                 fontsize=14, fontweight='bold', pad=20)

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.2f'))
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Set y-axis to start from 0 or slightly below minimum
    y_min = min(0, min(cumulative) * 0.95)
    y_max = max(cumulative) * 1.05
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / f'factor_waterfall_sfy{sfy}.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


def plot_regional_factor_contributions(sfy: int = 2026, save: bool = True) -> plt.Figure:
    """
    Create grouped bar chart comparing factor contributions across regions
    for a specific fiscal year.
    """
    df = get_contribution_summary_by_region(sfy)
    df = df.sort_values('Net Change ($)', ascending=True)

    fig, ax = plt.subplots(figsize=(14, 8))

    regions = df['Region'].tolist()
    trend_impact = df['Trend Impact ($)'].tolist()
    pc_impact = df['PC Impact ($)'].tolist()
    mcs_impact = df['MCS Impact ($)'].tolist()

    # Colors
    color_trend = '#e74c3c'
    color_pc = '#f39c12'
    color_mcs = '#27ae60'

    y = np.arange(len(regions))
    height = 0.25

    # Horizontal grouped bars
    bars_trend = ax.barh(y - height, trend_impact, height,
                         label='Cost Trend', color=color_trend,
                         edgecolor='white', linewidth=1)
    bars_pc = ax.barh(y, pc_impact, height,
                      label='Program Changes', color=color_pc,
                      edgecolor='white', linewidth=1)
    bars_mcs = ax.barh(y + height, mcs_impact, height,
                       label='Managed Care Savings', color=color_mcs,
                       edgecolor='white', linewidth=1)

    # Value labels (positioned to the right of bars)
    max_val = max(max(trend_impact), max(pc_impact), abs(min(mcs_impact)))
    label_offset = max_val * 0.02  # 2% offset
    for i, (t, p, m) in enumerate(zip(trend_impact, pc_impact, mcs_impact)):
        ax.text(t + label_offset, i - height, f'${t/1e6:.1f}M', va='center', ha='left', fontsize=9)
        ax.text(p + label_offset, i, f'${p/1e6:.1f}M', va='center', ha='left', fontsize=9)
        ax.text(m + label_offset, i + height, f'${m/1e6:.1f}M', va='center', ha='left', fontsize=9)

    # Formatting
    ax.set_yticks(y)
    ax.set_yticklabels(regions)
    ax.set_xlabel('Dollar Impact ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Region', fontsize=12, fontweight='bold')
    ax.set_title(f'Cost Factor Contributions by Region (SFY {sfy})',
                 fontsize=14, fontweight='bold', pad=20)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Vertical line at x=0
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.3)

    # Legend
    ax.legend(loc='lower right', fontsize=10, framealpha=0.95)

    plt.tight_layout()

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / f'regional_factor_contributions_sfy{sfy}.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


def create_contribution_dashboard(save: bool = True) -> plt.Figure:
    """Create comprehensive dashboard for cost factor contribution analysis."""
    fig = plt.figure(figsize=(18, 12))

    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

    # Get data
    df_sfy = get_contribution_summary_by_sfy()
    df_region = get_contribution_summary_by_region(2026)

    # 1. Stacked bar: Dollar contributions by year (top, spanning 2 cols)
    ax1 = fig.add_subplot(gs[0, :])
    years = df_sfy['SFY'].astype(int).tolist()
    trend = df_sfy['Trend Impact ($)'].tolist()
    pc = df_sfy['PC Impact ($)'].tolist()
    mcs = df_sfy['MCS Impact ($)'].tolist()

    x = np.arange(len(years))
    width = 0.6
    ax1.bar(x, trend, width, label='Cost Trend', color='#e74c3c', edgecolor='white')
    ax1.bar(x, pc, width, bottom=trend, label='Program Changes',
            color='#f39c12', edgecolor='white')
    ax1.bar(x, mcs, width, label='MCS', color='#27ae60', edgecolor='white')

    ax1.set_xticks(x)
    ax1.set_xticklabels([f'SFY {y}' for y in years])
    ax1.set_title('Cost Factor Dollar Contributions by Fiscal Year',
                  fontsize=13, fontweight='bold')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    # 2. Percentage contributions (middle left)
    ax2 = fig.add_subplot(gs[1, 0])
    trend_pct = df_sfy['Trend %'].tolist()
    pc_pct = df_sfy['PC %'].tolist()
    mcs_pct = df_sfy['MCS %'].tolist()

    ax2.bar(x, trend_pct, width, color='#e74c3c', edgecolor='white')
    ax2.bar(x, pc_pct, width, bottom=trend_pct, color='#f39c12', edgecolor='white')
    ax2.bar(x, mcs_pct, width, bottom=[t+p for t,p in zip(trend_pct, pc_pct)],
            color='#27ae60', edgecolor='white')

    ax2.set_xticks(x)
    ax2.set_xticklabels([f'SFY {y}' for y in years])
    ax2.set_title('Percentage Contributions', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', alpha=0.3)

    # 3. Regional breakdown (middle right)
    ax3 = fig.add_subplot(gs[1, 1])
    regions_sorted = df_region.sort_values('Net Change ($)')
    regions = regions_sorted['Region'].tolist()
    net_change = regions_sorted['Net Change ($)'].tolist()

    colors3 = ['#27ae60' if x < 0 else '#e74c3c' for x in net_change]
    ax3.barh(regions, net_change, color=colors3, edgecolor='white')
    ax3.set_title('Net Cost Change by Region (SFY 2026)', fontsize=12, fontweight='bold')
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax3.grid(axis='x', alpha=0.3)
    ax3.axvline(x=0, color='black', linewidth=1, alpha=0.5)

    # 4. Trend over time - all factors (bottom left)
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(years, trend, marker='o', label='Trend', color='#e74c3c', linewidth=2)
    ax4.plot(years, pc, marker='s', label='PC', color='#f39c12', linewidth=2)
    ax4.plot(years, mcs, marker='^', label='MCS', color='#27ae60', linewidth=2)

    ax4.set_xticks(years)
    ax4.set_xticklabels([f'SFY {y}' for y in years])
    ax4.set_title('Factor Impact Trends', fontsize=12, fontweight='bold')
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax4.legend(fontsize=9)
    ax4.grid(alpha=0.3)
    ax4.axhline(y=0, color='black', linewidth=1, alpha=0.5)

    # 5. Summary statistics table (bottom right)
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')

    total_trend = df_sfy['Trend Impact ($)'].sum()
    total_pc = df_sfy['PC Impact ($)'].sum()
    total_mcs = df_sfy['MCS Impact ($)'].sum()
    total_net = df_sfy['Net Change ($)'].sum()

    table_data = [
        ['Factor', 'Total Impact'],
        ['Cost Trend', f'${total_trend/1e6:.1f}M'],
        ['Program Changes', f'${total_pc/1e6:.1f}M'],
        ['Managed Care Savings', f'${total_mcs/1e6:.1f}M'],
        ['───────────────', '─────────────'],
        ['Net Change', f'${total_net/1e6:.1f}M'],
    ]

    table = ax5.table(cellText=table_data, cellLoc='left',
                      bbox=[0.1, 0.2, 0.8, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)

    # Style header row
    for i in range(2):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')

    ax5.set_title('Total Impact Summary (SFY 2022-2026)',
                  fontsize=12, fontweight='bold', pad=10)

    # Overall title
    fig.suptitle('NC Medicaid Cost Factor Contribution Dashboard\n' +
                 'Trend vs. Program Changes vs. Managed Care Savings',
                 fontsize=16, fontweight='bold', y=0.98)

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'contribution_dashboard.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


def save_contribution_summary_text():
    """Save the contribution analysis summary to a file."""
    create_output_dir()
    summary = generate_contribution_summary_text()

    output_path = OUTPUT_DIR / 'contribution_summary.txt'
    with open(output_path, 'w') as f:
        f.write(summary)

    print(f"Contribution summary saved to {output_path}")


def plot_trend_percentage_change_yoy(save: bool = True) -> plt.Figure:
    """
    Create chart showing annual (year-over-year) percentage change in PMPM resulting from trend.

    This calculates the true annual trend increase:
    - Prior Year PMPM = Base × (1 + Trend)^((trend_months - 12)/12)
    - Current Year PMPM = Base × (1 + Trend)^(trend_months/12)
    - YoY % = (Current - Prior) / Prior × 100
    """
    # Get contribution data which includes base_pmpm, trend_factor, and sfy info
    df = analyze_contributions()

    # Calculate YoY percentage change by SFY
    summary_data = []

    for sfy in sorted(df['sfy_id'].unique()):
        sfy_data = df[df['sfy_id'] == sfy]

        # Determine trend months based on SFY
        trend_months = 42 if sfy in [2022, 2023] else 24

        # Calculate weighted average trend factor and base PMPM
        total_mm = sfy_data['member_months'].sum()
        avg_trend_factor = (sfy_data['trend_factor'] * sfy_data['member_months']).sum() / total_mm
        avg_base_pmpm = (sfy_data['base_pmpm'] * sfy_data['member_months']).sum() / total_mm

        # Calculate prior year and current year PMPMs
        prior_year_pmpm = avg_base_pmpm * ((1 + avg_trend_factor) ** ((trend_months - 12) / 12))
        current_year_pmpm = avg_base_pmpm * ((1 + avg_trend_factor) ** (trend_months / 12))

        # Calculate YoY percentage change
        yoy_pct_change = ((current_year_pmpm - prior_year_pmpm) / prior_year_pmpm) * 100

        summary_data.append({
            'sfy_id': sfy,
            'trend_factor': avg_trend_factor,
            'yoy_pct_change': yoy_pct_change,
            'trend_months': trend_months,
            'avg_base_pmpm': avg_base_pmpm,
            'prior_year_pmpm': prior_year_pmpm,
            'current_year_pmpm': current_year_pmpm,
        })

    summary = pd.DataFrame(summary_data)

    fig, ax = plt.subplots(figsize=(12, 7))

    years = summary['sfy_id'].astype(int).tolist()
    pct_change = summary['yoy_pct_change'].tolist()

    # Create colors based on SFY
    colors = [SFY_COLORS.get(y, COLORS['primary']) for y in years]

    # Bar chart
    bars = ax.bar(years, pct_change, color=colors, edgecolor='white', linewidth=2, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, pct_change):
        height = bar.get_height()
        ax.annotate(f'{val:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')

    # Add line overlay to show trend
    ax.plot(years, pct_change, marker='o', markersize=10, linewidth=2.5,
            color='#2c3e50', markerfacecolor='white', markeredgewidth=2,
            linestyle='--', alpha=0.7)

    ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Annual PMPM Percentage Increase (%)', fontsize=12, fontweight='bold')
    ax.set_title('Annual Year-over-Year Percentage Change in PMPM from Cost Trend\n' +
                 '(Medical Inflation Rate)',
                 fontsize=14, fontweight='bold', pad=20)

    ax.set_xticks(years)
    ax.set_xticklabels([f'SFY {y}' for y in years])

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())

    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.3)

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis to start from 0
    ax.set_ylim(bottom=0, top=max(pct_change) * 1.15)

    # Add text annotation explaining the calculation
    textstr = 'Annual % = (Current Year PMPM - Prior Year PMPM) / Prior Year PMPM × 100\nwhere Current/Prior Year PMPMs calculated using 12-month trend increments'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
            fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()

    if save:
        create_output_dir()
        fig.savefig(OUTPUT_DIR / 'trend_percentage_change_yoy.png',
                    dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig


if __name__ == "__main__":
    generate_all_visualizations()

