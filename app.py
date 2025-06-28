import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from llm_utils import classify_severity
from utils.location_utils import filter_by_location
from components.map_display import show_base_map

# -------------------------------
# IP-Based Location Detection
# -------------------------------
def get_ip_location():
    try:
        ip_info = requests.get('https://ipinfo.io/json').json()
        loc = ip_info.get('loc', '')
        if loc:
            lat, lon = map(float, loc.split(','))
            return lat, lon, True
    except:
        pass
    return 29.6516, -82.3248, False  # Fallback: Gainesville, FL

lat, lon, detected = get_ip_location()

# -------------------------------
# Streamlit Layout & Styling
# -------------------------------

st.set_page_config(
    page_title="MAPAssist-Disaster Relief",
    page_icon="assets/MAPAssist.png",  # relative path to your image
    layout="wide"
)
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .map-container iframe {
        height: 480px !important;
        width: 100% !important;
    }
    .chat-bubble {
        background-color: #0021A5;
        border-radius: 12px;
        padding: 10px;
        margin: 8px 0;
    }
    .chat-bubble-bot {
        background-color: #FA4616;
        border-radius: 12px;
        padding: 10px;
        margin: 8px 0;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.3, 1])

# -------------------------------
# Session State Initialization
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"sender": "bot", "message": "Hi, I’m MAPAssist. Tell me what’s happening and I’ll help you.", "time": datetime.now().strftime("%I:%M %p")}]
if "extra_df" not in st.session_state:
    st.session_state.extra_df = None
if "marker_type" not in st.session_state:
    st.session_state.marker_type = None
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# -------------------------------
# Right Column: Chat Interface
# -------------------------------
with col2:
    st.markdown("## 💬 MAPAssist - Chat Assistant")

    # Display chat history
    for msg in st.session_state.chat_history:
        sender = "👤 **You**" if msg["sender"] == "user" else "🤖 **MAPAssist**"
        bubble_class = "chat-bubble" if msg["sender"] == "user" else "chat-bubble-bot"
        st.markdown(f"{sender} ({msg['time']}):\n<div class='{bubble_class}'>{msg['message']}</div>", unsafe_allow_html=True)

    # Process input
    def handle_input():
        user_msg = st.session_state.chat_input.strip()
        if user_msg:
            now = datetime.now().strftime("%I:%M %p")
            st.session_state.chat_history.append({"sender": "user", "message": user_msg, "time": now})

            severity = classify_severity(user_msg)
            st.session_state.marker_type = None
            st.session_state.extra_df = None

            now_bot = datetime.now().strftime("%I:%M %p")
            response = f"🚨 **Severity Level:** {severity}\n\n"

            if severity == "CRITICAL":
                disasters = pd.read_csv("data/Disasters_Data.csv")
                filtered = filter_by_location(disasters, lat, lon, radius_km=20)
                st.session_state.extra_df = filtered
                st.session_state.marker_type = "Disaster"
                response += "🚨 Please call 911 immediately.\n\n📍 Nearby disaster zones are shown on the map."

            elif severity == "MEDIUM":
                volunteers = pd.read_csv("data/Volunteers_Data.csv")
                nearby = filter_by_location(volunteers, lat, lon)
                st.session_state.extra_df = nearby
                st.session_state.marker_type = "Volunteer"
                if not nearby.empty:
                    response += f"✅ Found {len(nearby)} volunteer(s) nearby. Check the map!"
                else:
                    response += "⚠️ No volunteers found near you. We'll keep looking."

            elif severity == "LOW":
                resources = pd.read_csv("data/Resources_Data.csv")
                support = pd.read_csv("data/Mental_Health_Support_Data.csv")
                filtered = filter_by_location(resources, lat, lon, radius_km=15)
                st.session_state.extra_df = filtered
                st.session_state.marker_type = "Resource"
                response += "ℹ️ Nearby help centers and mental health support are now available on the map."

            st.session_state.chat_history.append({"sender": "bot", "message": response, "time": now_bot})
            st.session_state.chat_input = ""

    st.text_area("Type your message here", key="chat_input", height=80, on_change=handle_input)

# -------------------------------
# Left Column: Map Section
# -------------------------------
with col1:
    st.markdown("### 🗺️ Your Location (Auto-Detected)" if detected else "### 🗺️ Default Location Used")
    st.caption(f"📍 Latitude: `{round(lat, 6)}` | Longitude: `{round(lon, 6)}`")

    show_base_map(
        user_lat=lat,
        user_lon=lon,
        extra_locations=st.session_state.extra_df,
        marker_label=st.session_state.marker_type or "Location"
    )
