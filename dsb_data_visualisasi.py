import pandas as pd
import streamlit as st
import plotly.express as px


# Gathering Data
@st.cache_data
def load_raw_data():
    file_path = "day.csv"  # Pastikan file berada di lokasi ini atau sesuaikan
    data = pd.read_csv(file_path)
    return data

# Assessing Data
@st.cache_data
def assess_data(data):
    issues = {}
    if data.isnull().sum().any():
        issues['missing_values'] = data.isnull().sum().to_dict()
    if (data.dtypes == object).any():
        issues['object_columns'] = data.select_dtypes(include=['object']).columns.tolist()
    return issues

# Cleaning Data
@st.cache_data
def clean_data(raw_data):
    data = raw_data.copy()
    data['dteday'] = pd.to_datetime(data['dteday'])
    data.rename(columns={
        'yr': 'year',
        'mnth': 'month',
        'weathersit': 'weather',
        'hum': 'humidity',
        'cnt': 'total_rentals'
    }, inplace=True)
    data['is_weekend'] = data['weekday'].apply(lambda x: 1 if x in [0, 6] else 0)
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    data['season_name'] = data['season'].map(season_mapping)
    return data

# Load raw data and process it
raw_data = load_raw_data()
data_issues = assess_data(raw_data)
data = clean_data(raw_data)

# Streamlit app
st.title("Data Analysis Dashboard Rental Sepeda")

# Show data issues if any
if data_issues:
    st.subheader("Data Quality Issues")
    for issue, details in data_issues.items():
        st.write(f"**{issue.capitalize()}**: {details}")

# Sidebar for filtering
year_filter = st.sidebar.multiselect("Select Year", options=data['year'].unique(), default=data['year'].unique())
season_filter = st.sidebar.multiselect("Select Season", options=data['season_name'].unique(), default=data['season_name'].unique())

# Filter data based on user input
filtered_data = data[(data['year'].isin(year_filter)) & (data['season_name'].isin(season_filter))]

# Display raw data
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.write(filtered_data)

# Basic Statistics
st.subheader("Basic Statistics")
st.write(filtered_data.describe())

# Exploratory Data Analysis (EDA)
st.subheader("Exploratory Data Analysis")

# Total rentals by season
season_rentals = filtered_data.groupby('season_name')['total_rentals'].sum()
st.bar_chart(season_rentals, use_container_width=True)

# Total rentals by year
year_rentals = filtered_data.groupby('year')['total_rentals'].sum()
st.line_chart(year_rentals, use_container_width=True)

# Scatter plot for temperature vs rentals
st.subheader("Temperature vs Total Rentals")
st.write("Scatter plot showing the relationship between temperature and total rentals.")
st.plotly_chart(
    px.scatter(filtered_data, x='temp', y='total_rentals', color='season_name', 
               labels={'temp': 'Temperature', 'total_rentals': 'Total Rentals'})
)

# Conclusion
st.subheader("Conclusion")
st.markdown(
    """ 
    - Rental Sepeda dipengaruhi oleh musim dan temperatur.
    - Musim panas dan musim gugur memiliki jumlah penyewa paling tinggi.
    - Temperatur yang hangat memiliki keterkaitan dengan jumlah penyewa yang tinggi.
    """
)
