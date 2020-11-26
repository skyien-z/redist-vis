import pandas as pd
import geopandas
import streamlit as st
import pydeck as pdk

st.title('Possible Wisconsin Districting Plans')

district_slider = st.slider('Select a district plan', 1, 83, 1)
current_gdf = geopandas.read_file('geojson/wi_map_plan_' + str(district_slider) + '.geojson')

INITIAL_VIEW_STATE = pdk.ViewState(latitude=44.155, longitude=-89.483492, zoom=6.3, max_zoom=16, pitch=45, bearing=0)

geojson = pdk.Layer(
    "GeoJsonLayer",
     data=current_gdf,
     pickable=True,
     auto_highlight=True,
     get_fill_color='[15 + district*30, 150, 120]',
     get_line_color='[255, 255, 255]',
)

r = pdk.Deck(layers=[geojson],
            initial_view_state=INITIAL_VIEW_STATE,
            mapbox_key='pk.eyJ1Ijoic2t5aWVuLXoiLCJhIjoiY2tnODJiaXRyMDl1OTJzbWtveTRsaGMwOSJ9.zFW9CBqmz3PAJ74FLRZRBA',
            tooltip={'text': 'District: {district}\nPopulation: {population}\nDem Votes: {dem_votes}\nGOP Votes: {gop_votes}'}
            )

st.pydeck_chart(r)

# Displays metrics on app sidebar
st.sidebar.subheader('Metrics for Plan ' + str(district_slider) + ":")
st.sidebar.text('SL Index: ' + str(current_gdf.loc[1]['SL_index']))
st.sidebar.text('Efficiency Gap: ' + str(current_gdf.loc[1]['efficiency_gap']))
st.sidebar.text('Mean-Median Gap: ' + str(current_gdf.loc[1]['mm_gap']))
st.sidebar.text('')

st.sidebar.text('Party Votes per District:')
votes_data_df = current_gdf.drop(columns=['district', 'population', 'dem_voteshare', 'gop_voteshare', 'geometry', 'SL_index', 'efficiency_gap', 'mm_gap'])
st.sidebar.line_chart(votes_data_df, 200, 200)

st.sidebar.text('\n Party Voteshare per District:')
voteshare_data_df = current_gdf.drop(columns=['district', 'population', 'dem_votes', 'gop_votes', 'geometry', 'SL_index', 'efficiency_gap', 'mm_gap'])
st.sidebar.line_chart(voteshare_data_df, 200, 200)
