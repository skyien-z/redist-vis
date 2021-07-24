from collections import deque
import csv
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import pandas as pd
import random

import gerrychain
from gerrychain.accept import always_accept
from gerrychain.proposals import propose_random_flip

# Constants
DEFAULT_POP_BAL_THRESHOLD = 0.05

def add_population_data(gdf, populations_file_path=None):
    """
    Reads a population data file (CSV) and 
    joins it to the given GeoDataFrame using
    'GEOID' as the index/key. 

    The CSV file must have at least a 'GEOID' column and
    a 'population' column. Any other columns will be ignored.

    If populations_file_path is None, 
    then populations are all set to 1. 

    Returns the new GeoDataFrame with population data. 
    The given gdf is modified. 
    """
    if populations_file_path is None:
        gdf['population'] = 1.
        return gdf
    
    pop_df = pd.read_csv(populations_file_path)
    pop_df = pop_df[['GEOID', 'population']]
    pop_df = pop_df.astype({'GEOID': str})
    pop_df.set_index('GEOID', inplace=True)
    
    return gdf.join(pop_df)


def add_voteshare_data(gdf, voteshares_file_path=None):
    """
    Reads a voteshares data file (CSV) and 
    joins it to the given GeoDataFrame using
    'GEOID' as the index/key. 

    The CSV file must have at least a 'GEOID' column, 
    a 'gop_voteshare' column, and 
    a 'dem_voteshare' column. 
    Any other columns will be ignored.

    If voteshares_file_path is None, 
    then voteshares are all set to 0.5. 

    Returns the new GeoDataFrame with voteshare data, 
    including the given voteshares and 
    computed votes columns (voteshare times population). 
    Since this requires the gdf to have a 'population' column,
    `add_population_data` should be called first. 

    The given gdf is modified. 
    """
    if voteshares_file_path is None:
        gdf['gop_voteshare'] = 0.5
        gdf['dem_voteshare'] = 0.5
        return gdf

    voteshare_df = pd.read_csv(voteshares_file_path)
    voteshare_df = voteshare_df[['GEOID', 'gop_voteshare', 'dem_voteshare']]
    voteshare_df = voteshare_df.astype({'GEOID': str})
    voteshare_df.set_index('GEOID', inplace=True)

    gdf = gdf.join(voteshare_df)
    gdf['gop_votes'] = gdf['gop_voteshare'] * gdf['population']
    gdf['dem_votes'] = gdf['dem_voteshare'] * gdf['population']

    return gdf


