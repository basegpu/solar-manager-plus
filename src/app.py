import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from utils import page_config
from config import CONFIG
from data import get_call


LOGGER = get_logger(__name__)


def run():
    page_config()
    st.title(CONFIG.name)
    st.write(f'Location: {CONFIG.location}')

    st.header('Ammortization')

    key = 'ammortization'
    df = pd.DataFrame({key: [0.0] * len(CONFIG.dates)}, index=CONFIG.dates)
    for date in df.index:
        response = get_call('overview')
        #st.write(response.json())
        df[key][date] = 1.0
    total = df.sum()[key]
    
    fig = px.bar(df, title=f'{total} from {CONFIG.volume} ammortized')
    fig.update_layout(showlegend=False, xaxis_title='Date', yaxis_title='Ammortization [CHF]')
    st.plotly_chart(fig, use_container_width=True)
    
    st.progress(total / CONFIG.volume, f'Expected date of full ammortization: {CONFIG.expected_end(total)}')
    st.write()


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()