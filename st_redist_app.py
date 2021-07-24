import pandas as pd
import geopandas
import streamlit as st
import pydeck as pdk
import metrics

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
metric_type = st.sidebar.selectbox("What metrics would you like to see?",("Metrics for Plan " + str(district_slider),
"Overall Metrics"))
if metric_type == ("Metrics for Plan " + str(district_slider)):

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
elif metric_type == "Overall Metrics":
    # Cached since it takes quite a while to run the first time
    @st.cache
    def get_metric_df():
        return metrics.make_metrics_df()

    # Ranges are somewhat arbitrary 
    def make_sl_plot(metric_df):
        return metrics.make_metrics_plot(metric_df[['plan_number', 'sl_index']], "sl_index", 
        'Sainte-Lague Index', 'Sainte-Lague Indices by District Plan',(.2839,.28394))

    
    def make_mm_gap_plot(metric_df):
        return metrics.make_metrics_plot(metric_df[['plan_number', 'mm_gap']], 'mm_gap',
        'Mean-Median Gap', 'Mean-Median Gaps by District Plan',(-.0446,-.0456))

   
    def make_efficiency_gap_plot(metric_df):
        return metrics.make_metrics_plot(metric_df[['plan_number', 'efficiency_gap']],
        'efficiency_gap', 'Efficiency Gap', 'Eficiency Gaps by District Plan',(-.2778,-.28))

    metric_df = get_metric_df()
    st.sidebar.altair_chart(make_efficiency_gap_plot(metric_df))
    st.sidebar.altair_chart(make_mm_gap_plot(metric_df))
    st.sidebar.altair_chart(make_sl_plot(metric_df))


