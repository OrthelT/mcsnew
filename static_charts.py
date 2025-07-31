import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from millify import millify

# Set style
plt.style.use('default')
sns.set_palette("viridis")

def load_data():
    """Load and prepare data for visualizations"""
    df = pd.read_csv('mcs_saving2.csv')
    df['savings_display'] = -df['savings']  # Convert to positive values
    df['savings_millions'] = df['savings_display'] / 1_000_000
    df['cost_millions'] = df['cost'] / 1_000_000
    return df

def create_executive_summary_chart():
    """Create a compelling executive summary visualization"""
    df = load_data()
    
    # Calculate key metrics
    total_savings = df['savings_display'].sum()
    total_cost = df['cost'].sum()
    savings_rate = (total_savings / total_cost) * 100
    total_members = df['MM'].sum() / 12
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('North Carolina Medicaid Managed Care Program Impact\nSFY 2026 Projections', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # 1. Total Savings Highlight
    ax1.text(0.5, 0.6, f'${total_savings:,.0f}', ha='center', va='center', 
             fontsize=32, fontweight='bold', color='navy')
    ax1.text(0.5, 0.4, 'Total Annual Savings', ha='center', va='center', 
             fontsize=16, fontweight='bold')
    ax1.text(0.5, 0.25, f'({savings_rate:.2f}% of total program cost)', ha='center', va='center', 
             fontsize=12, style='italic')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=False, linewidth=3, color='navy'))
    
    # 2. Regional Savings
    regional_data = df.groupby('region')['savings_millions'].sum().sort_values(ascending=True)
    bars = ax2.barh(regional_data.index, regional_data.values, color='steelblue')
    ax2.set_xlabel('Annual Savings ($ Millions)')
    ax2.set_title('Savings by Region', fontweight='bold')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'${width:.1f}M', ha='left', va='center', fontweight='bold')
    
    # 3. Top Savings Categories
    category_data = df.groupby('category')['savings_millions'].sum().sort_values(ascending=False).head(8)
    ax3.bar(range(len(category_data)), category_data.values, color='royalblue')
    ax3.set_xlabel('Service Category')
    ax3.set_ylabel('Annual Savings ($ Millions)')
    ax3.set_title('Top Savings Categories', fontweight='bold')
    ax3.set_xticks(range(len(category_data)))
    ax3.set_xticklabels([cat.replace(' - ', '\n') for cat in category_data.index], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, v in enumerate(category_data.values):
        ax3.text(i, v + 1, f'${v:.1f}M', ha='center', va='bottom', fontweight='bold')
    
    # 4. Program Scale Metrics
    metrics_text = f"""Program Scale:
    
Total Members: {total_members:,.0f}
Member Months: {df['MM'].sum():,.0f}

Per-Member Impact:
Annual Savings: ${total_savings/total_members:.0f}
Monthly Savings: ${total_savings/(total_members*12):.2f}

Cost Efficiency:
Savings Rate: {savings_rate:.2f}%
Total Program Cost: ${total_cost:,.0f}"""
    
    ax4.text(0.05, 0.95, metrics_text, ha='left', va='top', fontsize=11, 
             transform=ax4.transAxes, fontfamily='monospace')
    ax4.axis('off')
    ax4.add_patch(plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, linewidth=2, color='navy'))
    
    plt.tight_layout()
    plt.savefig('managed_care_impact_summary.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_detailed_category_analysis():
    """Create detailed analysis of savings by category"""
    df = load_data()
    
    # Get category data with additional metrics
    category_analysis = df.groupby('category').agg({
        'savings_display': 'sum',
        'cost': 'sum',
        'MM': 'sum'
    }).reset_index()
    
    category_analysis['savings_millions'] = category_analysis['savings_display'] / 1_000_000
    category_analysis['cost_millions'] = category_analysis['cost'] / 1_000_000
    category_analysis['savings_rate'] = (category_analysis['savings_display'] / category_analysis['cost']) * 100
    category_analysis['savings_pmpm'] = category_analysis['savings_display'] / category_analysis['MM']
    
    # Sort by total savings
    category_analysis = category_analysis.sort_values('savings_millions', ascending=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    fig.suptitle('Managed Care Savings Analysis by Service Category', fontsize=16, fontweight='bold')
    
    # Horizontal bar chart of total savings
    bars1 = ax1.barh(category_analysis['category'], category_analysis['savings_millions'], 
                     color='steelblue', alpha=0.8)
    ax1.set_xlabel('Annual Savings ($ Millions)')
    ax1.set_title('Total Annual Savings by Category')
    
    # Add value labels
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'${width:.1f}M', ha='left', va='center', fontweight='bold')
    
    # Scatter plot of savings rate vs total cost
    scatter = ax2.scatter(category_analysis['cost_millions'], category_analysis['savings_rate'], 
                         s=category_analysis['savings_millions']*10, alpha=0.7, color='navy')
    ax2.set_xlabel('Total Category Cost ($ Millions)')
    ax2.set_ylabel('Savings Rate (%)')
    ax2.set_title('Savings Rate vs Category Size\n(Bubble size = Total Savings)')
    
    # Add category labels to scatter plot
    for i, row in category_analysis.iterrows():
        ax2.annotate(row['category'].split(' - ')[0], 
                    (row['cost_millions'], row['savings_rate']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('category_savings_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_regional_comparison():
    """Create comprehensive regional comparison"""
    df = load_data()
    
    regional_data = df.groupby('region').agg({
        'savings_display': 'sum',
        'cost': 'sum',
        'MM': 'sum'
    }).reset_index()
    
    regional_data['savings_millions'] = regional_data['savings_display'] / 1_000_000
    regional_data['cost_millions'] = regional_data['cost'] / 1_000_000
    regional_data['savings_rate'] = (regional_data['savings_display'] / regional_data['cost']) * 100
    regional_data['members'] = regional_data['MM'] / 12
    regional_data['savings_per_member'] = regional_data['savings_display'] / regional_data['members']
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Regional Performance Comparison - Managed Care Savings', fontsize=16, fontweight='bold')
    
    # 1. Total savings by region
    bars1 = ax1.bar(regional_data['region'], regional_data['savings_millions'], color='steelblue')
    ax1.set_title('Total Annual Savings by Region')
    ax1.set_ylabel('Savings ($ Millions)')
    ax1.tick_params(axis='x', rotation=45)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'${height:.1f}M', ha='center', va='bottom', fontweight='bold')
    
    # 2. Savings rate by region
    bars2 = ax2.bar(regional_data['region'], regional_data['savings_rate'], color='royalblue')
    ax2.set_title('Savings Rate by Region')
    ax2.set_ylabel('Savings Rate (%)')
    ax2.tick_params(axis='x', rotation=45)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    # 3. Member population by region
    bars3 = ax3.bar(regional_data['region'], regional_data['members']/1000, color='lightblue')
    ax3.set_title('Member Population by Region')
    ax3.set_ylabel('Members (Thousands)')
    ax3.tick_params(axis='x', rotation=45)
    
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{height:.0f}K', ha='center', va='bottom', fontweight='bold')
    
    # 4. Savings per member
    bars4 = ax4.bar(regional_data['region'], regional_data['savings_per_member'], color='mediumblue')
    ax4.set_title('Annual Savings per Member')
    ax4.set_ylabel('Savings per Member ($)')
    ax4.tick_params(axis='x', rotation=45)
    
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'${height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('regional_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_all_static_charts():
    """Generate all static chart visualizations"""
    print("Creating static visualizations...")
    
    create_executive_summary_chart()
    print("✓ Executive summary chart created: managed_care_impact_summary.png")
    
    create_detailed_category_analysis()
    print("✓ Category analysis chart created: category_savings_analysis.png")
    
    create_regional_comparison()
    print("✓ Regional comparison chart created: regional_comparison.png")
    
    print("\nAll static visualization files created successfully!")

if __name__ == "__main__":
    generate_all_static_charts()