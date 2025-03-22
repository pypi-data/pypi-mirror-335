# Imports.

from . import Preprocessing
from . import Utilities as util

from .. import Global_Utilities as gu

# Main function definition.

def Global_Analysis_Main( ip ):

    features_df, std_of_features_df = [], []

    resin_data = gu.get_list_of_resins_data( ip.directory ) # Obtain the spreadsheet of data for the resins.

    if ip.rerun_compute_features:

        Preprocessing.rerun_compute_features( ip.name )

    if ip.read_files:

        features_df, std_of_features_df, rank_features_df = Preprocessing.read_files_and_preprocess( ip, ip.datasets_to_read, name_appendage = ip.name_appendage )

    if ip.plot_global_features:

        gu.plot_global_features( ip.output_directory + "Global/", features_df.to_numpy(), features_df.columns, [resin_data.loc[i]["Label"] for i in features_df.index] )

    if ip.scatterplot:

        features_df, std_of_features_df, rank_features_df = Preprocessing.read_files_and_preprocess( ip, datasets_to_read = ip.datasets_to_read, normalised = False, minimal_datasets = True, feature_1 = ip.scatterplot_x, feature_2 = ip.scatterplot_y )

        return util.scatterplots( ip, features_df, std_of_features_df )

    if ip.correlation_heatmaps:

        spearman_rank_df = util.correlation_heatmap( rank_features_df, spearman = True )
        pearson_df = util.correlation_heatmap( features_df )

        gu.plot_df_heatmap( spearman_rank_df, savefig = True, filename = ip.output_directory + "Global/Correlations/Spearman.pdf" )
        gu.plot_df_heatmap( pearson_df, savefig = True, filename = ip.output_directory + "Global/Correlations/Pearson.pdf" )

    if ip.pca:

        return util.pca( ip, features_df, std_of_features_df, name_appendage = ip.name_appendage )

    if ip.distance_to_virgin_analysis_based_on_pcas:

        util.distance_to_virgin_analysis_based_on_pcas( ip.output_directory, features_df )

    if ip.huang_brown_model:

        util.huang_brown_model( ip )

    if ip.manual_ml:

        util.manual_ml( ip.directory, ip, features_df )

    if ip.pca_ml:

        util.pca_ml( ip.directory, ip, features_df )

    if ip.sandbox:

        util.sandbox( ip, features_df, std_of_features_df )
