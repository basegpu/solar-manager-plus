import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from savings import Savings
from utils import page_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')

cfg = page_config()

st.title('Ammortization Forecast')
st.write(f'Investment: {cfg.volume} CHF, Start: {cfg.date}')

savings = Savings(cfg)

st.write('---')
status = savings.last_status
st.write(f'ammortization: {status["total"]:.1f} CHF ({savings})')
st.progress(status['total'] / cfg.volume, f'Expected date of full ammortization: {status["expected end"]}')

tab1, tab2 = st.tabs(['Expected date of full ammortization', 'Daily savings'])
with tab1:
    fig = px.line(savings.raw[savings.Columns.expected])
    fig.update_traces(line_color='green')
    fig.update_layout(showlegend=False, yaxis_title='Date', xaxis_title='Date')
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    fig = px.bar(savings.raw[[savings.Columns.notSpent, savings.Columns.sold]])
    fig.update_layout(yaxis_title='Savings [CHF]', xaxis_title='Date')
    st.plotly_chart(fig, use_container_width=True)