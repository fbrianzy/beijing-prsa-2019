import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import st_folium

st.set_page_config(page_title="Air Quality Dashboard (PRSA)", layout="wide")

# load data
@st.cache_data
def load_data():
    daily_df = pd.read_csv("./data/daily_df.csv")
    station_cluster = pd.read_csv("./data/station_cluster.csv")

    daily_df["datetime"] = pd.to_datetime(daily_df["datetime"])
    if "season" not in daily_df.columns:
        def get_season(month):
            if month in [12, 1, 2]:
                return "Winter"
            elif month in [3, 4, 5]:
                return "Spring"
            elif month in [6, 7, 8]:
                return "Summer"
            else:
                return "Autumn"
        daily_df["season"] = daily_df["datetime"].dt.month.apply(get_season)

    if "year" not in daily_df.columns:
        daily_df["year"] = daily_df["datetime"].dt.year

    return daily_df, station_cluster

daily_df, station_cluster = load_data()

# sidebar
st.sidebar.title("Filters")

min_date = daily_df["datetime"].min().date()
max_date = daily_df["datetime"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

stations = sorted(daily_df["station"].unique())
selected_stations = st.sidebar.multiselect(
    "Stations",
    options=stations,
    default=stations,
)

# filter
mask = (
    (daily_df["datetime"].dt.date >= start_date) &
    (daily_df["datetime"].dt.date <= end_date) &
    (daily_df["station"].isin(selected_stations))
)
df_f = daily_df.loc[mask].copy()

# header
st.title("Air Quality Dashboard (PRSA) - PM2.5 Focus")
st.caption("Daily aggregation per station (2013-03-01 to 2017-02-28).")
st.markdown(
    'Data Source: [Beijing Multi-Site Air Quality Data (GitHub)](https://github.com/marceloreis/HTI/tree/master/PRSA_Data_20130301-20170228)'
)

# kpi row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows (filtered)", f"{len(df_f):,}")
col2.metric("Stations (filtered)", f"{df_f['station'].nunique():,}")
col3.metric("Avg PM2.5", f"{df_f['PM2.5'].mean():.2f}")
col4.metric("Max PM2.5", f"{df_f['PM2.5'].max():.2f}")

st.divider()

# tab
tab_overview, tab_season, tab_station, tab_corr, tab_extreme, tab_geo = st.tabs(
    ["Overview", "Seasonality", "Stations", "Correlation", "Extreme", "Geospatial"]
)

# overview
with tab_overview:
    st.subheader("Overall Daily PM2.5 Trend (All Selected Stations)")

    overall_daily = (
        df_f.groupby("datetime")["PM2.5"].mean().reset_index()
    )

    fig = plt.figure(figsize=(12, 4))
    plt.plot(overall_daily["datetime"], overall_daily["PM2.5"])
    plt.title("Overall Daily PM2.5 Trend")
    plt.xlabel("Date")
    plt.ylabel("Average PM2.5")
    plt.grid(alpha=0.3)
    st.pyplot(fig)

    st.write("Sample data (filtered):")
    st.dataframe(df_f.head(20), use_container_width=True)

# seasonality
with tab_season:
    st.subheader("PM2.5 by Month")
    monthly = (
        df_f.groupby(df_f["datetime"].dt.month)["PM2.5"].mean().reset_index()
    )
    monthly.columns = ["month", "avg_PM25"]

    fig = plt.figure(figsize=(10, 4))
    plt.plot(monthly["month"], monthly["avg_PM25"], marker="o")
    plt.title("Average PM2.5 by Month")
    plt.xlabel("Month")
    plt.ylabel("Average PM2.5")
    plt.xticks(range(1, 13))
    plt.grid(alpha=0.3)
    st.pyplot(fig)

    st.subheader("PM2.5 by Season")
    seasonal = (
        df_f.groupby("season")["PM2.5"].mean()
        .reindex(["Winter", "Spring", "Summer", "Autumn"])
    )

    fig = plt.figure(figsize=(8, 4))
    seasonal.plot(kind="bar")
    plt.title("Average PM2.5 by Season")
    plt.xlabel("Season")
    plt.ylabel("Average PM2.5")
    plt.xticks(rotation=0)
    plt.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

# stations
with tab_station:
    st.subheader("Average PM2.5 by Station (Filtered Range)")

    station_avg = (
        df_f.groupby("station")["PM2.5"].mean().sort_values(ascending=False)
    )

    fig = plt.figure(figsize=(12, 4))
    station_avg.plot(kind="bar")
    plt.title("Average PM2.5 by Station")
    plt.xlabel("Station")
    plt.ylabel("Average PM2.5")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

    st.subheader("Station stats (mean & std)")
    station_stats = (
        df_f.groupby("station")["PM2.5"].agg(["mean", "std"]).sort_values("mean", ascending=False)
    )
    st.dataframe(station_stats, use_container_width=True)

# correlation
with tab_corr:
    st.subheader("Correlation Matrix (Daily Aggregation, Filtered)")

    corr_cols = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    corr_df = df_f[corr_cols].corr()

    fig = plt.figure(figsize=(10, 7))
    sns.heatmap(
        corr_df, annot=True, fmt=".2f",
        cmap="coolwarm", center=0, vmin=-1, vmax=1, linewidths=0.5
    )
    plt.title("Correlation Matrix")
    st.pyplot(fig)

    st.subheader("Correlation vs PM2.5")
    st.dataframe(corr_df["PM2.5"].sort_values(ascending=False), use_container_width=True)

# extreme
with tab_extreme:
    st.subheader("PM2.5 Category Distribution (Station-Day)")

    def categorize_pm25(value):
        if value <= 12:
            return "Good"
        elif value <= 35:
            return "Moderate"
        elif value <= 55:
            return "Unhealthy (Sensitive)"
        elif value <= 150:
            return "Unhealthy"
        elif value <= 250:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    df_f["PM25_Category"] = df_f["PM2.5"].apply(categorize_pm25)

    category_counts = df_f["PM25_Category"].value_counts()

    fig = plt.figure(figsize=(10, 4))
    category_counts.plot(kind="bar")
    plt.title("Distribution of PM2.5 Categories (Station-Day)")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

    st.subheader("Extreme station-days per year (Very Unhealthy + Hazardous)")
    extreme = df_f[df_f["PM25_Category"].isin(["Very Unhealthy", "Hazardous"])]
    extreme_per_year = extreme.groupby(extreme["datetime"].dt.year).size()

    fig = plt.figure(figsize=(8, 4))
    extreme_per_year.plot(kind="bar")
    plt.title("Extreme Pollution Station-Days per Year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.xticks(rotation=0)
    plt.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

    st.dataframe(extreme_per_year.rename("extreme_station_days"), use_container_width=True)

# geospatial 
with tab_geo:
    st.subheader("Geospatial Map (Basemap Switch + Heatmap + Segmentation Overlay)")

    # kolom wajib ada: 'station', 'PM2.5', 'Cluster', 'lat', 'long'
    required_cols = {"station", "PM2.5", "Cluster", "lat", "long"}
    if not required_cols.issubset(set(station_cluster.columns)):
        st.error(
            f"Kolom station_cluster.csv kurang lengkap. Wajib ada: {sorted(list(required_cols))}. "
            f"Kolom yang terdeteksi: {list(station_cluster.columns)}"
        )
        st.stop()

    # data cleaning awal
    station_cluster_clean = station_cluster.dropna(subset=["lat", "long", "PM2.5", "Cluster"]).copy()
    if station_cluster_clean.empty:
        st.warning("Data geospatial tidak valid setelah drop NaN (lat/long/PM2.5/Cluster).")
        st.stop()

    # terapkan filter station dari sidebar ke data geospatial
    station_cluster_f = station_cluster_clean[station_cluster_clean["station"].isin(selected_stations)].copy()
    if station_cluster_f.empty:
        st.warning("Tidak ada stasiun terpilih untuk ditampilkan pada peta.")
        st.stop()

    # controls
    st.markdown("### Map Controls")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_heatmap = st.checkbox("Show Heatmap", value=True)
    with c2:
        show_segmentation = st.checkbox("Show Segmentation Overlay", value=True)
    with c3:
        seg_opacity = st.slider("Segmentation Opacity", 0.0, 0.4, 0.12, 0.01)
    with c4:
        grid_step = st.slider(
            "Grid Step",
            0.02, 0.06, 0.03, 0.01,
            help="Semakin kecil semakin halus tapi semakin berat."
        )

    # tombol render
    render = st.button("Render / Refresh Map")
    if not render:
        st.info("Klik tombol 'Render / Refresh Map' setelah mengubah filter.")
        st.stop()

    # build map
    m = folium.Map(
        location=[39.9, 116.4],
        zoom_start=10,
        tiles=None,
        control_scale=True,
        prefer_canvas=True
    )

    # basemap switch (LayerMapControl)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap (Default)", control=True).add_to(m)
    folium.TileLayer("CartoDB Positron", name="Light Basemap", control=True).add_to(m)
    folium.TileLayer("Esri.WorldImagery", name="Satellite", control=True).add_to(m)

    # english labels overlay
    folium.TileLayer(
        "CartoDB PositronOnlyLabels",
        name="English Labels (Overlay)",
        overlay=True,
        control=True,
        opacity=0.95
    ).add_to(m)

    # heatmap (pakai station terpilih)
    if show_heatmap:
        heat_data = [
            [float(r["lat"]), float(r["long"]), float(r["PM2.5"])]
            for _, r in station_cluster_f.iterrows()
        ]
        HeatMap(heat_data, radius=28, blur=18, max_zoom=13, name="Heatmap").add_to(m)

    # segmentation overlay (nearest-station grid, pakai station terpilih)
    if show_segmentation:
        import math
        import numpy as np

        def haversine_km(lat1, lon1, lat2, lon2):
            R = 6371.0
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dl = math.radians(lon2 - lon1)
            a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
            return 2 * R * math.asin(math.sqrt(a))

        # bounding box berdasarkan station terpilih + padding
        pad_lat, pad_lon = 0.10, 0.15
        min_lat = float(station_cluster_f["lat"].min()) - pad_lat
        max_lat = float(station_cluster_f["lat"].max()) + pad_lat
        min_lon = float(station_cluster_f["long"].min()) - pad_lon
        max_lon = float(station_cluster_f["long"].max()) + pad_lon

        lats = np.arange(min_lat, max_lat, grid_step)
        lons = np.arange(min_lon, max_lon, grid_step)

        cluster_fill = {
            "High Pollution": "#ff0000",
            "Medium Pollution": "#ff8c00",
            "Low Pollution": "#00a000"
        }

        seg_layer = folium.FeatureGroup(name="Segmentation (Nearest Selected Stations)", show=True)

        station_rows = station_cluster_f[["lat", "long", "Cluster"]].to_dict("records")

        for lat in lats:
            for lon in lons:
                best = None
                best_d = 1e18
                for s in station_rows:
                    d = haversine_km(lat, lon, float(s["lat"]), float(s["long"]))
                    if d < best_d:
                        best_d = d
                        best = s

                cell = [
                    [lat, lon],
                    [lat, lon + grid_step],
                    [lat + grid_step, lon + grid_step],
                    [lat + grid_step, lon],
                    [lat, lon]
                ]

                folium.Polygon(
                    locations=cell,
                    color=None,
                    fill=True,
                    fill_color=cluster_fill.get(best["Cluster"], "#0000ff"),
                    fill_opacity=seg_opacity,
                    weight=0
                ).add_to(seg_layer)

        seg_layer.add_to(m)

    # station markers (pakai station terpilih)
    color_map = {"High Pollution": "red", "Medium Pollution": "orange", "Low Pollution": "green"}
    marker_layer = folium.FeatureGroup(name="Stations", show=True)

    for _, r in station_cluster_f.iterrows():
        folium.CircleMarker(
            location=[float(r["lat"]), float(r["long"])],
            radius=7,
            tooltip=f"{r['station']} | Avg PM2.5: {float(r['PM2.5']):.1f} | {r['Cluster']}",
            popup=folium.Popup(
                f"<b>Station:</b> {r['station']}<br>"
                f"<b>Avg PM2.5:</b> {float(r['PM2.5']):.2f}<br>"
                f"<b>Cluster:</b> {r['Cluster']}",
                max_width=300
            ),
            color=color_map.get(r["Cluster"], "blue"),
            fill=True,
            fill_color=color_map.get(r["Cluster"], "blue"),
            fill_opacity=0.9,
            weight=2
        ).add_to(marker_layer)

    marker_layer.add_to(m)

    Fullscreen(position="topright").add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    # force re-render (paksa re-render untuk menghindari bug map)
    selected_key = "_".join(sorted(selected_stations))
    map_key = f"geo_{start_date}_{end_date}_{selected_key}_{show_heatmap}_{show_segmentation}_{grid_step}_{seg_opacity}"

    st_folium(m, width=1100, height=650, returned_objects=[], key=map_key)
