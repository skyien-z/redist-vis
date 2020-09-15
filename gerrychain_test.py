import csv
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from gerrychain import Graph, Partition

######################################################################
# 
# Test script for checking installation of required packages 
# for the redist-vis project
# 
# Author: Ian Ludden
# 
######################################################################

def read_partition(partition_fname):
    """
    Reads a partition (district map) from a csv file with 
    columns 'GEOID' (unique identifiers for the census tracts) and 'district'. 
    
    Returns a pandas DataFrame object representing the map, where
    'GEOID' is the key.
    """
    with open(partition_fname, 'r') as map_file:
        map_reader = csv.reader(map_file)
        map_raw = list(map_reader)

    map_headers = map_raw.pop(0)
    map_df = pd.DataFrame(map_raw, columns=map_headers).astype({'district': int})
    return map_df.set_index('GEOID')


def get_sample_wi_map(tracts_fname, partition_fname):
    """
    Loads a sample Wisconsin district map. 

    Parameters:
        tracts_fname: the name of the Wisconsin census tracts file (zipped shapefile)
        partition_fname: the name of the initial partition file (.csv)

    Returns:
        the given Wisconsin district map as a GerryChain Partition object
    """
    # Step 1. Build a GeoDataFrame (a geographic version of a pandas DataFrame)
    # from the tracts zip file (adding 'zip://' prefix if missing). 
    tracts_fname = tracts_fname if 'zip://' in tracts_fname else 'zip://' + tracts_fname
    gdf = geopandas.read_file(tracts_fname)
    gdf.set_index('GEOID', inplace=True)

    # Step 2. Load the initial partition and join it to the GeoDataFrame. 
    map_df = read_partition(partition_fname)
    map_gdf = gdf.join(map_df)

    map_gdf['district'].fillna(value=-1, inplace=True) # Slight cleanup

    # Step 3. Create a barebones GerryChain Partition object from the GeoDataFrame. 
    map_graph = Graph.from_geodataframe(map_gdf)
    map_graph.add_data(map_gdf)
    partition = Partition(map_graph, 'district')

    return partition


if __name__ == '__main__':
    tracts_fname = 'data/tl_2013_55_tract.zip'
    partition_fname = 'data/wi_gerrymander_dem.csv'

    sample_map = get_sample_wi_map(tracts_fname, partition_fname)

    # Test GerryChain's built-in plot features (using matplotlib)
    sample_map.plot()
    plt.axis('off')
    plt.show()
