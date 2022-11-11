import streamlit as st
import geopandas as gpd
import pandas as pd
import math

import plotly.graph_objects as go
TOKEN = "pk.eyJ1Ijoic2hhbm5vbm5ha2FtdXJhIiwiYSI6ImNrbG9zbG44OTB2d2Eyd20yc3FkYXVib3oifQ.Mck3r247wz8bgWvROUi_ww"
 
# constants
WOODBURY_LAT = 40.81206
WOODBURY_LON = -73.48622 
MINEOLA_LAT = 40.737398
MINEOLA_LON = -73.638756
SEAFORD_LAT = 40.66499
SEAFORD_LON = -73.49661

# read files
woodbury = gpd.read_file('WoodburyPD.geojson')
woodbury = woodbury.sort_values('radius', ascending=True)
mineola = gpd.read_file('MineolaPD.geojson')
mineola = mineola.sort_values('radius', ascending=True)
seaford = gpd.read_file('SeafordPD.geojson')
seaford = seaford.sort_values('radius', ascending=True)

pd_vehicle_df = pd.read_csv('vehicle_inventory.csv')
nassau_boundary = gpd.read_file('tl_2013_36059_roads.shp')
# st.write(nassau_boundary['geometry'].to_json())

def make_choropleth_traces(fig, boundaries: pd.DataFrame(), colorscale: str, lat: float, lon: float):
    fig.add_trace(
        go.Choroplethmapbox(
            geojson = eval(boundaries['geometry'].to_json()),
            locations = boundaries.index,
            text = boundaries['description'],
            z = boundaries['radius'],
            colorscale=colorscale, 
            zmin=boundaries['radius'].min()/2, 
            zmax=boundaries['radius'].max(),
            )
        )
    fig.update_traces(marker_opacity=0.2, 
                    #   hoverinfo='text',
                    hovertemplate=boundaries['description'].astype(str)+'<extra></extra>',
                    selector=dict(type='choroplethmapbox'))
    fig.add_trace(go.Scattermapbox(
        lon=[lon], lat=[lat],
        mode='markers',
        hovertemplate='Nassau County PD'+'<extra></extra>',
        marker_size=10,
        marker_color='white'
        )
                )
    return fig

def make_choropleth_map(boundaries: pd.DataFrame(), colorscale: str, lat: float, lon: float):
    fig = go.Figure()
    fig.add_trace(
        go.Choroplethmapbox(
            geojson = eval(boundaries['geometry'].to_json()),
            locations = boundaries.index,
            text = boundaries['description'],
            z = boundaries['radius'],
            colorscale=colorscale, 
            zmin=boundaries['radius'].min()/2, 
            zmax=boundaries['radius'].max(),
            )
        )
    fig.update_traces(marker_opacity=0.2, 
                    #   hoverinfo='text',
                    hovertemplate=boundaries['description'].astype(str)+'<extra></extra>',
                    selector=dict(type='choroplethmapbox')
                    )
    fig.add_trace(go.Scattermapbox(
        lon=[lon], lat=[lat],
        mode='markers',
        # hoverinfo='text',
        marker_size=10,
        marker_color='white'
        )
                )

    fig.update_layout(
        dict(mapbox = dict(
                accesstoken = TOKEN,
                center = dict(lon = lon, lat = lat),
                # pitch = 60,
                zoom = 11,
                style = 'dark',
                ),
            height = 600,
            width = 1200,
            margin = dict(t = 0, b = 0, l = 0, r = 0),
            legend_title_text = '<b> Distance in Miles </b>',
        )
    )
    return fig

def make_horizontal_bar(df: pd.DataFrame()):
    fig = go.Figure()
    df.sort_values('Electric Range', inplace=True)
    fig.add_trace(
        go.Bar(
        x=df["Electric Range"], 
        y=df["Model"], 
        orientation="h"
        )
                  )
    fig.update_layout(
        xaxis_title="Vehicle range (in miles)", 
        # yaxis_title="Vehicle model",
        margin = dict(t = 0, b = 0, l = 0, r = 0),
        height = 200,
        width = 1200
    )
    return fig

