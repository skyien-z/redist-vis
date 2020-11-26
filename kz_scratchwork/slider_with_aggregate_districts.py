import pandas as pd
import geopandas
import streamlit as st
import pydeck as pdk

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
