# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 07:08:49 2023

@author: timon
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px




#--- PROCESS DATA AREA ---
file_path = "230725-Wohnungssuche-Wien.xlsx"
df = pd.read_excel(file_path, usecols=["Nummer","Bezugsdatum", "Bezirk", "Lat", "Lon", "Flaeche", "Zimmer", "Kosten"])
df.columns = ["Nummer", "Bezugsdatum", "Bezirk", "lat", "lon", "Flaeche", "Zimmer", "Kosten"]


#Hinzufügen der latlon
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
        if pd.isnull(row['lat']):
            district = row['Bezirk']
            latitude, longitude = get_lat_long_for_district(district)
            df.at[index, 'lat'] = latitude
            df.at[index, 'lon'] = longitude




#Einteilung in Gruppen nach Flaeche
conditions2 = [
    df['Flaeche'] < 50,
    (df['Flaeche'] >= 50) & (df['Flaeche'] < 70),
    (df['Flaeche'] >= 70) & (df['Flaeche'] <= 90),
    df['Flaeche'] > 90
]
choices2 = [0, 1, 2, 3]
df['Group'] = np.select(conditions2, choices2)




#Einteilung in Gruppen nach Kosten
conditions3 = [
    df['Kosten'] < 800,
    (df['Kosten'] >= 800) & (df['Kosten'] < 1100),
    (df['Kosten'] >= 1100) & (df['Kosten'] < 1300),
    df['Kosten'] >= 1300
]
choices3 = [1, 2, 3, 4]
choices4 = ['rgb(255,0,0)','rgb(255,165,0)','rgb(255,255,0)','rgb(0,128,0)']
df['Group_Points'] = np.select(conditions3, choices3)
df['Colour'] = np.select(conditions3, choices4)





def set_size_based_on_capacity(input_df, size):
    #Zuordnung der size
    conditions = [
        input_df['Group'] < 2,
        input_df['Group'] == 2,
        input_df['Group'] > 2
    ]
    choices = [(size), (size*3), (size*6)]
    input_df['size'] = np.select(conditions, choices)
    return input_df
    
    
    
    

def load_map(input_df, size, map_style):
    #input_df['size'] = 5
    result_df = set_size_based_on_capacity(input_df, size)
    
    if not result_df.empty:
        fig = px.scatter_mapbox(
            input_df,
            lat="lat",
            lon="lon",
            #mapbox_style="stamen-terrain",
            mapbox_style=map_style,
            color="Colour",  # Farbinformation aus dem DataFrame verwenden
            color_discrete_map={
                "rgb(255,0,0)": "rgb(255,0,0)",      # Rot
                "rgb(255,165,0)": "rgb(255,165,0)",  # Orange
                "rgb(255,255,0)": "rgb(255,255,0)",  # Gelb
                "rgb(0,128,0)": "rgb(0,128,0)" },     # Grün
            size="size",
            size_max=size*6,
            zoom=10,
            height=1000,
            hover_data=hover_data,
            hover_name="Nummer",
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("Sorry, no data to display. Please adjust your filters.")



### __________________________________________________________________________________________________________________________________________
### STREAMLIT

#--- SETUP WEBSITE CONFIG ---
st.set_page_config(page_title="Wohnungssuche Alina und Timon in Wien", page_icon=":derelict_house:", layout="wide" , initial_sidebar_state = "collapsed" )

    


#--- MAP FILTER ---
with st.sidebar:
    
    st.title("Wohnungsfilter")
    
    # Erstelle eine Liste aller eindeutigen Bezirke
    bezirke = df.Bezirk.unique().tolist()
    # Füge die Option "All" am Anfang der Liste hinzu
    bezirke.insert(0, "All")
    
    industry_type = st.selectbox("Bezirk", bezirke)
    
    
    CH4_min, CH4_max = st.slider(
       "Wohnungsgröße", 0, 3, (1, 3), step=1, help="0: unter 50 qm < 1: bis 70 qm < 2: bis 90 qm < 3: über 90 qm"
   )

    
    st.title("Kartenanpassungen")
    
    size = st.slider(
    "Größe der Punkte", 0.5, 3.0, (2.0), step=0.5, help="Hier kannst du verstellen wie groß die Punkte dargestellt werden sollen."
)
    
    map_style=st.selectbox("Background Mapstyle", {"carto-positron", "open-street-map", "carto-darkmatter"})

    

    
#--- MAP SECTION ---"Bezugsdatum", "Bezirk", "lat", "lon", "Flaeche", "Zimmer", "Kosten"

with st.container():
    st.title("Wohnungssuche in Wien")
    st.write('Auf der Karte finden sich alle potenziellen Wohungen und deren Lage. Falls du nichts siehst, ändere den Background Kartenstil in der Sidebar ganz unten zu carto-darkmatte. Die Bezirke lassen sich filtern. Die Farben zeigen die Preisgruppe und die Größe der Punkte die gesamtfläche.')
    
    #hover data sind die die angezeigt werden beim darüber fahren mit der maus
    hover_data = {'Nummer': False
                  'Bezugsdatum': False,
                  'Bezirk' : False,
                  'lat': False,
                  'lon': False,
                  'Flaeche': True,
                  'Zimmer': True,
                  'Kosten': True,
                  'size' : False,
                  'Colour': False
            }
    
    
    df_mima = df.query("`Group` >= @CH4_min and `Group` <= @CH4_max")
    
    if industry_type == "All":
        load_map(df_mima, size, map_style)
    else:
        df1 = df_mima.query("Bezirk == @industry_type")
        load_map(df1, size, map_style)