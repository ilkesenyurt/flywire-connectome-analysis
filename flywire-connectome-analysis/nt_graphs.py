import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Loading the data
connections = pd.read_csv("connections_princeton.csv")
neurons = pd.read_csv("neurons.csv")
input_totals = connections.groupby('post_root_id')['syn_count'].sum()

# Constants
nts = ['ACH','GABA','GLUT','DA','SER','OCT']

# Which groups to plot
groups = [
    ('Whole brain', None),
    ('Top 100,000', 100000),
    ('Top 50,000',  50000),
    ('Top 10,000',  10000),
    ('Top 5,000',   5000),
    ('Top 1,000',   1000),
    ('Top 500',     500),
    ('Top 100',     100),
    ('Top 50',      50),
    ('Top 10',      10),
]

# Computation function
def get_nt_fractions(n):
    """Return the neurotransmitter distribution (as fractions) for the top n hub neurons.
    If n is None, returns the whole-brain baseline."""
    if n is None:
        info = neurons
    else:
        top_ids = input_totals.nlargest(n).index.tolist()
        info = neurons[neurons['root_id'].isin(top_ids)]
    
    fractions = info['nt_type'].value_counts(normalize=True)
    return [fractions.get(nt, 0) for nt in nts]


# Plotting function
def plot_trends_log(thresholds):
    """thresholds: list of numeric thresholds, e.g. [10, 50, 100, 500, ...]
    Does not include whole brain — just specific hub thresholds."""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    all_fractions = np.array([get_nt_fractions(n) for n in thresholds])
    
    for nt_idx, nt in enumerate(nts):
        ax.plot(thresholds, all_fractions[:, nt_idx], marker='o', label=nt, linewidth=2)
    
    ax.set_xscale('log')
    ax.set_xlabel('Number of top hubs (log scale)')
    ax.set_ylabel('Fraction of neurons')
    ax.set_title('Neurotransmitter composition vs. hub size')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')  # both = major and minor gridlines
    plt.tight_layout()
    plt.show()


thresholds = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 139255]
plot_trends_log(thresholds)

# Adding input totals to the neurons table
neurons_with_totals = neurons.merge(
    input_totals.rename('total_input').reset_index(),
    left_on='root_id',
    right_on='post_root_id',
    how='left'
).fillna({'total_input': 0})


# Data summary
print("Input count statistics:")
print(neurons_with_totals['total_input'].describe())
print(f"\nNeurons with zero inputs: {(neurons_with_totals['total_input'] == 0).sum()}")
print(f"Neurons with 1 input: {(neurons_with_totals['total_input'] == 1).sum()}")
print(f"Neurons with ≤10 inputs: {(neurons_with_totals['total_input'] <= 10).sum()}")

# Splitting into q equal neuron number groups
neurons_with_totals['input_bin'] = pd.qcut(neurons_with_totals['total_input'],q=50,labels=False,duplicates='drop')

n_bins = neurons_with_totals['input_bin'].nunique()
print(f"\nNumber of bins formed: {n_bins}")

# Neurotransmitter distribution per bin (as fractions)
bin_composition = (neurons_with_totals.groupby('input_bin')['nt_type'].value_counts(normalize=True).unstack(fill_value=0))

# Mean input count per bin (for x-axis)
bin_means = neurons_with_totals.groupby('input_bin')['total_input'].mean()

print("\nNeurotransmitter composition per bin:")
print(bin_composition.round(3))
print("\nMean input count per bin:")
print(bin_means.round(1))

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))

for nt in nts:
    if nt in bin_composition.columns:
        ax.plot(bin_means.values,bin_composition[nt].values,marker='o', label=nt, linewidth=2)

ax.set_xscale('log')
ax.set_xlabel('Mean input synapse count per bin (log scale)')
ax.set_ylabel('Fraction of neurons')
ax.set_title('Neurotransmitter composition by input percentile bins')
ax.legend()
ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.show()

# Finding the bins with the bumps
bump_bins = [3, 4, 5]  # Bins in the middle (bin numaraları grafikte 0-indexed)

# Group distribution of neurons in those bins
bump_neurons = neurons_with_totals[neurons_with_totals['input_bin'].isin(bump_bins)]
print("Bumpun olduğu binlerdeki grup dağılımı:")
print(bump_neurons['group'].value_counts(normalize=True).head(10))

# Comparing low input bin neurons groups
low_neurons = neurons_with_totals[neurons_with_totals['input_bin'].isin([0, 1])]
print("\nGroup distribution of low input bin neurons:")
print(low_neurons['group'].value_counts(normalize=True).head(10))

# High input bins
high_neurons = neurons_with_totals[neurons_with_totals['input_bin'].isin([8, 9])]
print("\nGroup distribution of high input bin neurons:")
print(high_neurons['group'].value_counts(normalize=True).head(10))


# Top groups per bin
bin_group_composition = (neurons_with_totals.groupby('input_bin')['group'].value_counts(normalize=True).unstack(fill_value=0))

# Keep the most common 8 groups and group the others as "Other"
top_groups = bin_group_composition.sum().nlargest(8).index
other_sum = bin_group_composition.drop(columns=top_groups).sum(axis=1)
bin_group_composition = bin_group_composition[top_groups]
bin_group_composition['Other'] = other_sum

# Stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))
bin_group_composition.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
ax.set_xlabel('Input percentile bin (0 = fewest inputs, 9 = most)')
ax.set_ylabel('Fraction of neurons')
ax.set_title('Brain region composition across input percentile bins')
ax.legend(title='Region', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()