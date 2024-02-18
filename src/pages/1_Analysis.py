import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from hourlyStats import HourlyStats
from utils import page_config
from config import get_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')

page_config()
cfg = get_config()

# load hourly stats
hours = HourlyStats(cfg)
st.write(f'HourlyStats: {hours}')

st.dataframe(hours.raw)

fig = px.line(hours.raw[[hours.Columns.consumption, hours.Columns.production, hours.Columns.selfConsumption]], title='Hourly Stats')
fig.update_layout(yaxis_title='MWh', xaxis_title='Time')
st.plotly_chart(fig, use_container_width=True)