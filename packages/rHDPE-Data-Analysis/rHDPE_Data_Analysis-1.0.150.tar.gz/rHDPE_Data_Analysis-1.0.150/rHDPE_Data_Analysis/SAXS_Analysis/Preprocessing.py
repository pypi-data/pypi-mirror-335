# Imports.

import os
import glob
import shutil
import re
import numpy as np
import pandas as pd

from .. import Global_Utilities as gu

# Function definitions.

def read_raw_data_file_1( filename, resin_data, file_data, data ):

    sheet = "Sheet 1"

    df = pd.read_excel( filename, sheet )

    resins = df.iloc[:, 0].tolist()

    for r in resins:

        file_data.append( [int( r ), 0, resin_data.loc[int( r )]["Label"] + ".{}".format( 0 ), ""] )

    for i in range( 1, len( df.columns ) ):

        for j in range( len( df ) ):

            data[i - 1].append( df.iloc[j, i] )

def extract_raw_data( directory, data_directory ):
    '''Extract the raw data from the files.'''

    resin_data = gu.get_list_of_resins_data( directory ) # Obtain the spreadsheet of data for the resins.

    file_data, data = [], [[] for i in range( 14 )]

    read_raw_data_file_1( data_directory + "Raw Data.xlsx", resin_data, file_data, data )

    return file_data, data

def standardise_data( data ):
    '''Standardise data.'''

    pass

def add_description_to_file_data( file_data ):
    '''Add descriptions in the form of letters to each specimen.'''

    pass

def read_files_and_preprocess( directory, data_directory, merge_groups ):
    '''Read files and preprocess data.'''

    file_data, data = extract_raw_data( directory, data_directory )

    standardise_data( data )

    add_description_to_file_data( file_data )

    if merge_groups:

        gu.merge( file_data )

    return file_data, data

def write_csv( output_directory, file_data, data, name_appendage = "" ):
    '''Write read and preprocessed data to a .csv file.'''

    pass

    # array = data[0][:, np.newaxis]
    #
    # for i in range( len( data[1] ) ):
    #
    #     array = np.hstack( (array, data[1][i][:, np.newaxis]) )
    #
    # np.savetxt( output_directory + "ESCR/Condensed_Data/escr_data" + name_appendage + ".csv", array, delimiter = ",", fmt = "%.2f" )
    #
    # array = np.array( file_data )
    #
    # np.savetxt( output_directory + "ESCR/Condensed_Data/file_data" + name_appendage + ".csv", array, delimiter = ",", fmt = "%s" )

def read_csv( directory, output_directory, merge_groups, name_appendage = "" ):
    '''Read the preprocessed .csv file.'''

    pass

    # resin_data = gu.get_list_of_resins_data( directory, name_appendage ) # Obtain the spreadsheet of data for the resins.
    #
    # file_data = []
    #
    # df = pd.read_csv( output_directory + "ESCR/Condensed_Data/file_data" + name_appendage + ".csv", sep = ",", header = None )
    #
    # for i in range( len( df.index ) ):
    #
    #     resin = int( df.iloc[i, 0] )
    #     specimen = int( df.iloc[i, 1] )
    #
    #     file_data.append( [resin, specimen, resin_data.loc[resin]["Label"] + ".{}".format( specimen ), ""] )
    #
    # data = []
    #
    # df = pd.read_csv( output_directory + "ESCR/Condensed_Data/escr_data" + name_appendage + ".csv", sep = ",", header = None )
    #
    # data.append( df.iloc[:, 0].to_numpy( dtype = np.float64 ) )
    #
    # percentages = []
    #
    # for i in range( 1, len( df.columns ) ):
    #
    #     percentages.append( df.iloc[:, i].to_numpy( dtype = np.float64 ) )
    #
    # data.append( percentages )
    #
    # data.append( np.array( [24, 48, 72, 96] ) )
    #
    # add_description_to_file_data( file_data )
    #
    # if merge_groups:
    #
    #     gu.merge( file_data )
    #
    # return file_data, data

def remove_files( file_data, data, descriptors_to_remove = "" ):
    '''Remove files not needed/wanted for analysis by searching for letters in file descriptions.'''

    return file_data, data

    # files_to_remove = []
    #
    # for i in range( len( file_data ) ):
    #
    #     s = file_data[i][3]
    #
    #     for l in descriptors_to_remove:
    #
    #         if s.find( l ) > -0.5:
    #
    #             files_to_remove.append( i )
    #
    #             break
    #
    # files_to_remove.reverse()
    #
    # for r in files_to_remove:
    #
    #     file_data.pop( r )
    #     data[1].pop( r )
    #
    # return file_data, data

def compute_mean( output_directory, file_data, data, name_appendage = "" ):
    '''Compute the mean data for each resin.'''

    pass

def read_mean( output_directory, data, name_appendage = "" ):
    '''Read the computed means for each resin from a file.'''

    pass

def copy_data( output_directory, name_appendage_1, name_appendage_2 ):
    '''Delete data.'''

    pass

    # shutil.copyfile( output_directory + "ESCR/Condensed_Data/escr_data" + name_appendage_1 + ".csv", output_directory + "ESCR/Condensed_Data/escr_data" + name_appendage_2 + ".csv" )
    #
    # shutil.copyfile( output_directory + "ESCR/Condensed_Data/file_data" + name_appendage_1 + ".csv", output_directory + "ESCR/Condensed_Data/file_data" + name_appendage_2 + ".csv" )

def delete_data( output_directory, name_appendage ):
    '''Delete data.'''

    pass

    # pattern = re.compile( name_appendage + "\\.csv$" )
    #
    # for path in glob.glob( output_directory + "ESCR/Condensed_Data/*" ):
    #
    #     if pattern.search( path ):
    #
    #         os.remove( path )
    #
    # for path in glob.glob( output_directory + "ESCR/Features/*" ):
    #
    #     if pattern.search( path ):
    #
    #         os.remove( path )
