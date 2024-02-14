import datetime as dt
import time
import pytz
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.logger import get_logger
from solar_manager.statistics import Statistics
from utils import page_config
from config import CONFIG
from data import get_stats


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')


def run():
    page_config()
    st.title(CONFIG.name)
    st.write(f'Location: {CONFIG.location}')

    key = 'ammortization'
    df = pd.DataFrame({key: [0.0] * len(CONFIG.dates)}, index=CONFIG.dates)
    for date in df.index:
        # find the prices for the date
        price = next(p for p in CONFIG.prices if p.first_date <= date <= p.last_date)
        # loop through the slots and get the according stats
        for slot in price.slots:
            t = time.time()
            start = dt.datetime(date.year, date.month, date.day, slot.from_hour, tzinfo=pytz.timezone('CET'))
            end = dt.datetime(date.year, date.month, date.day, slot.to_hour-1, 59, 59, 999, tzinfo=pytz.timezone('CET'))
            data = get_stats(CONFIG.sm_id, start.isoformat(), end.isoformat()).json()
            savings = Statistics(**data).savings_for(slot)
            df[key][date] += savings
            LOGGER.debug(f'calculated savings for ({date}, {slot}): {savings} chf, took {time.time() - t:.3f}s')
    total = df.sum()[key]
    
    fig = px.bar(df, title=f'{total:.1f} from {CONFIG.volume} ammortized')
    fig.update_layout(showlegend=False, yaxis_title='Savings [CHF]')
    st.plotly_chart(fig, use_container_width=True)
    
    st.progress(total / CONFIG.volume, f'Expected date of full ammortization: {CONFIG.expected_end(total)}')


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()