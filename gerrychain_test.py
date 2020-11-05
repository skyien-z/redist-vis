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

    metric_fn_names = ['compute_SL_index', 'compute_efficiency_gap', 'compute_mm_gap']

    dem_plan = helpers.build_district_plan(tracts_fname, dem_assignment_fname, population_fname, voteshares_fname)
    gop_plan = helpers.build_district_plan(tracts_fname, gop_assignment_fname, population_fname, voteshares_fname)

    # Test GerryChain's built-in plot features (using matplotlib)
    dem_plan.plot()
    plt.axis('off')
    plt.title('Democratic Party Gerrymander')
    plt.show()

    print('\n~~~ Dem. plan metrics ~~~')
    for fn_name in metric_fn_names:
        metric_fn = getattr(helpers, fn_name)
        metric_val = metric_fn(dem_plan)
        print('\t{0}: {1:.4f}'.format(fn_name, metric_val))

    gop_plan.plot()
    plt.axis('off')
    plt.title('Republican Party Gerrymander')
    plt.show()

    print('\n~~~ GOP plan metrics ~~~')
    for fn_name in metric_fn_names:
        metric_fn = getattr(helpers, fn_name)
        metric_val = metric_fn(gop_plan)
        print('\t{0}: {1:.4f}'.format(fn_name, metric_val))
