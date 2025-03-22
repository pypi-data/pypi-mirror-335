# Imports.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl

from .. import Global_Utilities as gu

# Function definitions.

def plot_data( ip, file_data, data, savefig = True, name_appendage = "" ):

    resin_data = gu.get_list_of_resins_data( ip.directory, name_appendage )

    feature_names, features = gu.csv_to_df_to_array_and_column_titles( ip.output_directory + "SAXS/Features/Features.csv" )

    sample, sample_array, samples_present, samples_present_array = gu.sample_data_from_file_data( file_data )

    samples_to_plot = samples_present
    samples_to_plot = [16, 17, 19, 12, 15, 1, 2, 3, 5, 6, 7, 8, 9, 4, 10, 13, 11, 18, 20, 21, 22, 23]

    specimens = False
    all_specimens = True
    specimen_mask = []

    mean = True

    if mean:

        mean_features = gu.extract_mean_features( features, sample_array, samples_to_plot )

        std_of_features = gu.extract_std_of_features( features, sample_array, samples_to_plot )

        bar_weights = {"Lc": mean_features[:, 3], "La": mean_features[:, 4]}
        hatch = {"Lc": "/", "La": "*"}

        y_pos = np.arange( len( mean_features[:, 0] ) )

        colours = gu.list_of_colours()
        colours = [colours[i] for i in samples_to_plot]

        fig, ax = plt.subplots()
        bottom = np.zeros( len( mean_features[:, 3] ) )

        for label, weight in bar_weights.items():

            ax.bar( y_pos, weight, label = label, bottom = bottom, align = 'center', alpha = 0.5, color = colours, edgecolor = "black", hatch = hatch[label] )

            bottom += weight

        # plt.bar( y_pos, mean_features[:, 0], align = 'center', alpha = 0.5, color = colours )

        plt.xticks( y_pos, [resin_data.loc[i]["Label"] for i in samples_to_plot], rotation = 90 )

        legend_1 = mpatches.Patch( facecolor = "white", edgecolor = "black", hatch = "/",label = "lc" )
        legend_2 = mpatches.Patch( facecolor = "white", edgecolor = "black", hatch = "*",label = "la" )
        plt.legend( handles = [legend_1, legend_2] )

        # plt.xlabel( xlabel )
        plt.ylabel( "d" )
        # plt.title( title )
        #
        # plt.ylim( [55, 75] )
        #
        plt.tight_layout()
        #
        if savefig:

            plt.savefig( ip.output_directory + "SAXS/Plots/Plot.pdf" )

        else:

            plt.show()

        plt.close()


