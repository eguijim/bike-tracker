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

# ---- CITY MAP ----
if option == 'Alquilar' and find_bikes_button == False:
    show_initial_map(data)

if option == 'Devolver' and find_docks_button == False:
    show_initial_map(data)

# ---- SHOW USER INPUT RESULTS ----

# "Alquilar" Option Map (Bikes)
if option == 'Alquilar':
    if find_bikes_button:
        if street != "":
            actual_location = geocode(street + " " + city + " " + country)
            if actual_location != "":
                selected_station = get_bike_availability(actual_location, data, bike_type)
                center = actual_location
                m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')
                for _, row in data.iterrows():
                    marker_color = get_marker_color(row['num_bikes_available']) 
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=2,
                        color=marker_color,
                        fill=True,
                        fill_color=marker_color,
                        fill_opacity=0.7,
                        popup=folium.Popup(f"Estación ID: {row['station_id']}<br>"
                                            f"Total Bicicletas Disponibles: {row['num_bikes_available']}<br>")
                    ).add_to(m1)
                folium.Marker(
                    location=actual_location,
                    popup="Estás aquí.",
                    icon=folium.Icon(color='blue', icon='person', prefix='fa')
                ).add_to(m1)

                folium.Marker(
                    location = (selected_station[1], selected_station[2]),
                    popup="Bicicleta disponible aquí.",
                    icon=folium.Icon(color='red', icon='bicycle', prefix='fa')
                ).add_to(m1)
                
                coordinates, duration = run_osrm(selected_station, actual_location)
                print(coordinates)

                folium.PolyLine(
                    locations=coordinates,
                    color='blue',
                    weight=5,
                    tooltip="te tomará {} para llegar aquí.".format(duration),
                ).add_to(m1)

                # Display the map
                folium_static(m1)
                with col3: 
                    st.metric(label="Tiempo Estimado (min)", value=duration)

# "Devolver" Option Map (Docks)
if option == 'Devolver':
    if find_docks_button:
        if street != "":
            actual_location_return = geocode(street + " " + city + " " + country)
            if actual_location_return != "":
                selected_station = get_dock_availability(actual_location_return, data)
                center = actual_location_return
                m2 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')
                for _, row in data.iterrows():
                    marker_color = get_marker_color(row['num_bikes_available']) 
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=2,
                        color=marker_color,
                        fill=True,
                        fill_color=marker_color,
                        fill_opacity=0.7,
                        popup=folium.Popup(f"Estación ID: {row['station_id']}<br>"
                                            f"Total Bicicletas Disponibles: {row['num_bikes_available']}<br>")
                    ).add_to(m2)
                folium.Marker(
                    location=actual_location_return,
                    popup="Estás aquí.",
                    icon=folium.Icon(color='blue', icon='person', prefix='fa')
                ).add_to(m2)

                folium.Marker(
                    location = (selected_station[1], selected_station[2]),
                    popup="Deja tu bicicleta aquí.",
                    icon=folium.Icon(color='red', icon='home', prefix='fa')
                ).add_to(m2)
                
                coordinates, duration = run_osrm(selected_station, actual_location_return)
                print(coordinates)

                folium.PolyLine(
                    locations=coordinates,
                    color='blue',
                    weight=5,
                    tooltip="te tomará {} para llegar aquí.".format(duration),
                ).add_to(m2)

                # Display the map
                folium_static(m2)
                with col3: 
                    st.metric(label="Tiempo Estimado (min)", value=duration)    