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

# ---- SIDEBAR ----
with st.sidebar:
    option = st.selectbox(
        '¿Quieres alquilar o devolver una bicicleta?',
        ['Alquilar', 'Devolver']
    )

    # ALQUILAR OPTION
    if option == 'Alquilar':
        bike_type = st.multiselect(
            '¿Qué tipo de bicicletas quieres alquilar?',
            ['ICONIC', 'BOOST', 'FIT', 'EFIT']
        )
        st.header('¿Dónde te encuentras?')
        street = st.text_input('Calle')
        city = st.text_input('Ciudad', 'Barcelona')
        country = st.text_input('País', 'España')
        drive_selected = st.checkbox('Me dirijo hacia allí')

        # FIND BIKES BUTTON
        find_bikes_button = st.button('Buscar bicicletas', type='primary')
        if find_bikes_button:
            if street != "":
                actual_location = geocode(street + " " + city + " " + country)
                if actual_location == "":
                    st.subheader('Dirección no válida.')    
            else:
                st.subheader('Dirección no válida')
    # DEVOLVER OPTION
    elif option == 'Devolver':
        st.header('¿Dónde te encuentras?')
        street = st.text_input('Calle')
        city = st.text_input('Ciudad', 'Barcelona')
        country = st.text_input('País', 'España')

        # FIND DOCKS BUTTON
        find_docks_button = st.button('Buscar espacios', type='primary')
        if find_docks_button:
            if street != "":
                actual_location_return = geocode(street + " " + city + " " + country)
                if actual_location_return == "":
                    st.subheader('Dirección no válida')    
            else:
                st.subheader('Dirección no válida')
