# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 20:13:02 2023

@author: timon
"""

import streamlit as st
import pandas as pd
import plotly.express as px


#--- PROCESS DATA AREA ---
file_path = "230725-Wohnungssuche-Wien.xlsx"

df = pd.read_excel(file_path)


def get_lat_long_for_district(district):
    district_coordinates = {
        1: (48.2092, 16.3700),
        2: (48.2200, 16.3704),
        3: (48.2155, 16.3803),
        4: (48.2027, 16.3771),
        5: (48.1883, 16.3599),
        6: (48.1852, 16.3290),
        7: (48.1995, 16.3490),
        8: (48.2005, 16.3754),
        9: (48.2085, 16.3510),
        10: (48.1869, 16.3563),
        11: (48.1783, 16.3125),
        12: (48.1751, 16.3007),
        13: (48.1768, 16.3229),
        14: (48.1851, 16.3285),
        15: (48.1753, 16.3454),
        16: (48.2262, 16.3057),
        17: (48.2353, 16.3283),
        18: (48.2261, 16.3352),
        19: (48.2343, 16.3570)
    }

    return district_coordinates.get(district, "Ungültiger Bezirk")


for index, row in df.iterrows():
        if pd.isnull(row['Lat']):
            district = row['Bezirk']
            latitude, longitude = get_lat_long_for_district(district)
            df.at[index, 'Lat'] = latitude
            df.at[index, 'Lon'] = longitude


### __________________________________________________________________________________________________________________________________________
### STREAMLIT

#--- SETUP WEBSITE CONFIG ---
st.set_page_config(page_title="Wohnungssuche-Alina-Timon", layout="wide")


with st.sidebar:
    st.title("Wohnungen")

    st.markdown("Diese Karte zeigt die Lage der Wohnungen in Wien.")






#hover data sind die die angezeigt werden beim darüber fahren mit der maus
hover_data = {'Link': False,
              'Bezugsdatum' : True,
              'Bezirk' : True  ,
              'Lat': True,
              'Lon': True,
              'Flaeche' : False,
              'Zimmer': False,
              'Kosten': True
              }


df['size'] = 20

if not df.empty:
    fig = px.scatter_mapbox(
        df,
        lat="Lat",
        lon="Lon",
        mapbox_style="carto-darkmatter",
        #color="Kosten",
        #color_continuous_scale= [[0, color_custom], [1, 'white']], #[[0, '#00441b'], [0.5, '#72c375'], [1, 'white']],
        #color_continuous_scale= [[0, '#00441b'], [0.5, '#72c375'], [1, 'white']],
        size="Flaeche",
        #size_max=size,
        #zoom=5,
        #height=700,
        )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Sorry, no data to display. Please adjust your filters.")






