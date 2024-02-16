import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from savings import Savings
from utils import page_config
from config import CONFIGS


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')


def run():
    page_config()

    cfg = st.sidebar.selectbox('Select object', CONFIGS)

    st.title(cfg.name)
    st.write(f'Location: {cfg.location}, Timezone: {cfg.timezone}')
    st.write(f'Investment: {cfg.volume} CHF, Start: {cfg.date}')

    savings = Savings(cfg)
    
    st.write('---')
    status = savings.last_status
    st.write(f'ammortization: {status["total"]:.1f} CHF ({savings})')
    st.progress(status['total'] / cfg.volume, f'Expected date of full ammortization: {status["expected end"]}')

    fig = px.line(savings.expected_ends, title='Expected date of full ammortization')
    fig.update_traces(line_color='green')
    fig.update_layout(showlegend=False, yaxis_title='Date', xaxis_title='Date')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(savings.raw, title='Daily savings')
    fig.update_layout(yaxis_title='Savings [CHF]', xaxis_title='Date')
    st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()