# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 07:08:49 2023

@author: timon
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
# import requests
# from bs4 import BeautifulSoup
# import re
# requests==2.31.0
# beautifulsoup4==4.12.2
# selenium==4.10.0




#--- PROCESS DATA AREA ---
file_path = "230725-map.xlsx"
df = pd.read_excel(file_path, usecols=["Nummer","Bezugsdatum", "Bezirk", "Lat", "Lon", "Flaeche", "Zimmer", "Kosten", "Bild", "Link"])
df.columns = ["Nummer", "Bezugsdatum", "Bezirk", "lat", "lon", "Flaeche", "Zimmer", "Kosten", "Bild", "Link"]

file_path = "230725-Wohnungssuche-Wien.xlsx"
df2 = pd.read_excel(file_path, usecols=["Nummer","Bezugsdatum", "Bezirk", "Lat", "Lon", "Flaeche", "Zimmer", "Kosten", "Bild", "Link"])
df2.columns = ["Nummer", "Bezugsdatum", "Bezirk", "lat", "lon", "Flaeche", "Zimmer", "Kosten", "Bild", "Link"]


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

# Die Schleife zum Umformatieren der Spalte 'Datum'
for index, value in df['Bezugsdatum'].items():
    if value != 'sofort':
        df.at[index, 'Bezugsdatum'] = pd.to_datetime(value, format='%d.%m.%Y').strftime('%d.%m.')



# def extract_image_urls_from_website(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     image_tags = soup.find_all("img")
#     image_urls = [img.get("src") for img in image_tags]
#     return image_urls

# def extract_image_urls_from_website(url):
#     response = requests.get(url)
#     response.raise_for_status()

#     # Suche nach Bild-URLs im HTML-Code mit Hilfe von regulären Ausdrücken
#     image_urls = re.findall(r'<img .*?src="(.*?)"', response.text)

#     # Füge das Schema (http oder https) zu den Bild-URLs hinzu, falls es fehlt
#     base_url = response.url
#     image_urls = [url if url.startswith(("http://", "https://")) else f"{base_url}{url}" for url in image_urls]

    # return image_urls


#Darstellung der Bilder
def display_images_from_urls(df):
    
    for index, row in df.iterrows():
        
        nummer = row['Nummer']
        Link = row['Link']
        Bild = row['Bild']
        
        st.markdown(f"[{nummer}]({Link})")
        

        st.image(Bild)


        
        


#Einteilung in Gruppen nach Flaeche
conditions2 = [
    df['Flaeche'] < 0,
    (df['Flaeche'] > 0) & (df['Flaeche'] < 70),
    (df['Flaeche'] >= 70) & (df['Flaeche'] <= 90),
    df['Flaeche'] > 90
]
choices2 = [0, 1, 2, 3]
df['Group'] = np.select(conditions2, choices2)




#Einteilung in Gruppen nach Kosten
conditions3 = [
    df['Kosten'] < 100,
    (df['Kosten'] >= 100) & (df['Kosten'] < 1100),
    (df['Kosten'] >= 1100) & (df['Kosten'] < 1300),
    df['Kosten'] >= 1300
]
choices3 = [1, 2, 3, 4]
choices4 = ['rgb(0,128,0)','rgb(144,238,144) ','rgb(255,165,0)', 'rgb(255,255,255)']
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
    
    
    
    
# --- LOAD MAP ---    

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
    st.title('Die Wohnungen:')
    display_images_from_urls(df2)
    
  
    
#--- MAP SECTION ---"Bezugsdatum", "Bezirk", "lat", "lon", "Flaeche", "Zimmer", "Kosten"



st.title("Wohnungssuche in Wien")
st.write('Auf der Karte finden sich alle potenziellen Wohungen und deren Lage. Du kannst die Sidebar oben auf dem Pfeil öffnen um die einzelnen Wohnungen zu sehen. Folgende Filter kannst du setzen: Die Bezirke lassen sich filtern. Bezirk 99 sind die Ubahn Stationen. Die Farben zeigen die Preisgruppe (rot: 1300€+/ Orange: bis 1300€/ Türkis: bis 1100€), außerdem in Grün die Ubahn stationen. Diese werden nur angezeigt wenn du den slider "Wohnungsgröße" auf 0 verkleinerst. Die Linie steht im Feld "Zimmer"')

col1, col2 = st.columns([7,1])

with col2:
  
    st.write("Wohnungsfilter")
    
    # Erstelle eine Liste aller eindeutigen Bezirke
    bezirke = df.Bezirk.unique().tolist()
    # Füge die Option "All" am Anfang der Liste hinzu
    bezirke.insert(0, "All")
    
    industry_type = st.selectbox("Bezirk", bezirke)
    
    
    CH4_min, CH4_max = st.slider(
       "Wohnungsgröße", 0, 3, (1, 3), step=1, help="1: bis 70 qm < 2: bis 90 qm < 3: über 90 qm || Null sind die UBAHNEN"
   )

    
    st.write("Kartenanpassungen")
    
    size = st.slider(
    "Größe der Punkte", 0.5, 3.0, (2.0), step=0.5, help="Hier kannst du verstellen wie groß die Punkte dargestellt werden sollen."
)
    
    map_style = "carto-positron"
    #map_style=st.selectbox("Hintergrund", {"carto-positron", "open-street-map", "carto-darkmatter"})

    

with col1:
    
    #hover data sind die die angezeigt werden beim darüber fahren mit der maus
    hover_data = {'Nummer': False,
                  'Bezugsdatum': True,
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
        
        

    