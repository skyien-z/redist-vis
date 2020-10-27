import matplotlib.pyplot as plt

import gerrychain
import helpers

######################################################################
# 
# Test script for checking installation of required packages 
# for the redist-vis project
# 
# Author: Ian Ludden
# 
######################################################################

if __name__ == '__main__':
    tracts_fname = 'data/tl_2013_55_tract.zip'
    dem_assignment_fname = 'data/wi_gerrymander_dem.csv'
    gop_assignment_fname = 'data/wi_gerrymander_rep.csv'
    population_fname = 'data/wi_tract_populations_census_2010.csv'
    voteshares_fname = 'data/wi_voteshares.csv'

    dem_plan = helpers.build_district_plan(tracts_fname, dem_assignment_fname, population_fname, voteshares_fname)
    gop_plan = helpers.build_district_plan(tracts_fname, gop_assignment_fname, population_fname, voteshares_fname)

    # Test GerryChain's built-in plot features (using matplotlib)
    dem_plan.plot()
    plt.axis('off')
    plt.title('Democratic Party Gerrymander')
    plt.show()

    gop_plan.plot()
    plt.axis('off')
    plt.title('Republican Party Gerrymander')
    plt.show()
