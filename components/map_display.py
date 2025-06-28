import folium
from streamlit_folium import st_folium

def show_base_map(user_lat, user_lon, extra_locations=None, marker_label="Location"):
    m = folium.Map(location=[user_lat, user_lon], zoom_start=14)

    # User marker
    folium.Marker(
        location=[user_lat, user_lon],
        popup="📍 You are here",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(m)

    # Add extra markers (volunteers/disasters/etc)
    if extra_locations is not None:
        for _, row in extra_locations.iterrows():
            folium.Marker(
                location=[row['lat'], row['long']],
                popup=f"{row.get('name', marker_label)}<br>{row.get('skills', row.get('description', ''))}",
                icon=folium.Icon(color="green" if marker_label == "Volunteer" else "red")
            ).add_to(m)

    st_folium(m, width=1000, height=700)
