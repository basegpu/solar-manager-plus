import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from hourlyStats import HourlyStats
from utils import months_dict, page_config
from config import CONFIGS, set_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')

def run():
    page_config()

    cfg = st.sidebar.selectbox('Select object', CONFIGS)
    set_config(cfg)

    # load hourly stats
    hours = HourlyStats(cfg)
    data_cols = [hours.Columns.consumption, hours.Columns.production, hours.Columns.selfConsumption]

    st.title(cfg.name)
    st.write(f'Location: {cfg.location}, Timezone: {cfg.timezone}')
    
    month = st.select_slider('Select Month', months_dict.keys(), value=2, format_func=lambda x: months_dict[x])
    filter = f'{hours.Columns.month} == {month}'
    day_view = hours.raw.query(filter).groupby('hour')[data_cols].mean()/1000
    
    fig = px.line(day_view, title='Average Daily Views',
        color_discrete_map={
            hours.Columns.consumption: "red",
            hours.Columns.production: "yellow",
            hours.Columns.selfConsumption: "green",
        })
    fig.update_layout(
        yaxis_title='kWh',
        xaxis_title='Hour of the day')
    st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()