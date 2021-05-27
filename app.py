"""
Twilitter Dash App

@author: pablo.otero@ieo.es

Last version: May 2021
"""

import os
import pathlib
import plotly.express as px
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_daq as daq
import networkx as nx


# Initialize app
app = dash.Dash(
    __name__, suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]   
)
app.title = 'Twilitter'
server = app.server


# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# df = pd.read_csv(
#     os.path.join(APP_PATH, os.path.join("data", "output.csv"))
# )

# Read from public url in Google drive
url = 'https://drive.google.com/file/d/1LTJOExzF6aWREh_0AFLWloDN97LNE-nX/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
df = pd.read_csv(path)


df = df.loc[(df['lat'] > -89) & (df['lat'] < 89) & (df['lon'] > -179) & (df['lon'] < 179)]
df.loc[df.city_from_profile == 'City of Westminster', 'city_from_profile'] = "London"

#mapbox_token hidden in file
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"
px.set_mapbox_access_token(open(os.path.join(APP_PATH, 'mapbox_token')).read())


# Plot time series once
df2 = (pd.to_datetime(df['created_at']).dt.floor('d').value_counts().rename_axis('date').reset_index(name='count'))
df2 = df2.sort_values('date')
index = pd.DatetimeIndex(df2['date']) 
fig2 = px.area(df2, x='date', y='count', color_discrete_sequence =['#7FDBFF']*len(df2), 
               labels={
                     "date": "Time",
                     "count": "Tweet volume",
                 },
               )
fig2.update_xaxes(rangeslider_visible=True)
fig2_layout = fig2["layout"]
fig2_layout["paper_bgcolor"] = "#1f2630"
fig2_layout["plot_bgcolor"] = "#1f2630"
fig2_layout["font"]["color"] = "#7FDBFF"
fig2_layout["xaxis"]["tickfont"]["color"] = "#7FDBFF"
fig2_layout["yaxis"]["tickfont"]["color"] = "#7FDBFF"
fig2_layout["xaxis"]["gridcolor"] = "#5b5b5b"
fig2_layout["yaxis"]["gridcolor"] = "#5b5b5b"     


tabs_styles = {
    'height': '44px',
    'fontSize': '18px',
}
tab_style = {
    'padding': '6px',
    'fontWeight': 'bold',
}
tab_selected_style = {
    'backgroundColor': "#7FDBFF",
    'color': 'white',
    'padding': '6px'
}

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": "#1f2630", "plot_bgcolor": "#1f2630"}}

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


div_tab1 = html.Div(      
    id="root",
    children=[


        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P("Map of tweets' volume.",
                                    id="heatmap-title",
                                ),
                                html.P("Use the box select tool to make a subset.",
                                    id="heatmap-title2",
                                ),
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=[
                                        dcc.Graph(id="county-choropleth")
            
                                    ]
                                )                                                  
                            ],
                        ),
                        html.Div(
                            id="time-series-container",
                            children=[                                                
                                    html.P("Number of tweets over time. ",
                                        id="time-series-title",
                                    ),
                                    html.P("Use the bottom selector to adjust the dates.",
                                        id="time-series-title2",
                                    ),                               
                                dcc.Graph(
                                    id='time-series',                          
                                    figure = fig2,
                                    style={
                                        'bgcolor': "#1f2630",
                                    }                             
                                ),
                                html.Div(id='output-container-range-slider'),
                            ],
                        ),
                    ],
                ),                
                html.Div(
                    [
                        html.Div(
                            id="indicator",
                            className="six columns pretty_container",
                            children=[
                                html.P(
                                    [
                                        "Number of Tweets with location",                                     
                                    ],
                                    className="container_title",
                                ),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="indicator-graph",
                                        figure=blank_fig(row_heights[0]),
                                        config={"displayModeBar": False},
                                    ),
                                    className="svg-container",
                                    style={"height": 150},
                                ),
                            ],                         
                        ),
                        html.Div(
                            id="indicator2",
                            className="six columns pretty_container",
                            children=[
                                html.P(
                                    [
                                        "Sentiment score",                                     
                                    ],
                                    className="container_title",
                                ),
                                daq.GraduatedBar(
                                        id='my-graduated-bar',
                                        color={"gradient":True,"ranges":{"red":[0,3.5],"yellow":[3.5,6.5],"green":[6.5,10]}},
                                        showCurrentValue=False,
                                        label=" <--Negative | Positive -->",
                                        value=6
                                    ),
                            ],                         
                        ),                       
                        html.Div(
                            id="graph-container2",
                            children=[
                                html.P(id="chart-selector", children="Select chart:"),
                                dcc.Dropdown(
                                    id="chart-dropdown",
                                    options=[
                                        {
                                            "label": "Most frequent hashtags",
                                            "value": "hashtags",
                                        },
                                        {
                                            "label": "Most successful users (favorites + retweets)",
                                            "value": "engagement",
                                        },
                                        {
                                            "label": "Most mentioned users",
                                            "value": "mentions",
                                        },
                                        {
                                            "label": "Top cities",
                                            "value": "cities",
                                        },
                                        {
                                            "label": "Top countries",
                                            "value": "countries",
                                        },                                
                                    ],
                                    value="hashtags"                           
                                ),
                                dcc.Loading(
                                    id="loading-2",
                                    type="default",
                                    children=[
                                        dcc.Graph(id="selected-data")
                                    ]
                                )
                            ],
                        ),                     
                        html.Div(
                            id="description3",
                            children=[
                                dcc.Markdown('''
                                             
                                             
                                By [@PabloOteroT](https://twitter.com/PabloOteroT) 
                                inspired in the [Dash opioid epidemic example](https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-opioid-epidemic).
                                This app is part of the work of [Instituto Español de Oceanografía](http://www.ieo.es/) in the
                                [CleanAtlantic - Tackling Marine Litter in the Atlantic Area](http://www.cleanatlantic.eu/) project. This app 
                                only reflects the author´s view, thus the Atlantic Area Programme authorities are not liable for any use that may be made of the
                                information contained therein.
                                
                        
                                ''')
                            ],
                        ),
                    ],
                ),
                              
            ],
        ),             
])


                                      
# Scatter plot map with sentiments                                             
# def create_map(dff):
#     fig = px.scatter_mapbox(dff, lat="lat", lon="lon", color="polarity",
#         color_continuous_scale=px.colors.cyclical.IceFire, size_max=8, zoom=1,
#         mapbox_style=mapbox_style, hover_data=["lat", "lon", "polarity"]) 

