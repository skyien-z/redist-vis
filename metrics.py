import pandas as pd
import geopandas
import json
import altair as alt

def make_metrics_df():
    GEOJSON = 'geojson/wi_map_plan_{}.geojson'
    mm_gaps = []
    sl_indices = []
    efficiency_gaps = []
    plan_number = [i for i in range(1,84)]
    for i in range(1,84):
        plan = geopandas.read_file(GEOJSON.format(i))
        mm_gaps.append(plan['mm_gap'].iloc[0])
        sl_indices.append(plan['SL_index'].iloc[0])
        efficiency_gaps.append(plan['efficiency_gap'].iloc[0])
    metrics_dict = {'plan_number':plan_number,'mm_gap':mm_gaps,'sl_index':sl_indices,'efficiency_gap':efficiency_gaps}
    metrics_df = pd.DataFrame(metrics_dict, columns = ['plan_number','mm_gap','sl_index','efficiency_gap']) 
    return metrics_df


def make_metrics_plot(metric_df, variable, variable_title, plot_title, scale):
    plot = alt.Chart(metric_df).mark_line(interpolate = 'basis').encode(
    alt.X('plan_number', title = "Plan Number"),
    alt.Y(variable, title = variable_title, scale = alt.Scale(domain = scale))).properties(
        title = plot_title,
        width = 300,
        height = 300
    )
    return plot