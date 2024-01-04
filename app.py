from typing import List, Tuple

from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st


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
    data['DATE'] = pd.to_datetime(data['DATE'])
    return data

def filter_by_date(data: pd.DataFrame, start_date: date, end_date:date):
    mask = (data['DATE'] > start_date) & (data['DATE'] <= end_date)
    return data.loc[mask]

def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data

@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_sales = data['#_HAZARDS'].sum()
    sales_in_m = f"{total_sales / 1000000:.2f}M"
    total_orders = data['ORDERNUMBER'].nunique()
    average_sales_per_order = f"{total_sales / total_orders / 1000:.2f}K"
    unique_customers = data['CUSTOMERNAME'].nunique()
    return [sales_in_m, total_orders, average_sales_per_order, unique_customers]

def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("Food Hazards Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)

def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.header("Filters")
    st.sidebar.divider()
    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['DATE'].min().date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", data['DATE'].max().date()))

    st.sidebar.divider()
    product_lines = sorted(data['PRODUCTLINE'].unique())
    selected_product_lines = st.sidebar.multiselect("Food Safety Hazards", product_lines, product_lines)

    return start_date, end_date, selected_product_lines

def display_charts(data: pd.DataFrame):
    combine_product_lines = st.checkbox("Combine Hazards", value=True)

    if combine_product_lines:
        fig = px.area(data, x='DATE', y='#_HAZARDS',
                      title="Food Safety Hazards Over Time", width=900, height=500)
    else:
        fig = px.area(data, x='DATE', y='#_HAZARDS', color='PRODUCTLINE',
                      title="Food Safety Hazards Over Time", width=900, height=500)

    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(rangemode='tozero', showgrid=False)
    fig.update_yaxes(rangemode='tozero', showgrid=True)
    st.plotly_chart(fig, use_container_width=True)


def main():
    set_page_config()
    data = load_data()
    st.title("📊 Food Safety - Global Food Solutions Inc.")

    start_date, end_date, selected_product_lines = display_sidebar(data)

    st.sidebar.divider()
    #if st.sidebar.button('Run', type='primary'):
        # filtering with camera and alert type is optional
    #    if start_date and end_date:
    filtered_data = data.copy()
    filtered_data = filter_by_date(data, start_date, end_date)
    filtered_data = filter_data(filtered_data, 'PRODUCTLINE', selected_product_lines)

    kpis = calculate_kpis(filtered_data)
    kpi_names = ["Total Hazards"]
    display_kpi_metrics(kpis, kpi_names)

    display_charts(filtered_data)


if __name__ == '__main__':
    main()