#     fig.update_layout(
#         paper_bgcolor = "#1f2630",
#         font_color='#7FDBFF',
#         hovermode="closest",
#         margin=dict(r=0, l=0, t=0, b=0),
#         height= 300,
#     ) 
    
#     return fig


def create_map(dff):
    fig = ff.create_hexbin_mapbox(data_frame=dff, lat="lat", lon="lon", 
                                  nx_hexagon=100, opacity=0.5, 
                                  labels={"color": "Tweet Count"}, 
                                  color_continuous_scale="Viridis",
                                  mapbox_style="carto-positron",
                                  min_count=1) 

    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    
    return fig


def load_network():
     
    G = nx.read_edgelist("./data/tweets.edgelist")
    
    pos = nx.spring_layout(G, k=2)
    
    # edges trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(color="#7FDBFF", width=1),
        hoverinfo='none',
        showlegend=False,
        mode='lines')

    # nodes trace
    node_x = []
    node_y = []
    text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y, text=text,
        mode='markers',
        showlegend=False,
        hoverinfo='text',
        marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='YlOrRd',
                reversescale=False,
                color=[],
                size=15,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right',
                    bgcolor='white',
                ),
                line_width=2))
    
    # color marker by adjacency
    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))   
    node_trace.marker.color = node_adjacencies
  
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Top-100 word bigrams of the overall period.',
                height=700,
                titlefont_size=16,
                titlefont_color="#d6a622",
                plot_bgcolor="#1f2630",
                paper_bgcolor="#1f2630",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)),
                )
    
    return fig


app.layout = html.Div([
    html.Div(
        id="header",
        children=[
            html.Img(id="logo", src=app.get_asset_url("ieo.svg")),
            html.H4(children="Twilitter"),
            html.P(
                id="description",
                children="Tweets containing words 'plastic' or 'microplastic' in combination with any \
                of these words: 'coast[s]', 'beach[es]', 'marine', 'ocean[s]'. Following languages have been \
                taken into consideration: English, Japanese, Spanish, Portuguese, French, Italian, Malaysian, \
                German, Turkish, Thai, Korean and Indi. The dataset has undergone pre-processing to eliminate \
                as far as possible unrelated tweets. In this visualization, the bots have not been eliminated \
                so caution must be exercised in the interpretation. These data can be helpful to assess the impact \
                of NGOs, international organizations and academic institutions that wish to play a relevant role \
                in the fight against marine pollution by plastics, environmental awareness and scientific dissemination.",
            ),
            html.P(
                id="description2",
                children="To learn more and cite: Otero, P., J. Gago, P. Quintás, 2021. Twitter data analysis \
                to assess the interest of citizens on the  impact of marine plastic pollution. Submitted.",
            ),                    
        ],
    ),   
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Volume analysis', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Graph network', value='tab-2', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-example-content')
])


