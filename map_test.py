import streamlit as st
import folium
from streamlit_folium import st_folium

lat, lon = 29.6516, -82.3248
m = folium.Map(location=[lat, lon], zoom_start=13)
folium.Marker([lat, lon], tooltip="📍 Your Location").add_to(m)
st.title("Map Test")
st_folium(m, width=700, height=450)
