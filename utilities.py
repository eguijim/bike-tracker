import urllib  
import json  
import requests 
import pandas as pd  
import folium  
import datetime as dt 
from geopy.distance import geodesic  
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
import streamlit as st  

@st.cache_data  # Cache the function's output to improve performance

# Function to query station status from a given URL
def query_station_status(url):
    # Open the URL and decode the JSON data
    with urllib.request.urlopen(url) as data_url:  
        data = json.loads(data_url.read().decode()) 

    # Treat and filter the data
    df = pd.DataFrame(data['data']['stations'])  
    df = df[df.is_renting == 1] 
    df = df[df.is_returning == 1] 
    df = df.drop_duplicates(['station_id', 'last_reported']) 
    df.last_reported = df.last_reported.map(lambda x: dt.datetime.utcfromtimestamp(x))  # Convert to datetime
    df['time'] = data['last_updated']  
    df.time = df.time.map(lambda x: dt.datetime.utcfromtimestamp(x))  
    df = df.set_index('time') 
    df.index = df.index.tz_localize('UTC') 
    
    # Get the total of vehicles available per type
    if 'vehicle_types_available' in df.columns:
        bike_types = df['vehicle_types_available'].apply(
            lambda x: {item['vehicle_type_id']: item['count'] for item in x} if isinstance(x, list) else {}
        ).apply(pd.Series)
        df = pd.concat([df, bike_types], axis=1)

    return df  

# Function to get station latitude and longitude from a given URL
def get_station_latlon(url):
    with urllib.request.urlopen(url) as data_url:  
        latlon = json.loads(data_url.read().decode())  
    latlon = pd.DataFrame(latlon['data']['stations'])
    return latlon 

# Function to join two DataFrames on station_id
def join_latlon(df1, df2):
    df = df1.merge(df2[['station_id', 'lat', 'lon']], 
                how='left', 
                on='station_id')  
    return df  

# Function to determine marker color based on the number of bikes available
def get_marker_color(num_bikes_available):
    if num_bikes_available > 3:
        return 'green'
    elif 0 < num_bikes_available <= 3:
        return 'yellow'
    else:
        return 'red'

# Function to geocode an address
def geocode(address):
    geolocator = Nominatim(user_agent="clicked-demo")  # Create a geolocator object
    location = geolocator.geocode(address)  # Geocode the address
    if location is None:
        return ''  
    else:
        return (location.latitude, location.longitude)

# Function to get bike availability near a location calculating distances
def get_bike_availability(latlon, df, input_bike_modes):
    if len(input_bike_modes) == 0 or len(input_bike_modes) == 4:  # If no mode selected, assume all bikes are selected
        df = df.loc[df['num_bikes_available'] > 0].reset_index(drop=True) # Should be at least one bike
    else:
        # Select only the stations with the type/s of bike selected
        valid_modes = [m for m in input_bike_modes if m in df.columns]
        df = df.loc[df[valid_modes].sum(axis=1) > 0].reset_index(drop=True)

    # In case there is no bikes from the type selected
    if len(df) == 0:
        return []
        
    i = 0
    df['distance'] = ''
    while i < len(df):
        df.loc[i, 'distance'] = geodesic(latlon, (df['lat'][i], df['lon'][i])).km  # Calculate distance to each station
        i = i + 1
    chosen_station = []
    chosen_station.append(df[df['distance'] == min(df['distance'])]['station_id'].iloc[0])  # Get closest station
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lat'].iloc[0])
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lon'].iloc[0])
    
    return chosen_station  

# Function to get dock availability near a location
def get_dock_availability(latlon, df):
    i = 0
    df['distance'] = ''
    while i < len(df):
        df.loc[i, 'distance'] = geodesic(latlon, (df['lat'][i], df['lon'][i])).km  
        i = i + 1
    df = df.loc[df['num_docks_available'] > 0] 
    chosen_station = []
    chosen_station.append(df[df['distance'] == min(df['distance'])]['station_id'].iloc[0])  
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lat'].iloc[0])
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lon'].iloc[0])
    return chosen_station 

# Function to run OSRM and get route coordinates and duration
def run_osrm(chosen_station, actual_location):
    # Format the coordinates
    start = "{},{}".format(actual_location[1], actual_location[0])  
    end = "{},{}".format(chosen_station[2], chosen_station[1]) 

    # Create the OSRM API URL
    url = 'http://routing.openstreetmap.de/routed-foot/route/v1/driving/{};{}?geometries=geojson'.format(start, end)

    # Make the API request
    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)  
    print("Calling API ...:", r.status_code)  

    routejson = r.json()  # Parse the JSON response
    coordinates = []
    i = 0
    lst = routejson['routes'][0]['geometry']['coordinates']
    while i < len(lst):
        coordinates.append([lst[i][1], lst[i][0]])  
        i = i + 1
    duration = round(routejson['routes'][0]['duration'] / 60, 1)  # Convert to minutes

    return coordinates, duration  

# Function that shows the initial city map
def show_map(df):
    center_coordinates = [41.3874, 2.1686]
    city_map = folium.Map(location=center_coordinates, zoom_start=13, tiles='cartodbpositron')

    # Add circle markers to represent each station
    for _, row in df.iterrows():
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
        ).add_to(city_map)

    # Display the map 
    folium_static(city_map)

# Function that show the route for getting or leaving a bike
def show_nearest_location(data, option, find_button, street, city, country, col3, bike_type):
    if find_button:
        if street != "":
            current_location = geocode(street + " " + city + " " + country)
            if current_location != "":
                if option == 'Devolver':
                    selected_station = get_dock_availability(current_location, data)
                else:
                    selected_station = get_bike_availability(current_location, data, bike_type)
    
                if not selected_station: # Check if there is any bike of the type/s selected in the stations
                    st.warning(f"Lo sentimos, ahora mismo no hay ninguna bicicleta del tipo {bike_type} disponible.")
                else:
                    center = current_location
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
                        location=current_location,
                        popup="Estás aquí.",
                        icon=folium.Icon(color='blue', icon='person', prefix='fa')
                    ).add_to(m1)

                    # Popup text and icon
                    if option == 'Devolver':
                        popup_text = "Deja tu bicicleta aquí."
                        map_icon = folium.Icon(color='red', icon='home', prefix='fa')
                    else:
                        popup_text = "Bicicleta disponible aquí."
                        map_icon = folium.Icon(color='red', icon='bicycle', prefix='fa')
                    folium.Marker(
                        location = (selected_station[1], selected_station[2]),
                        popup=popup_text,
                        icon=map_icon
                    ).add_to(m1)
                        
                    coordinates, duration = run_osrm(selected_station, current_location)
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