@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return div_tab1
    elif tab == 'tab-2':
        return html.Div(      
            children=[
                dcc.Graph(figure=load_network())         
            ]
        )

    
@app.callback(
    Output('county-choropleth', 'figure'),
    [Input('time-series', 'relayoutData')]
)    
def update_map_with_dates(relayoutData):
    if relayoutData is None:
        return(create_map(df))            
    elif 'xaxis.range' in relayoutData:        
        time_converted = pd.to_datetime(df['created_at'])
        dff = df[(time_converted > relayoutData['xaxis.range'][0]) & (time_converted < relayoutData['xaxis.range'][1])]
        return(create_map(dff))  
    else:       
        return(create_map(df))       
    

def sort_hashtags(dff):
        l = list(dff['hashtags'].dropna())
        flat_list = []
        for sublist in l:
            for item in sublist.replace(' ','').split(','):
                flat_list.append(item)
        
        hashtag_dict = {}
        for match in flat_list:
            if match not in hashtag_dict.keys():
                hashtag_dict[match] = 1
            else:
                hashtag_dict[match] = hashtag_dict[match]+1
        
        #Making a list of the most used hashtags and their values
        hashtag_ordered_list =sorted(hashtag_dict.items(), key=lambda x:x[1])
        hashtag_ordered_list = hashtag_ordered_list[::-1]
        #Separating the hashtags and their values into two different lists
        hashtag_ordered_values = []
        hashtag_ordered_keys = []
        #Pick the 25 most used hashtags to plot
        for item in hashtag_ordered_list[0:20]:
            hashtag_ordered_keys.append('#' + item[0])
            hashtag_ordered_values.append(item[1])
        
        df2 = pd.DataFrame(hashtag_ordered_keys)
        df2['hashtag_ordered_keys'] = hashtag_ordered_keys
        df2['hashtag_ordered_values'] = hashtag_ordered_values
        
        return df2


def sort_mentions(dff):
        l = list(dff['user_mentions'].dropna())
        flat_list = []
        for sublist in l:
            for item in sublist.replace(' ','').split(','):
                flat_list.append(item)
        
        mentions_dict = {}
        for match in flat_list:
            if match not in mentions_dict.keys():
                mentions_dict[match] = 1
            else:
                mentions_dict[match] = mentions_dict[match]+1
        
        #Making a list of the most user mentions
        mentions_ordered_list =sorted(mentions_dict.items(), key=lambda x:x[1])
        mentions_ordered_list = mentions_ordered_list[::-1]
        #Separating the hashtags and their values into two different lists
        mentions_ordered_values = []
        mentions_ordered_keys = []
        #Pick the 25 most used hashtags to plot
        for item in mentions_ordered_list[0:20]:
            mentions_ordered_keys.append('@' + item[0])
            mentions_ordered_values.append(item[1])
        
        df3 = pd.DataFrame(mentions_ordered_keys)
        df3['mentions_ordered_keys'] = mentions_ordered_keys
        df3['mentions_ordered_values'] = mentions_ordered_values
        
        return df3



