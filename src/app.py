import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from savings import Savings
from utils import page_config
from config import CONFIG


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')


def run():
    page_config()
    st.title(CONFIG.name)
    st.write(f'Location: {CONFIG.location}, Timezone: {CONFIG.timezone}')
    st.write(f'Investment: {CONFIG.volume} CHF, Start: {CONFIG.date}')

    savings = Savings()
    
    st.write('---')
    status = savings.last_status
    st.write(f'ammortization: {status["total"]:.1f} CHF ({savings})')
    st.progress(status['total'] / CONFIG.volume, f'Expected date of full ammortization: {status["expected end"]}')

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