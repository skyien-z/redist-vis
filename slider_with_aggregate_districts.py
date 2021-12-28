import pandas as pd
import geopandas
import streamlit as st
import pydeck as pdk
import altair as alt
import metrics

st.title('Possible Wisconsin Districting Plans')

# This section encodes the slider and map

district_slider = st.slider('Select a district plan', 1, 83, 1)
current_gdf = geopandas.read_file('geojson/wi_map_plan_' + str(district_slider) + '.geojson')

INITIAL_VIEW_STATE = pdk.ViewState(latitude=44.8, longitude=-89.483492, zoom=5.4, max_zoom=16, pitch=0, bearing=0)

current_gdf['color'] = [[80, 80, 80],[100, 149, 237],[153, 50, 204],[210,105,30],[154,205,50],[255, 160, 122],[25,50,100],[0,255,255],[255,255,0]]
current_gdf['dem_votes'] = current_gdf['dem_votes'].astype(int)
current_gdf['gop_votes'] = current_gdf['gop_votes'].astype(int)

geojson = pdk.Layer(
    "GeoJsonLayer",
     data=current_gdf,
     pickable=True,
     auto_highlight=True,
     get_fill_color='color',
     get_line_color='[255, 255, 255]'
)

r = pdk.Deck(layers=[geojson],
            initial_view_state=INITIAL_VIEW_STATE,
            api_keys={"mapbox": 'pk.eyJ1Ijoic2t5aWVuLXoiLCJhIjoiY2tnODJiaXRyMDl1OTJzbWtveTRsaGMwOSJ9.zFW9CBqmz3PAJ74FLRZRBA'},
            tooltip={'text': 'District: {district}\nPopulation: {population}\nDem Votes: {dem_votes}\nGOP Votes: {gop_votes}'}
            )

st.pydeck_chart(r)

#Displays metrics on app sidebar

st.sidebar.subheader('Metrics for Plan ' + str(district_slider) + ":")

metric_descriptions = [ 'SL Index: ' + str(round(current_gdf.loc[1]['SL_index'], 7)),
                        'Efficiency Gap: ' + str(round(current_gdf.loc[1]['efficiency_gap'], 7)),
                        'Mean-Median Gap: ' + str(round(current_gdf.loc[1]['mm_gap'], 7))]

st.sidebar.text('')

# This section encodes the metric graphs
metric_gdf_column_names = ['SL_index', 'efficiency_gap', 'mm_gap']
y_column_names = ['Sainte-Lague Index', 'Efficiency Gap', 'Mean-Median Gap']
plot_title_names = ["Sainte-Lague Indices by District Plan", "Efficiency Gaps by District Plan", "Mean-Median Gaps By District Plan"]
metric_scaling = [(.2839,.28394), (-.277,-.28), (-.04445,-.0457)]
metrics_df = pd.read_json('geojson/all_plan_metrics')
current_metric_df = pd.DataFrame(metrics_df.loc[district_slider]).transpose()

for i in range(0, 3):
    st.sidebar.text(metric_descriptions[i])
    altair_metric_chart = alt.Chart(metrics_df).mark_line().encode(
        alt.X('plan', title = "Plan Number"),
        alt.Y(metric_gdf_column_names[i], title = y_column_names[i], scale = alt.Scale(domain = metric_scaling[i]))).properties(
            title = plot_title_names[i],
            width = 300,
            height = 300
        )

    highlighted_plan_points = alt.Chart(current_metric_df).mark_point(filled=True, size=100).encode(
        alt.X('plan'),
        alt.Y(metric_gdf_column_names[i]),

    color=alt.value('yellow')
    )

    st.sidebar.write(altair_metric_chart + highlighted_plan_points)

st.sidebar.text('Party Votes per District:')
votes_data_df = current_gdf.drop(columns=['color', 'district', 'population', 'dem_voteshare', 'gop_voteshare',
'geometry', 'SL_index', 'efficiency_gap', 'mm_gap'])
st.sidebar.line_chart(votes_data_df, 200, 200)

st.sidebar.text('\n Party Voteshare per District:')
voteshare_data_df = current_gdf.drop(columns=['color', 'district', 'population', 'dem_votes', 'gop_votes',
                                            'geometry', 'SL_index', 'efficiency_gap', 'mm_gap'])
st.sidebar.line_chart(voteshare_data_df, 200, 200)
