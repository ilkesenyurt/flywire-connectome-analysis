import pandas as pd
import plotly.io as pio
import navis
from fafbseg import flywire

#loading the connectivity table and neurotransmitter predictions
connections = pd.read_csv("connections_princeton.csv")
neurons = pd.read_csv("neurons.csv")

print("Connections Table:")
print(connections.head())
print("\nShape:", connections.shape)

print("\nNeurons Table:")
print(neurons.head())
print("\nShape:", neurons.shape)
print(neurons.columns.tolist())
print("\n",connections['nt_type'].value_counts())

# 5 largest synapse counts
print("\npost_root_id\n",connections['syn_count'].nlargest())
# 10 of the higest vale
input_totals = connections.groupby('post_root_id')['syn_count'].sum()
top10 = input_totals.nlargest(10)
print("\n",top10)




top10_ids = top10.index.tolist()

top10_info = neurons[neurons['root_id'].isin(top10_ids)][['root_id', 'nt_type']]
print(top10_info)

# Fetching the 3D skeletons from flywire
skeletons = flywire.get_skeletons(top10_ids, dataset='783')

# Defining colors for neurotransmitters
nt_colors = {
    'ACH':  'red',        # Acetylcholine
    'GABA': 'blue',       # GABA
    'GLUT': 'green',      # Glutamate
    'DA':   'orange',     # Dopamine
    'SER':  'purple',     # Serotonin
    'OCT':  'cyan',       # Octopamine
}

# Building a color list
id_to_nt = dict(zip(top10_info['root_id'], top10_info['nt_type']))
colors = [nt_colors.get(id_to_nt.get(int(s.id), 'ACH'), 'gray') for s in skeletons]

# Plotting
pio.renderers.default = 'browser'
fig = navis.plot3d(skeletons, color=colors, backend='plotly')
fig.show()