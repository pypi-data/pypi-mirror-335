# Imports.

import os
import glob
import shutil
import re
import numpy as np
import pandas as pd
from numbers_parser import Document

from .. import Global_Utilities as gu

# Function definitions.

def read_raw_data_file_1( filename, resin_data, file_data, data ):

    doc = Document( filename )

    sheets = doc.sheets
    tables = sheets[0].tables
    rows = tables[0].rows()

    for r in rows[1:]:

        file_data.append( [int( r[0].value ), int( r[1].value ), resin_data.loc[int( int( r[0].value ) )]["Label"] + ".{}".format( int( r[1].value ) ), ""] )

        for i in range( 6 ):

            data[i].append( r[i + 2].value )

    for i in range( 6 ):

            data[i] = np.array( data[i] )

def extract_raw_data( directory, data_directory ):
    '''Extract the raw data from the files.'''

    resin_data = gu.get_list_of_resins_data( directory ) # Obtain the spreadsheet of data for the resins.

    file_data, data = [], [[] for i in range( 6 )]

    read_raw_data_file_1( data_directory + "GPC_Data_Summary.numbers", resin_data, file_data, data )

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

    array = data[0][:, np.newaxis]

    for i in range( 1, len( data ) ):

        array = np.hstack( (array, data[i][:, np.newaxis]) )

    np.savetxt( output_directory + "GPC/Condensed_Data/gpc_data" + name_appendage + ".csv", array, delimiter = ",", fmt = "%.2f" )

    array = np.array( file_data )

    np.savetxt( output_directory + "GPC/Condensed_Data/file_data" + name_appendage + ".csv", array, delimiter = ",", fmt = "%s" )

def read_csv( directory, output_directory, merge_groups, name_appendage = "" ):
    '''Read the preprocessed .csv file.'''

    resin_data = gu.get_list_of_resins_data( directory, name_appendage ) # Obtain the spreadsheet of data for the resins.

    file_data = []

    df = pd.read_csv( output_directory + "GPC/Condensed_Data/file_data" + name_appendage + ".csv", sep = ",", header = None )

    for i in range( len( df.index ) ):

        resin = int( df.iloc[i, 0] )
        specimen = int( df.iloc[i, 1] )

        file_data.append( [resin, specimen, resin_data.loc[resin]["Label"] + ".{}".format( specimen ), ""] )

    data = []

    df = pd.read_csv( output_directory + "GPC/Condensed_Data/gpc_data" + name_appendage + ".csv", sep = ",", header = None )

    for i in range( len( df.columns ) ):

        data.append( df.iloc[:, i].to_numpy( dtype = np.float64 ) )

    add_description_to_file_data( file_data )

    if merge_groups:

        gu.merge( file_data )

    return file_data, data

def remove_files( file_data, data, descriptors_to_remove = "" ):
    '''Remove files not needed/wanted for analysis by searching for letters in file descriptions.'''

    return file_data, data

def compute_mean( output_directory, file_data, data, name_appendage = "" ):
    '''Compute the mean data for each resin.'''

    means = []

    for i in range( len( data ) ):

        means.append( np.array( [j[0] for j in gu.sample_mean( file_data, [[data[0][k]] for k in range( len( file_data ) )] )] ) )

    means_array = means[0][:, np.newaxis]

    for i in range( 1, len( means ) ):

        means_array = np.hstack( (means_array, means[i][:, np.newaxis]) )

    np.savetxt( output_directory + "GPC/Condensed_Data/Means.csv", means_array, delimiter = ",", fmt = "%.3f" )

def read_mean( output_directory, data, name_appendage = "" ):
    '''Read the computed means for each resin from a file.'''

    df = pd.read_csv( output_directory + "GPC/Condensed_Data/Means.csv", sep = ",", header = None )

    for i in range( len( df.columns ) ):

        if len( data ) > 6 + i: # A previous list of means is already appended.

            data[6 + i] = df.iloc[:, i].to_numpy( dtype = np.float64 )

        else:

            data.append( df.iloc[:, i].to_numpy( dtype = np.float64 ) )

    return data

def copy_data( output_directory, name_appendage_1, name_appendage_2 ):
    '''Copy data.'''

    shutil.copyfile( output_directory + "GPC/Condensed_Data/gpc_data" + name_appendage_1 + ".csv", output_directory + "GPC/Condensed_Data/gpc_data" + name_appendage_2 + ".csv" )

    shutil.copyfile( output_directory + "GPC/Condensed_Data/file_data" + name_appendage_1 + ".csv", output_directory + "GPC/Condensed_Data/file_data" + name_appendage_2 + ".csv" )

def delete_data( output_directory, name_appendage ):
    '''Delete data.'''

    pattern = re.compile( name_appendage + "\\.csv$" )

    for path in glob.glob( output_directory + "GPC/Condensed_Data/*" ):

        if pattern.search( path ):

            os.remove( path )

    for path in glob.glob( output_directory + "GPC/Features/*" ):

        if pattern.search( path ):

            os.remove( path )