@app.callback(
    #Output("time-series-title", "children"),
    Output("indicator-graph", "figure"),
    Output("my-graduated-bar", "value"),
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("time-series", "relayoutData"),
    ],
)
def display_selected_data(selected_points, chart_dropdown, relayoutData):
    
   
    if relayoutData is None:  
        dff=df
    else:
        if 'xaxis.range' in relayoutData:
            time_converted = pd.to_datetime(df['created_at'])
            dff = df[(time_converted > relayoutData['xaxis.range'][0]) & (time_converted < relayoutData['xaxis.range'][1])]         
        else:
            dff=df
       
    if selected_points is not None:
        # This works with scatter plot
        # selected_lats = []
        # selected_lons = []
        # for i in range(len(selected_points['points'])):
        #     selected_lats.append(float(selected_points['points'][i]['lat']))
        #     selected_lons.append(float(selected_points['points'][i]['lon']))
        # dff = dff[ (dff['lat']>=min(selected_lats)) & \
        #            (dff['lat']<=max(selected_lats)) & \
        #            (dff['lon']>=min(selected_lons)) & \
        #            (dff['lon']<=max(selected_lons)) ]
        try:
            coords = selected_points['range']['mapbox']
            min_lat = min([float(item[1]) for item in coords])
            max_lat = max([float(item[1]) for item in coords])
            min_lon = min([float(item[0]) for item in coords])
            max_lon = max([float(item[0]) for item in coords])
            dff = dff[ (dff['lat']>=min_lat) & \
                       (dff['lat']<=max_lat) & \
                       (dff['lon']>=min_lon) & \
                       (dff['lon']<=max_lon) ]
            update_map_with_dates(relayoutData)
        except:
            pass
     
    try:
        date_start = pd.to_datetime(dff['created_at'].min()).strftime("%d %b %Y")
    except:
        date_start = pd.to_datetime(dff['created_at'].iloc[0]).strftime("%d %b %Y")
    try:
        date_end   = pd.to_datetime(dff['created_at'].max()).strftime("%d %b %Y")
    except:
        date_end   = pd.to_datetime(dff['created_at'].iloc[-1]).strftime("%d %b %Y") 
    

    if chart_dropdown == "hashtags": 
        title='Most used hashtags<br>from {0} '.format(date_start) + 'to {0} '.format(date_end)        
        fig = px.bar(sort_hashtags(dff), x="hashtag_ordered_keys", y='hashtag_ordered_values', \
                     title=title, color_discrete_sequence =['#7FDBFF']*len(dff),
                     labels={
                     "hashtag_ordered_keys": "Top hashtags",
                     "hashtag_ordered_values": "Frequency",
                     },
        )            
    elif chart_dropdown == "engagement":
        dff_engagement = dff[['original_author', 'engagement']]
        dff_engagement = dff_engagement.groupby(by=['original_author'], as_index=False).sum()
        dff_engagement = dff_engagement.sort_values('engagement', ascending=False)[:20]
        dff_engagement['original_author'] = ['@' + element for element in dff_engagement.original_author]

        title='Users with more engagement<br>from {0} '.format(date_start) + 'to {0} '.format(date_end)
        fig = px.bar(dff_engagement, x="original_author", y='engagement', \
                     title=title, color_discrete_sequence =['#7FDBFF']*len(dff_engagement),
                     labels={
                     "original_author": "User name",
                     "engagement": "Engagement",
                     },
        )               
    elif chart_dropdown == "mentions":
        title='Most mentioned users<br>from {0} '.format(date_start) + 'to {0} '.format(date_end)        

        fig = px.bar(sort_mentions(dff), x="mentions_ordered_keys", y='mentions_ordered_values', \
                     title=title, color_discrete_sequence =['#7FDBFF']*len(dff),
                     labels={
                     "mentions_ordered_keys": "User name",
                     "mentions_ordered_values": "Mentions",
                     },
        )
    elif chart_dropdown == "cities":
        dff_cities = dff[['city_from_profile']].dropna()
        dff_cities = dff_cities['city_from_profile'].value_counts()
        dff_cities=dff_cities[:20]
        title='Cities with more tweets<br>from {0} '.format(date_start) + 'to {0} '.format(date_end)        

        fig = px.bar(dff_cities, x=dff_cities.index, y='city_from_profile', \
                     title=title, color_discrete_sequence =['#7FDBFF']*len(dff_cities),
                     labels={
                     "x": "Top cities",
                     "city_from_profile": "Tweet volume from city",
                     },
        )
    else:
        dff_countries = dff[['country_from_profile']].dropna()
        dff_countries = dff_countries['country_from_profile'].value_counts()
        dff_countries=dff_countries[:20]
        title='Countries with more tweets<br>from {0} '.format(date_start) + 'to {0} '.format(date_end)        
        
        fig = px.bar(dff_countries, x=dff_countries.index, y='country_from_profile', \
                     title=title, color_discrete_sequence =['#7FDBFF']*len(dff_countries),
                     labels={
                     "x": "Top countries",
                     "country_from_profile": "Tweet volume from country",
                     },
        )
               

    fig_layout = fig["layout"]
    fig_layout["hovermode"] = "closest"
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#7FDBFF"
    fig_layout["xaxis"]["tickfont"]["color"] = "#7FDBFF"
    fig_layout["yaxis"]["tickfont"]["color"] = "#7FDBFF"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b" 
    fig_layout["margin"]["t"] = 75
    fig_layout["margin"]["r"] = 50
    fig_layout["margin"]["b"] = 100
    fig_layout["margin"]["l"] = 50       


    n_selected=len(dff)
    
    # Build indicator figure
    n_selected_indicator = {
        "data": [
            {
                "type": "indicator",
                "value": n_selected,
                "number": {"font": {"color": "#7FDBFF"}},
            }
        ],
        "layout": {
            "template": template,
            "height": 50,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
        },
    }
    
    sentiment_mean=dff['polarity'].mean()
    
    #From [-1, 1] to [0, 10] range
    sentiment_mean=(sentiment_mean+1)*5

    return  (
        n_selected_indicator,
        sentiment_mean,
        fig,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
