import os
from pathlib import Path
from typing import List, Tuple

from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LOGO = os.path.join(BASE_DIR, 'icon', 'aimakr_logo.jpg') 
USER_IMG = os.path.join(BASE_DIR, 'image', 'user.png') 

def set_page_config():
    st.set_page_config(
        page_title="Food Safety - Global Food Solutions Inc.",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv('data/food_hazards_data_sample.csv', encoding='latin1')
    data['TIME'] = pd.to_datetime(data['TIME'], format='mixed')
    return data

def filter_by_date(data: pd.DataFrame, start_date: date, end_date:date):
    mask = (data['TIME'] > start_date) & (data['TIME'] <= end_date)
    return data.loc[mask]

def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data

@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_hazards = format(data['NUMBER OF HAZARDS'].sum(), ',d')
    return [total_hazards]


def add_header(user):
    """
    # top header : user pic | name   logout    
    """
    user_img_name, logo = st.columns((7, 1))
    with user_img_name:
        col1, _, col2 = st.columns([1,1,20])
        with col1:
            st.image(USER_IMG, width=60)
        with col2:
            st.markdown(f":blue[Hello] :orange[{user.capitalize()}] :confetti_ball:")
    with logo:
        st.image(LOGO, width=50)
    st.subheader('', divider='rainbow')
    #add_space
    for _ in range(1):
        st.write('#')


def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("Food Hazards Metrics")
    for _, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)

def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.header("Filters")
    st.sidebar.divider()
    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['TIME'].min().date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", data['TIME'].max().date()))

    st.sidebar.divider()
    hazard_types = sorted(data['HAZARD TYPE'].unique())
    selected_hazard_types = st.sidebar.multiselect("Food Safety Hazards", hazard_types, hazard_types)

    return start_date, end_date, selected_hazard_types

def display_charts(data: pd.DataFrame):
    combine_hazard_types = st.checkbox("Combine Hazards", value=True)

    if combine_hazard_types:
        fig = px.area(data, x='TIME', y='NUMBER OF HAZARDS',
                      title="Food Safety Hazards Over Time", width=900, height=500)
    else:
        fig = px.area(data, x='TIME', y='NUMBER OF HAZARDS', color='HAZARD TYPE',
                      title="Food Safety Hazards Over Time", width=900, height=500)

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(rangemode='tozero', showgrid=False)
    fig.update_yaxes(rangemode='tozero', showgrid=True)
    st.plotly_chart(fig, use_container_width=True)


def main(username):
    set_page_config()
    data = load_data()

    add_header(user=username)

    st.title("📊 Food Safety - Global Food Solutions Inc.")

    start_date, end_date, selected_hazard_types = display_sidebar(data)

    st.sidebar.divider()
    #if st.sidebar.button('Run', type='primary'):
        # filtering with camera and alert type is optional
    #    if start_date and end_date:
    filtered_data = data.copy()
    filtered_data = filter_by_date(data, start_date, end_date)
    filtered_data = filter_data(filtered_data, 'HAZARD TYPE', selected_hazard_types)

    kpis = calculate_kpis(filtered_data)
    kpi_names = ["Total Hazards"]
    display_kpi_metrics(kpis, kpi_names)
    display_charts(filtered_data)


if __name__ == '__main__':
    user = 'mike'
    main(user)