st.set_page_config(page_title='Charge4Fleets for non-fixed routes',page_icon="⚡️",layout='wide',initial_sidebar_state='auto',)

with st.sidebar:
    st.write(
    '''
    # Charge4Fleets &trade;
    Arup’s Charge4Fleets supports fleet electrification by assessing feasibility and strategy for future zero-emission operations. This sample website shows an isochrone-based approach to evaluate potential limitations with specified electric vehicles. 
    
    Contact [Arup](mailto:charge4fleets@arup.com) with any questions or read more about our work [here](https://www.arup.com/services/tools/charge4fleets). 
    '''
)

st.title('Fleet electrification for non-fixed route vehicles')
st.write('')
st.write('')
st.header('Vehicle assessment')
st.write('')

st.write('##### Sample vehicle ranges')
st.caption('The following electric vehicles have been utilized by police departments in US counties. This graph compares the range of each vehicle')
st.write('')
vehicle_fig = make_horizontal_bar(pd_vehicle_df)
st.plotly_chart(vehicle_fig)

st.write('')
st.write('')
st.write('##### Operational considerations')
st.caption('Select a vehicle from the list to assess how it may be used in operation. Select a minimum state of charge to reduce risk.')
st.write('')
model = st.selectbox('Select a vehicle', pd_vehicle_df['Model'])
SOC = st.slider('Minimum state of charge (%)', 0, 100, 20)
st.write('')
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col2:
    st.metric('Total vehicle range', str(pd_vehicle_df.loc[pd_vehicle_df['Model']==model, 'Electric Range'].iloc[0])+' miles')
with col3:
    st.metric('Round trips (10 miles one direction)', str(math.floor(pd_vehicle_df.loc[pd_vehicle_df['Model']==model, 'Electric Range']*((100-SOC)/100)/20))+' trips')

st.write('')
st.write('')
st.header('What area is accessible within a 10-mile radius?')
st.write('')

st.write('##### Police Precinct on Franklin')
st.caption('Analysis of Mineola location for Nassau County Police Department')
mineola_fig = make_choropleth_map(mineola, 'Reds', MINEOLA_LAT, MINEOLA_LON)
st.plotly_chart(mineola_fig)

st.write('##### 2nd Precinct Police Department')
st.caption('Analysis of Woodbury location for Nassau County Police Department')
woodbury_fig = make_choropleth_map(woodbury, 'Greens', WOODBURY_LAT, WOODBURY_LON)
st.plotly_chart(woodbury_fig)

st.write('##### 7th Precinct Police Department')
st.caption('Analysis of Seaford location for Nassau County Police Department')
seaford_fig = make_choropleth_map(seaford, 'Blues', SEAFORD_LAT, SEAFORD_LON)
st.plotly_chart(seaford_fig)

st.write('')
st.header('How may vehicles utilize a charging network across precincts?')
st.caption('Combined isochrone maps for Mineola, Woodbury, and Seaford locations.')
combined_fig = go.Figure()
combined_fig = make_choropleth_traces(combined_fig, mineola, 'Reds', MINEOLA_LAT, MINEOLA_LON)
combined_fig = make_choropleth_traces(combined_fig, woodbury, 'Greens', WOODBURY_LAT, WOODBURY_LON)
combined_fig = make_choropleth_traces(combined_fig, seaford, 'Blues', SEAFORD_LAT, SEAFORD_LON)

combined_fig.update_layout(
        dict(mapbox = dict(
                accesstoken = TOKEN,
                center = dict(lon = (MINEOLA_LON+ WOODBURY_LON+ SEAFORD_LON)/3,
                              lat = (MINEOLA_LAT+ WOODBURY_LAT+ SEAFORD_LAT)/3),
                # pitch = 60,
                zoom = 9,
                style = 'dark',
                # layers = dict(
                #     sourcetype = 'geojson',
                #     source = nassau_boundary,
                #     type = 'line'
                # )
                ),
            height = 600,
            width = 1200,
            showlegend= False,
            margin = dict(t = 0, b = 0, l = 0, r = 0),
            legend_title_text = '<b> Distance in Miles </b>',
            
        )
)
st.plotly_chart(combined_fig)
