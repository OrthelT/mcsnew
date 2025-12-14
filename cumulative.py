import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from src.analysis import get_summary_by_sfy

# Get summary by SFY
df = get_summary_by_sfy()
df = df.sort_values('SFY')

years = df['SFY'].astype(int).tolist()
savings = df['Total Savings'].tolist()

# Calculate cumulative savings
cumulative_savings = np.cumsum(savings)

# Format currency
def format_currency(x, pos=None):
    if x >= 1e9:
        return f'\${x/1e9:.2f}B'
    elif x >= 1e6:
        return f'\${x/1e6:.1f}M'
    elif x >= 1e3:
        return f'\${x/1e3:.0f}K'
    else:
        return f'\${x:.0f}'

# Create figure
fig, ax = plt.subplots(figsize=(12, 7))

# Colors
primary_color = '#1e3a5f'
accent_color = '#5fb49c'
bar_color = '#89c4f4'

# Plot cumulative line with area fill
ax.fill_between(years, cumulative_savings, alpha=0.3, color=primary_color)
ax.plot(years, cumulative_savings, marker='o', markersize=12, linewidth=3, 
        color=primary_color, markerfacecolor=accent_color,
        markeredgecolor='white', markeredgewidth=2, label='Cumulative Savings', zorder=5)

# Add bar chart for annual savings (secondary, lighter)
bar_width = 0.4
bars = ax.bar(years, savings, width=bar_width, alpha=0.5, color=bar_color, 
              edgecolor='white', label='Annual Savings', zorder=3)

# Add cumulative value labels
for x, y in zip(years, cumulative_savings):
    ax.annotate(format_currency(y),
                xy=(x, y),
                xytext=(0, 15),
                textcoords='offset points',
                ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=primary_color)

# Add annual savings labels on bars
for bar, val in zip(bars, savings):
    height = bar.get_height()
    ax.annotate(format_currency(val),
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords='offset points',
                ha='center', va='bottom',
                fontsize=9, color='#555555')

ax.set_xlabel('State Fiscal Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Savings (\$)', fontsize=12, fontweight='bold')
ax.set_title('NC Medicaid Managed Care Cumulative Savings Trend\\n(SFY 2022-2026)', 
             fontsize=14, fontweight='bold', pad=20)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
ax.set_xticks(years)
ax.set_xticklabels([f'SFY {y}' for y in years])

ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)

# Legend
ax.legend(loc='upper left', fontsize=10)

# Add annotation for total
total = cumulative_savings[-1]
ax.annotate(f'Total Cumulative Savings:\\n{format_currency(total)}',
            xy=(0.98, 0.20), xycoords='axes fraction',
            ha='right', va='bottom',
            fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=primary_color, alpha=0.9))

plt.tight_layout()

# Save
output_path = 'output/cumulative_savings_trend2.png'
fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()

print(f'Saved to {output_path}')

# Print summary
print('\\nCumulative Savings by Fiscal Year:')
print('-' * 50)
for y, annual, cumul in zip(years, savings, cumulative_savings):
    print(f'  SFY {y}: Annual {format_currency(annual):>10} | Cumulative {format_currency(cumul):>10}')
print('-' * 50)
print(f'  TOTAL CUMULATIVE SAVINGS: {format_currency(total)}')