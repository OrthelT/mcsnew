import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from millify import millify

# Set style for matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

def load_data():
    """Load and prepare data for visualizations"""
    # Load the detailed data
    df = pd.read_csv('mcs_saving2.csv')
    
    # Convert savings to positive values for display (since negative = savings)
    df['savings_display'] = -df['savings']
    df['savings_millions'] = df['savings_display'] / 1_000_000
    df['cost_millions'] = df['cost'] / 1_000_000
    
    return df

def create_total_savings_summary():
    """Create summary statistics for total program savings"""
    df = load_data()
    
    total_savings = -df['savings'].sum()  # Convert to positive
    total_cost = df['cost'].sum()
    savings_rate = (total_savings / total_cost) * 100
    total_members = df['MM'].sum() / 12  # Convert member months to members
    
    return {
        'total_savings': total_savings,
        'total_cost': total_cost,
        'savings_rate': savings_rate,
        'total_members': total_members,
        'savings_per_member': total_savings / total_members
    }

def create_regional_savings_chart():
    """Create bar chart showing savings by region"""
    df = load_data()
    regional_data = df.groupby('region').agg({
        'savings_display': 'sum',
        'cost': 'sum',
        'MM': 'sum'
    }).reset_index()
    
    regional_data['savings_millions'] = regional_data['savings_display'] / 1_000_000
    regional_data['savings_rate'] = (regional_data['savings_display'] / regional_data['cost']) * 100
    regional_data['members'] = regional_data['MM'] / 12
    
    # Create the visualization
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Annual Managed Care Savings by Region ($ Millions)', 
                       'Savings Rate by Region (%)'),
        vertical_spacing=0.12
    )
    
    # Savings bar chart
    fig.add_trace(
        go.Bar(
            x=regional_data['region'],
            y=regional_data['savings_millions'],
            name='Savings ($ Millions)',
            marker_color='#2E8B57',
            text=[f'${x:.1f}M' for x in regional_data['savings_millions']],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Savings rate bar chart
    fig.add_trace(
        go.Bar(
            x=regional_data['region'],
            y=regional_data['savings_rate'],
            name='Savings Rate (%)',
            marker_color='#4682B4',
            text=[f'{x:.2f}%' for x in regional_data['savings_rate']],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title_text="North Carolina Medicaid Managed Care Savings by Region",
        title_x=0.5,
        showlegend=False,
        height=700
    )
    
    fig.update_yaxes(title_text="Savings ($ Millions)", row=1, col=1)
    fig.update_yaxes(title_text="Savings Rate (%)", row=2, col=1)
    fig.update_xaxes(title_text="Region", row=2, col=1)
    
    return fig

def create_category_savings_chart():
    """Create chart showing savings by service category"""
    df = load_data()
    category_data = df.groupby('category').agg({
        'savings_display': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    category_data['savings_millions'] = category_data['savings_display'] / 1_000_000
    category_data = category_data.sort_values('savings_millions', ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=category_data['category'],
        x=category_data['savings_millions'],
        orientation='h',
        marker_color='#228B22',
        text=[f'${x:.1f}M' for x in category_data['savings_millions']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Annual Managed Care Savings by Service Category",
        title_x=0.5,
        xaxis_title="Annual Savings ($ Millions)",
        yaxis_title="Service Category",
        height=600,
        margin=dict(l=200)
    )
    
    return fig

def create_impact_dashboard():
    """Create comprehensive dashboard showing program impact"""
    summary = create_total_savings_summary()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Program Savings',
            'Savings Rate',
            'Per-Member Annual Savings',
            'Program Scale'
        ),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # Total savings indicator
    fig.add_trace(go.Indicator(
        mode="number",
        value=summary['total_savings'],
        title={"text": "Total Annual Savings"},
        number={'prefix': "$", 'suffix': "", 'valueformat': ',.0f'},
        domain={'row': 0, 'column': 0}
    ), row=1, col=1)
    
    # Savings rate indicator
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=summary['savings_rate'],
        title={'text': "Overall Savings Rate"},
        number={'suffix': "%", 'valueformat': '.2f'},
        gauge={
            'axis': {'range': [None, 2]},
            'bar': {'color': "#2E8B57"},
            'steps': [
                {'range': [0, 0.5], 'color': "lightgray"},
                {'range': [0.5, 1], 'color': "yellow"},
                {'range': [1, 2], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.5
            }
        }
    ), row=1, col=2)
    
    # Per-member savings
    fig.add_trace(go.Indicator(
        mode="number",
        value=summary['savings_per_member'],
        title={"text": "Annual Savings Per Member"},
        number={'prefix': "$", 'valueformat': ',.0f'}
    ), row=2, col=1)
    
    # Program scale
    fig.add_trace(go.Indicator(
        mode="number",
        value=summary['total_members'],
        title={"text": "Total Members Served"},
        number={'valueformat': ',.0f'}
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="North Carolina Medicaid Managed Care Program Impact",
        title_x=0.5,
        height=500
    )
    
    return fig

def create_cost_comparison_chart():
    """Create before/after cost comparison visualization"""
    df = load_data()
    
    # Calculate what costs would be without managed care
    df['cost_without_mc'] = df['cost'] + abs(df['savings'])
    
    regional_comparison = df.groupby('region').agg({
        'cost': 'sum',
        'cost_without_mc': 'sum',
        'savings_display': 'sum'
    }).reset_index()
    
    regional_comparison['cost_millions'] = regional_comparison['cost'] / 1_000_000
    regional_comparison['cost_without_mc_millions'] = regional_comparison['cost_without_mc'] / 1_000_000
    
    fig = go.Figure()
    
    # Without managed care costs
    fig.add_trace(go.Bar(
        name='Without Managed Care',
        x=regional_comparison['region'],
        y=regional_comparison['cost_without_mc_millions'],
        marker_color='#CD5C5C'
    ))
    
    # With managed care costs
    fig.add_trace(go.Bar(
        name='With Managed Care',
        x=regional_comparison['region'],
        y=regional_comparison['cost_millions'],
        marker_color='#2E8B57'
    ))
    
    fig.update_layout(
        title='Cost Comparison: With vs. Without Managed Care',
        title_x=0.5,
        xaxis_title='Region',
        yaxis_title='Annual Cost ($ Millions)',
        barmode='group',
        height=500
    )
    
    return fig

def generate_all_visualizations():
    """Generate and save all visualizations"""
    print("Creating managed care savings visualizations...")
    
    # Create summary statistics
    summary = create_total_savings_summary()
    print(f"\n=== NORTH CAROLINA MEDICAID MANAGED CARE SAVINGS SUMMARY ===")
    print(f"Total Annual Savings: ${summary['total_savings']:,.0f}")
    print(f"Overall Savings Rate: {summary['savings_rate']:.2f}%")
    print(f"Total Members Served: {summary['total_members']:,.0f}")
    print(f"Annual Savings Per Member: ${summary['savings_per_member']:,.0f}")
    print("=" * 65)
    
    # Generate visualizations
    regional_fig = create_regional_savings_chart()
    regional_fig.write_html("regional_savings.html")
    
    category_fig = create_category_savings_chart()
    category_fig.write_html("category_savings.html")
    
    dashboard_fig = create_impact_dashboard()
    dashboard_fig.write_html("impact_dashboard.html")
    
    comparison_fig = create_cost_comparison_chart()
    comparison_fig.write_html("cost_comparison.html")
    
    print("\nVisualization files created:")
    print("- regional_savings.html")
    print("- category_savings.html") 
    print("- impact_dashboard.html")
    print("- cost_comparison.html")

if __name__ == "__main__":
    generate_all_visualizations()