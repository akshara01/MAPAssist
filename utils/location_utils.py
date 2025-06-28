import pandas as pd
from geopy.distance import geodesic

def filter_by_location(df, user_lat, user_lon, radius_km=10):
    filtered_rows = []
    for _, row in df.iterrows():
        dist = geodesic((user_lat, user_lon), (row['lat'], row['long'])).km
        if dist <= radius_km and row.get('available', 'yes') == 'yes':
            filtered_rows.append(row)
    return pd.DataFrame(filtered_rows)
