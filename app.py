from utilities import *
import streamlit as st
import folium
from streamlit_folium import folium_static

# URLs with the bike stations data
station_url = "https://barcelona.publicbikesystem.net/customer/gbfs/v2/fr/station_status"
latlong_url = "https://barcelona.publicbikesystem.net/customer/gbfs/v2/fr/station_information"

st.title('Barcelona Bike Station Tracker')
st.markdown('Esta página muestra la disponibilidad de bicicletas de alquiler en Barcelona.')

# Dataframes with the pulled data
stations_data_df = query_station_status(station_url)
latlong_df = get_station_latlon(latlong_url)
data = join_latlon(stations_data_df, latlong_df)

# ---- METRICS ---- 
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label='Bicicletas Disponibles Ahora', value = sum(data['num_bikes_available']))
    st.metric(label='Estaciones con Bicicletas Disponibles', value = len(data[data['num_bikes_available'] > 0]))
with col2:    
    st.metric(label='Número de Espacios Disponibles', value = sum(data['num_docks_available']))
    st.metric(label='Estaciones con Espacios Disponibles', value = len(data[data['num_docks_available'] > 0]))
