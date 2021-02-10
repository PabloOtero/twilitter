import os
import pathlib
#import re
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
#import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.title = 'Twilitter'

server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "output.csv"))
)


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



app.layout = html.Div(      
    id="root",
    children=[
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

        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P("Sentiment map of tweets. The warmer the color, the more positive the feeling.",
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
                    id="graph-container",
                    children=[             
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


def create_map(dff):
    fig = px.scatter_mapbox(dff, lat="lat", lon="lon", color="polarity",
        color_continuous_scale=px.colors.cyclical.IceFire, size_max=8, zoom=1,
        mapbox_style=mapbox_style, hover_data=["lat", "lon", "polarity"]) 

    fig.update_layout(
        paper_bgcolor = "#1f2630",
        font_color='#7FDBFF',
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        height= 300,
    ) 
    
    return fig
    
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
        selected_lats = []
        selected_lons = []
        for i in range(len(selected_points['points'])):
            selected_lats.append(float(selected_points['points'][i]['lat']))
            selected_lons.append(float(selected_points['points'][i]['lon']))
        dff = dff[ (dff['lat']>=min(selected_lats)) & \
                   (dff['lat']<=max(selected_lats)) & \
                   (dff['lon']>=min(selected_lons)) & \
                   (dff['lon']<=max(selected_lons)) ]

    date_start = pd.to_datetime(dff['created_at'].iloc[0]).strftime("%d %b %Y")
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

    
    return  fig


if __name__ == "__main__":
    app.run_server(debug=True)
