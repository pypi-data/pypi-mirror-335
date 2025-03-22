##############
# How I previously obtained a directory.

from pathlib import Path

directory = Path( __file__ ).absolute().parents[1].as_posix() + "/"

##############
# Adding a path to the sys list.

import sys
from pathlib import Path

sys.path.append( Path( __file__ ).absolute().parents[3].as_posix() )

##############

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

def plot_dendrogram( model, **kwargs ):

    # Create linkage matrix and then plot the dendrogram

    counts = np.zeros( model.children_.shape[0] )
    n_samples = len( model.labels_ )

    for i, merge in enumerate( model.children_ ):

        current_count = 0

        for child_idx in merge:

            if child_idx < n_samples:

                current_count += 1  # leaf node

            else:

                current_count += counts[child_idx - n_samples]

        counts[i] = current_count

    linkage_matrix = np.column_stack( [model.children_, model.distances_, counts] ).astype( float )

    # Plot the corresponding dendrogram.

    dendrogram( linkage_matrix, **kwargs )

def plot_dendrogram_2( output_directory, features, file_data ):
    """7/9/23: A second way of plotting a dendrogram. Starting from features instead of a distance matrix,
    this works in the same way as the maths of gu.plot_dendrogram. It has the flexibility of defining the metric from which
    the distance matrix is created, but you can't use linkage 'ward' with any metric that isn't 'Euclidean'."""

    model = AgglomerativeClustering( distance_threshold = 0, n_clusters = None, affinity = 'manhattan', linkage = 'single' )

    model = model.fit( features )

    plt.figure( figsize = ( 18, 14 ) )

    labels = np.array( [f[2] for f in file_data] )

    plot_dendrogram( model, labels = labels, count_sort = True )

    ax = plt.gca()
    ax.tick_params( axis = 'x', which = 'major', labelsize = 15 )
    plt.tight_layout()

    plt.savefig( output_directory + "Features/Dendrogram.pdf" )

# The below is copied from Global_Analysis_Old.py

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from scipy.spatial.distance import squareform
import matplotlib.cm as cm
import numpy as np

def plot_distances( output_directory, subdirectory, df, sample_mask, labels = True ):

    fig, ax = plt.subplots()
    im = ax.imshow( df, cmap = cm.coolwarm )
    plt.xticks( np.arange( 0, len( sample_mask ), 1 ) )
    plt.yticks( np.arange( 0, len( sample_mask ), 1 ) )

    ax.set_xticklabels( sample_mask, rotation = 270, fontsize = 6 )
    ax.set_yticklabels( sample_mask, fontsize = 6 )

    for i in range( len( sample_mask ) ):

        for j in range( len( sample_mask ) ):

            ax.text( j, i, "{:.1f}".format( df.iloc[i, j] ), size = 6, ha = "center", va = "center", color = "w" )

    plt.tight_layout()
    ax.invert_yaxis()
    plt.savefig( subdirectory + "/Distances.pdf" )
    plt.close()

dir = "Users/philsmith/Documents/Postdoc/rHDPE_Data_Analysis/Distance_Matrices/"

sample_mask = [11, 14, 10, 4, 13, 21, 23, 18, 22, 20, 2, 3, 17, 16, 19, 1, 15, 12, 6, 5, 7, 9, 8]

os.chdir( dir )

matrices_files = glob.glob( "*" )

matrices = []

for f in matrices_files:

    if f == "Output":

        continue

    df = pd.read_csv( f, sep = "," )

    index_names = df.iloc[:, 0].tolist()

    df.rename( index = {df.index[i]:index_names[i] for i in range( len( index_names ) )}, inplace = True )

    df.drop( columns = df.columns[0], inplace = True )

    matrices.append( df )

for i in range( len( matrices ) ):

    max_val = matrices[i].max().max()
    matrices[i] = matrices[i].divide( max_val )

global_df = matrices[0] + matrices[1]

plot_distances( dir, "Output", global_df, sample_mask )

global_array = global_df.to_numpy()

fig, ax = plt.subplots()

condensed_distance_matrix = squareform( global_array )
linkage_matrix = linkage( condensed_distance_matrix, "single" )

dendrogram( linkage_matrix, labels = sample_mask, color_threshold = 0.65 * max( linkage_matrix[:,2] ), count_sort = True )

plt.xlabel( "PCR Sample" )
plt.title( "Clustering wrt FTIR" )
plt.savefig( "Output/Clustering.pdf" )
plt.close()

######
