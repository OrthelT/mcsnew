"""Visualization module for NC Medicaid Managed Care Savings Analysis."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from .analysis import (
    analyze_savings, 
    get_summary_by_sfy, 
    get_summary_by_region,
    get_summary_by_category,
    get_summary_by_rate_cell,
    generate_summary_text,
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
    
    print(f"\nAll visualizations saved to: {OUTPUT_DIR}")
    
    # Close all figures to free memory
    plt.close('all')


if __name__ == "__main__":
    generate_all_visualizations()

