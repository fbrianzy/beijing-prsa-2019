# Air Quality Dashboard - Beijing PM2.5 Analysis

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

This project provides an interactive **Streamlit dashboard** for exploring air quality data from multiple monitoring stations in Beijing.
The dashboard allows users to analyze temporal patterns, spatial distribution, pollutant relationships, and extreme pollution events related to **PM2.5 concentration**.

The application combines **data analysis, visualization, and geospatial mapping** to provide a comprehensive view of urban air pollution dynamics.

Key technologies used:

- Python
- Streamlit
- Pandas
- Matplotlib & Seaborn
- Folium (Geospatial Visualization)

---

## Dataset

Dataset used in this project:

**Beijing Multi-Site Air Quality Data**

Source:
[GitHub marceloreis](https://github.com/marceloreis/HTI/tree/master/PRSA_Data_20130301-20170228)

The dataset contains **hourly air quality measurements from 12 monitoring stations in Beijing between 2013–2017**.

---

# Project Structure

```bash
beijing-prsa-2019/
├── data/
│   ├── daily_df.csv
│   ├── station_cluster.csv
├── dashboard.py
├── requirements.txt
├── LICENCSE
└── README.md
```

---

# Requirements

Make sure the following are installed:

- Python **3.9 or newer**
- pip
- virtual environment support (`venv`)

---

# Setup Environment

It is recommended to run the project inside a **virtual environment**.

---

## 1. Clone Repository

```bash
git clone https://github.com/fbrianzy/beijing-prsa-2019.git
cd beijing-prsa-2019
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate Virtual Environment

Linux / macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Main dependencies include:

- streamlit
- pandas
- numpy
- matplotlib
- seaborn
- folium
- streamlit-folium

---

# Running the Dashboard

After installing dependencies, start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will start a local development server.

Open your browser and visit:

```bash
http://localhost:8501
```

The dashboard should now be running locally.

---

# Dashboard Features

### Overview
Displays daily PM2.5 trends across selected monitoring stations.

### Seasonal Analysis
Explores monthly and seasonal patterns of PM2.5 concentrations.

### Station Comparison
Compares average pollution levels between monitoring stations.

### Correlation Analysis
Shows relationships between PM2.5 and other pollutants or meteorological variables.

### Extreme Pollution Events
Analyzes frequency and distribution of extreme pollution days.

### Geospatial Visualization
Interactive map with:
- station markers
- pollution clustering
- spatial segmentation
- heatmap visualization

---

# Troubleshooting

If the map appears empty:

- Ensure `./data/` folder exists
- Ensure `station_cluster.csv` contains columns:

| Columns must have |
| :--- |
| lat |
| long |
| Cluster |  
| PM2.5 |

If the map does not update after changing filters, click:

_**Render / Refresh Map**_

inside the Geospatial tab.

---
