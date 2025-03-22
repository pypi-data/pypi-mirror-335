# Imports

import pandas as pd

import rHDPE_Data_Analysis.FTIR_Analysis as fa
import rHDPE_Data_Analysis.DSC_Analysis as da
import rHDPE_Data_Analysis.TGA_Analysis as ta
import rHDPE_Data_Analysis.Rheology_Analysis as ra
import rHDPE_Data_Analysis.Colour_Analysis as ca
import rHDPE_Data_Analysis.TT_Analysis as tt
import rHDPE_Data_Analysis.SHM_Analysis as sa
import rHDPE_Data_Analysis.TLS_Analysis as tls
import rHDPE_Data_Analysis.ESCR_Analysis as ea

from . import Utilities as util

from .. import Global_Utilities as gu

# Function definitions.

def rerun_compute_features( name ):

    # Parameters.

    ip = fa.Input_Parameters_Class.Input_Parameters()

    fa.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/FTIR_" + name + "_Parameters.numbers", ip )

    # Main function call.

    fa.Analysis.FTIR_Analysis_Main( ip )

    # Parameters.

    ip = da.Input_Parameters_Class.Input_Parameters()

    da.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/DSC_" + name + "_Parameters.numbers", ip )

    # Main function call.

    da.Analysis.DSC_Analysis_Main( ip )

    # Parameters.

    ip = ta.Input_Parameters_Class.Input_Parameters()

    ta.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/TGA_" + name + "_Parameters.numbers", ip )

    # Main function call.

    ta.Analysis.TGA_Analysis_Main( ip )

    # Parameters.

    ip = ra.Input_Parameters_Class.Input_Parameters()

    ra.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/Rheology_" + name + "_Parameters.numbers", ip )

    # Main function call.

    ra.Analysis.Rheology_Analysis_Main( ip )

    # Parameters.

    ip = ca.Input_Parameters_Class.Input_Parameters()

    ca.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/Colour_" + name + "_Parameters.numbers", ip )

    # Main function call.

    ca.Analysis.Colour_Analysis_Main( ip )

    # Parameters.

    ip = tt.Input_Parameters_Class.Input_Parameters()

    tt.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/TT_" + name + "_Parameters.numbers", ip )

    # Main function call.

    tt.Analysis.TT_Analysis_Main( ip )

    # Parameters.

    ip = sa.Input_Parameters_Class.Input_Parameters()

    sa.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/SHM_" + name + "_Parameters.numbers", ip )

    # Main function call.

    sa.Analysis.SHM_Analysis_Main( ip )

    # Parameters.

    ip = tls.Input_Parameters_Class.Input_Parameters()

    tls.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/TLS_" + name + "_Parameters.numbers", ip )

    # Main function call.

    tls.Analysis.TLS_Analysis_Main( ip )

    # Parameters.

    ip = ea.Input_Parameters_Class.Input_Parameters()

    ea.Input_Parameters_Class.read_parameters_from_numbers_file( ip.directory + "Input_Parameters/ESCR_" + name + "_Parameters.numbers", ip )

    # Main function call.

    ea.Analysis.ESCR_Analysis_Main( ip )

def read_files_and_preprocess( ip, datasets_to_read = [], normalised = True, minimal_datasets = False, feature_1 = "", feature_2 = "", name_appendage = "" ):

    authorised = False

    if type( datasets_to_read ) == int:

        datasets_to_read = [datasets_to_read]

    ip.datasets_to_read = datasets_to_read

    dataset_names = ["FTIR", "DSC", "TGA", "Rheology", "TT", "Colour", "SHM", "TLS", "ESCR", "FTIR2", "FTIR3", "TGA_SB", "SAXS", "GPC", "SAXS"]
    dataset_directories = ["FTIR/Features/", "DSC/Features/", "TGA/Features/", "Rheology/Features/", "TT/Features/", "Colour/Features/", "SHM/Features/", "TLS/Features/", "ESCR/Features/", "FTIR/Integral_Analysis/", "FTIR/Component_Analysis/Features/", "TGA/Sandbox/", "SAXS/Features/", "GPC/Features", "Global/TM/"]

    normalised_ext = ""

    dataset, std_dataset = [], []

    for i in range( len( dataset_names ) ):

        if datasets_to_read:

            if (i + 1) not in datasets_to_read:

                continue

        n = dataset_names[i]

        if not normalised:

            if n == "FTIR2" or n == "FTIR3" or n == "TGA_SB":

                normalised_ext = ""

            else:

                normalised_ext = "_Unnormalised"

        df, authorised = gu.read_csv_pipeline( ip, dataset_directories[i], "Mean_Features" + normalised_ext + name_appendage + ".csv", authorised )
        df_std, authorised = gu.read_csv_pipeline( ip, dataset_directories[i], "Std_of_Features" + normalised_ext + name_appendage + ".csv", authorised )

        if minimal_datasets:

            if feature_1 not in df.columns.tolist():

                if feature_2 not in df.columns.tolist():

                    continue

        dataset.append( df )
        std_dataset.append( df_std )

    if ip.sample_mask == None:

        ip.sample_mask = []

    sample_mask = ip.sample_mask.copy()

    if sample_mask == []:

        sample_mask = list( map( int, dataset[0].iloc[:, 0].tolist() ) )

        for i in range( 1, len( dataset ) ):

            samples_present = dataset[i].iloc[:, 0].tolist()
            sample_mask = gu.remove_redundant_samples( sample_mask, samples_present )

    else:

        for i in range( len( dataset ) ):

            samples_present = dataset[i].iloc[:, 0].tolist()
            sample_mask = gu.remove_redundant_samples( sample_mask, samples_present )

    features, feature_names = util.produce_full_dataset_of_features( dataset, sample_mask )

    rank_features = util.rank_features( features )

    features_df = gu.array_with_column_titles_and_label_titles_to_df( features, feature_names, sample_mask )

    rank_features_df = gu.array_with_column_titles_and_label_titles_to_df( rank_features, feature_names, sample_mask )

    std_of_features, _ = util.produce_full_dataset_of_features( std_dataset, sample_mask )

    std_of_features_df = gu.array_with_column_titles_and_label_titles_to_df( std_of_features, feature_names, sample_mask )

    #===============

    # Extracting the whole dataset as a .csv.

    # resin_data = gu.get_list_of_resins_data( ip.directory )
    #
    # sample_mask_2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    #
    # features_2, feature_names_2, sample_mask_2 = util.compile_full_dataset_of_features( dataset, sample_mask_2 )
    # std_of_features_2, std_of_feature_names_2, sample_mask_2 = util.compile_full_dataset_of_features( std_dataset, sample_mask_2 )
    #
    # features_2_df = gu.array_with_column_titles_and_label_titles_to_df( features_2, feature_names_2, sample_mask_2 )
    # std_of_features_2_df = gu.array_with_column_titles_and_label_titles_to_df( std_of_features_2, std_of_feature_names_2, sample_mask_2 )
    #
    # features_2_df = features_2_df.set_axis( [resin_data.loc[i]["Label"] for i in features_2_df.index], axis = "index" )
    # std_of_features_2_df = std_of_features_2_df.set_axis( [resin_data.loc[i]["Label"] for i in std_of_features_2_df.index], axis = "index" )
    #
    # features_2_df.astype( float ).to_csv( ip.output_directory + "Global/Dataset/Full_Dataset.csv", float_format = "%.5f" )
    # std_of_features_2_df.astype( float ).to_csv( ip.output_directory + "Global/Dataset/Full_Dataset_Std.csv", float_format = "%.5f" )

    #===============

    return features_df, std_of_features_df, rank_features_df
