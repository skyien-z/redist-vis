import pandas as pd
import geopandas
import streamlit as st
import matplotlib.pyplot as plt
from create_gdf import *
import pydeck as pdk
# import helpers

dem_assignment_fname = 'data/wi_gerrymander_dem.csv'
gop_assignment_fname = 'data/wi_gerrymander_rep.csv'
population_fname = 'data/wi_tract_populations_census_2010.csv'
voteshares_fname = 'data/wi_voteshares.csv'


# dem_plan = helpers.build_district_plan(tracts_fname, dem_assignment_fname, population_fname, voteshares_fname)
# gdf = dem_plan.graph.data


district_slider = st.slider('Select a district plan', 0, 83, 1)

#st.write(map_as_gdf, district_slider)

temp_gdf = geopandas.read_file('geojson/wi_map_plan_' + str(district_slider) + '.geojson')
temp_gdf.plot(column = 'district')
plt.axis('off')
st.pyplot(plt)

#st.map(map_as_gdf)

# st.pydeck_chart(pdk.Deck(
#      map_style='mapbox://styles/mapbox/light-v9',
#      layers=[
#         pdk.Layer(
#             "GeoJsonLayer",
#             data=map_as_gdf.district_plan_0,
#             get_position=['lon', 'lat'],
#
#         ),
#     ],
# ))