def build_partition(gdf, assignment_file_path=None, assignment_dict=None):
    """
    Loads a CSV representing a district plan as 
    a mapping of 'GEOID' to 'district', 
    or loads a district plan from an assignment dictionary 
    mapping GEOIDs to district indices. 

    Creates a gerrychain.Partition object using
    the graph of the given GeoDataFrame and 
    the assignment mapping. 
    """
    if assignment_file_path is not None:
        with open(assignment_file_path, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
        headers = data.pop(0)
        assignment = {data[i][0]: int(data[i][1]) for i in range(len(data))}
    else:
        assert(assignment_dict is not None)
        assignment = assignment_dict
        headers = ['GEOID', 'district']

    graph = gerrychain.Graph.from_geodataframe(gdf)
    nodes = list(graph.nodes)

    unassigned = []
    # Resolve any issues with unassigned units
    for node in nodes:
        if node not in assignment.keys():
            unassigned.append(node)

    while unassigned:
        node = unassigned.pop()
        for neighbor in graph.neighbors(node):
            if neighbor in assignment:
                assignment[node] = assignment[neighbor]
    
    # Add district assignment to GeoDataFrame
    assignment_array = [[node, assignment[node]] for node in assignment]
    assignment_df = pd.DataFrame(assignment_array, columns=headers)
    assignment_df.set_index('GEOID', inplace=True)
    gdf = gdf.join(assignment_df)
    graph.add_data(gdf)

    # Make sure population and votes columns exist even if data is missing
    if 'population' not in gdf.columns:
        gdf['population'] = 1.
    if 'gop_votes' not in gdf.columns:
        gdf['gop_votes'] = 0
    if 'dem_votes' not in gdf.columns:
        gdf['dem_votes'] = 0

    return gerrychain.Partition(graph, assignment, updaters={
        'population': gerrychain.updaters.Tally('population'), 
        'gop_votes': gerrychain.updaters.Tally('gop_votes'),
        'dem_votes': gerrychain.updaters.Tally('dem_votes')
        }) # The updater {'cut_edges': cut_edges} is included by default


def build_grid_graph(rows, cols):
    """
    Builds a rows-by-cols grid graph with 
    each unit having population 1. 

    TODO: Consider using gerrychain.Grid here
    """
    G = nx.Graph()
    G.add_nodes_from(np.arange(1, rows * cols + 1))

    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            if i < rows:
                G.add_edge(j + cols * (i - 1), j + cols * i)

            if j < cols:
                G.add_edge(j + cols * (i - 1), j + cols * (i - 1) + 1)

    graph = gerrychain.Graph(G)
    df = pd.DataFrame(graph.nodes)
    df.rename(columns={0: 'Name'}, inplace=True)
    df.set_index('Name', inplace=True)
    df['population'] = 1.
    graph.add_data(df)

    return graph


def draw_grid_plan(partition):
    """
    Prints a visual representation of the given partition
    of an r x r grid graph. 

    The input partition must be of a square grid graph. 

    TODO: Consider making this function and the build_grid_graph
    function of distances.py use the Grid class from gerrychain.grid. 
    """
    r = int(sqrt(partition.graph.number_of_nodes()))
    
    print('-', '----' * r, sep='')
    for i in range(r ** 2):
        index = i + 1
        row = i // r
        col = i % r

        print('| {0} '.format(partition.assignment[index]), end='')
        
        if col == r - 1:
            print('|\n-', '----' * r, sep='')


def pereira_index(p, q, property_name=None):
    """
    Given two Partition objects, 
    computes and returns the Tavares-Pereira et al. (2009)
    distance index. 

    If property_name is None, 
    then the edge weights delta_e are all 1. 
    Otherwise, 
    the given node property_name is used to compute
    the edge weights delta_e = min{p_i, p_j} 
    for each edge e = ij. 
    """
    if property_name is None:
        return pereira_index_unweighted(p, q)
    else:
        raise NotImplementedError()


def pereira_index_unweighted(p, q):
    """
    Given two Partition objects, 
    computes and returns the Tavares-Pereira et al. (2009)
    distance index (unweighted). 
    """
    num_disagree_edges = 0

    for e in p.graph.edges():
        x = min(e)
        y = max(e)
        px = p.assignment[x]
        qx = q.assignment[x]
        py = p.assignment[y]
        qy = q.assignment[y]

        num_disagree_edges += ((px == py and not(qx == qy)) or (not(px == py) and qx == qy))

    num_edges = p.graph.number_of_edges()
    assert(q.graph.number_of_edges() == num_edges) # Need to have same underlying graph
    
    return 1. / num_edges * (num_disagree_edges), num_disagree_edges, num_edges


def load_shapefile(shapefile_path):
    """
    Loads the shapefile at the given path,
    likely a zip folder, 
    to a GeoDataFrame using GeoPandas. 

    The shapefile must include a column with 'GEOID'
    to be used as the GeoDataFrame index. 

    Returns the GeoDataFrame with 'GEOID' set as the index. 
    """
    gdf = gpd.read_file(shapefile_path)
    return gdf.set_index('GEOID')


def build_district_plan(tracts_fname, assignment_fname, pop_fname=None, voteshares_fname=None):
    """
    Loads a sample Wisconsin district plan. 

    Parameters:
        tracts_fname: the name of the Wisconsin census tracts file (zipped shapefile)
        partition_fname: the name of the initial partition file (.csv)
        pop_fname: (optional) the name of the population data file (.csv)
        voteshares_fname: (optional) the name of the voteshares data file (.csv)

    Returns:
        the given Wisconsin district plan as a GerryChain Partition object
    """
    tracts_fname = tracts_fname if 'zip://' in tracts_fname else 'zip://' + tracts_fname
    gdf = load_shapefile(tracts_fname)
    gdf = add_population_data(gdf, pop_fname)
    gdf = add_voteshare_data(gdf, voteshares_fname)
    plan = build_partition(gdf, assignment_fname)
    return plan


def save_path_of_maps(path, fname='path_out.json'):
    """
    Saves the given path (list) of district maps to a file. 
    """
    path_dict = {}

    # Add initial map (set of units for each district)
    parts = path[0].partition.parts
    map_dict = {}
    for key in parts.keys():
        units = list(parts[key])
        map_dict[key] = units

    path_dict['initial_map'] = map_dict

    path_dict['flips'] = []
    for node in path:
        if node.flip is not None:
            path_dict['flips'].append(node.flip)

    with open(fname, 'w') as outfile:
        json.dump(path_dict, outfile)


def compute_feasible_flows(partition):
    """
    Given a Partition object, 
    computes feasible flow variable assignments 
    for the Shirabe flow constraints.
    (Helper function for the midpoint MIP warm-start.) 

    Returns f, an n-by-2m NumPy array 
    representing flow variable assignments, 
    where n is the number of nodes and 
    m is the number of undirected edges. 
    """
    n = partition.graph.number_of_nodes()
    m = partition.graph.number_of_edges()
    nodes = list(partition.graph.nodes())
    edges = list(partition.graph.edges())
    k = len(partition.parts)
    f = np.zeros((n, 2 * m)) # Flows are on directed edges, hence 2 * m

    for part in partition.parts:
        # The min unit is set as the center
        center = min(partition.parts[part])
        center_index = nodes.index(center)

        # Build a spanning tree of the part, and
        # label each node with its descendant count 
        # (treating center as root). 
        graph = partition.subgraphs[part]
        mst = nx.minimum_spanning_tree(graph)
        label_num_descendants(mst, center)

        # Set flow value of edge from parent to number of descendants
        stack = deque()
        stack.append(center)

        while stack:
            node = stack.pop()
            children = mst.nodes[node]['children']
            for child in children:
                stack.append(child)
                edge = (node, child)

                # Exact edge index depends on which directed version
                # of the edge has the flow
                if edge in edges:
                    edge_index = 2 * edges.index(edge)
                else:
                    edge_index = 2 * edges.index((edge[1], edge[0])) + 1

                f[center_index, edge_index] = mst.nodes[child]['num_descendants']

    return f


def label_num_descendants(tree, root):
    """
    Given a tree (Networkx Graph object)
    and its root, 
    label each node with its number of descendants, 
    including itself, 
    as a 'num_descendants' attribute. 
    """
    stack = deque()
    stack.append(root)

    postorder_stack = deque()

    for node in tree.nodes:
        tree.nodes[node]['visited'] = False # Use visited flags to avoid revisiting parents
        tree.nodes[node]['num_descendants'] = -1

    # In the first pass, determine parent-child relationships and
    # set num_descendants for leaves
    while stack:
        node = stack.pop()
        tree.nodes[node]['visited'] = True
        postorder_stack.append(node)
        
        children = []

        for neighbor in tree.neighbors(node):
            if not tree.nodes[neighbor]['visited']:
                stack.append(neighbor)
                children.append(neighbor)

        tree.nodes[node]['children'] = children

        if not children: # If children is empty, then node is a leaf
            tree.nodes[node]['num_descendants'] = 1

    # Use the post-order traversal to update num_descendants
    while postorder_stack:
        node = postorder_stack.pop()
        if tree.nodes[node]['num_descendants'] < 0:
            # Add up all num_descendants values of children, plus one to count node itself
            children_descendants = [tree.nodes[child]['num_descendants'] for child in tree.nodes[node]['children']]
            tree.nodes[node]['num_descendants'] = 1 + sum(children_descendants)
    return


# District plan metrics
def compute_SL_index(partition):
    """
    Input is a gerrychain.Partition object 
    with voteshare and population data. 

    It is assumed that `add_population_data` and 
    `add_voteshare_data` have been called on 
    the given partition's GeoDataFrame. 

    Returns the Sainte-Laguë Index of 
    the districting plan. 

    Reference: M. Gallagher. "Proportionality, 
    Disproportionality and Electoral Systems." 1991.
    """
    k = len(partition.parts)
    gop_vote_shares = [partition['gop_votes'][i] / (partition['gop_votes'][i] + partition['dem_votes'][i]) for i in range(1, k + 1)]
    print('\tGOP vote shares:', np.round(gop_vote_shares, decimals=4))
    gop_seat_share = sum((v >= 0.5) for v in gop_vote_shares) / k
    dem_seat_share = 1 - gop_seat_share
    
    gop_total_votes = sum(partition['gop_votes'][i] for i in range(1, k + 1))
    dem_total_votes = sum(partition['dem_votes'][i] for i in range(1, k + 1))
    gop_vote_share = gop_total_votes / (gop_total_votes + dem_total_votes)
    dem_vote_share = 1 - gop_vote_share
    
    return SL_helper(seat_shares_percent=[gop_seat_share, dem_seat_share], 
        vote_shares_percent=[gop_vote_share, dem_vote_share])


def SL_helper(seat_shares_percent, vote_shares_percent):
    """Computes the Sainte-Laguë Index given party seat-shares and 
    vote-shares as percentages.
    Reference: M. Gallagher. "Proportionality, Disproportionality 
        and Electoral Systems." 1991.
    """
    total = 0
    num_parties_seats = len(seat_shares_percent)
    num_parties_votes = len(vote_shares_percent)

    if num_parties_seats != num_parties_votes:
        raise InputError('Length of seat_shares_percent is {0}, but length of vote_shares_percent is {1}.'.format(num_parties_seats, m_parties_votes))
    for i in range(num_parties_seats):
        diff = seat_shares_percent[i] - vote_shares_percent[i]
        total += (diff ** 2 / vote_shares_percent[i])

    return total


def compute_efficiency_gap(partition):
    """
    Input is a gerrychain.Partition object 
    with voteshare and population data. 

    It is assumed that `add_population_data` and 
    `add_voteshare_data` have been called on 
    the given partition's GeoDataFrame. 

    Returns the efficiency gap of 
    the districting plan from the GOP perspective:
    (gop_wasted_votes - dem_wasted_votes) / total_votes.

    Reference: Stephanopoulos and McGhee. 
    "Partisan gerrymandering and the efficiency gap." 2015.
    """
    k = len(partition.parts)
    gop_wasted_votes = 0
    dem_wasted_votes = 0

    for i in range(1, k + 1):
        gop_votes = partition['gop_votes'][i]
        dem_votes = partition['dem_votes'][i]
        if gop_votes > dem_votes:
            gop_wasted_votes += gop_votes - 0.5 * (gop_votes + dem_votes)
            dem_wasted_votes += dem_votes
        else:
            gop_wasted_votes += gop_votes
            dem_wasted_votes += dem_votes - 0.5 * (gop_votes + dem_votes)

    # Using total population as a proxy for total_votes for simplicity
    total_votes = partition.graph.data.population.sum()
    return (gop_wasted_votes - dem_wasted_votes) / total_votes


def compute_mm_gap(partition):
    """
    Input is a gerrychain.Partition object 
    with voteshare and population data. 

    It is assumed that `add_population_data` and 
    `add_voteshare_data` have been called on 
    the given partition's GeoDataFrame. 

    Returns the mean-median gap of 
    the districting plan from the GOP perspective:
    gop_mean_voteshare - gop_median_voteshare.

    Reference: DeFord et al. 
    "Implementing partisan symmetry: Problems and paradoxes." 2020. 
    """
    k = len(partition.parts)
    gop_vote_shares = [partition['gop_votes'][i] / (partition['gop_votes'][i] + partition['dem_votes'][i]) for i in range(1, k + 1)]
    return np.mean(gop_vote_shares) - np.median(gop_vote_shares)


if __name__ == "__main__":
    tracts_fname = 'data/tl_2013_55_tract.zip'
    dem_assignment_fname = 'data/wi_gerrymander_dem.csv'
    gop_assignment_fname = 'data/wi_gerrymander_rep.csv'
    population_fname = 'data/wi_tract_populations_census_2010.csv'
    voteshares_fname = 'data/wi_voteshares.csv'

    dem_plan = build_district_plan(tracts_fname, dem_assignment_fname, population_fname, voteshares_fname)
    gop_plan = build_district_plan(tracts_fname, gop_assignment_fname, population_fname, voteshares_fname)

    # # Test GerryChain's built-in plot features (using matplotlib)
    # dem_plan.plot()
    # plt.axis('off')
    # plt.title('Democratic Party Gerrymander')
    # plt.show()

    # gop_plan.plot()
    # plt.axis('off')
    # plt.title('Republican Party Gerrymander')
    # plt.show()

    # Test alternate build_partition
    tracts_fname = tracts_fname if 'zip://' in tracts_fname else 'zip://' + tracts_fname
    gdf = load_shapefile(tracts_fname)
    gdf = add_population_data(gdf, population_fname)
    gdf = add_voteshare_data(gdf, voteshares_fname)
    plan = build_partition(gdf, assignment_dict={i: random.randint(1, 3) for i in gdf.index})

    plan.plot()
    plt.axis('off')
    plt.title('Randomly generated map built from assignment dictionary')
    plt.show()

    # TODO: add more tests
