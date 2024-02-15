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
    st.write(f'Location: {CONFIG.location}, Timezone: {CONFIG.timezone}')
    st.write(f'Investment: {CONFIG.volume} CHF, Start: {CONFIG.date}')

    keys = ('not spent', 'sold')
    df = pd.DataFrame({key: [0.0] * len(CONFIG.dates) for key in keys}, index=CONFIG.dates)
    for date in df.index:
        # find the slots for the date
        slots = next(s for s in CONFIG.structure if s.first_date <= date <= s.last_date and date.weekday() in s.days_of_week)
        # loop through the slots and get the according stats
        hours = [0] + slots.switching_hours + [24]
        for i in range(len(hours) - 1):
            t = time.time()
            start = dt.datetime(date.year, date.month, date.day, hours[i], tzinfo=pytz.timezone('CET'))
            end = dt.datetime(date.year, date.month, date.day, hours[i+1]-1, 59, 59, 999, tzinfo=pytz.timezone('CET'))
            data = get_stats(CONFIG.sm_id, start.isoformat(), end.isoformat()).json()
            savings = Statistics(**data).savings_for(CONFIG.tariffs[i%2])
            for iKey in range(len(keys)):
                df[keys[iKey]][date] += savings[iKey]
            LOGGER.debug(f'calculated savings for ({date}, {hours[i]}-{hours[i+1]}): {savings} chf, took {time.time() - t:.3f}s')
    
    categories = df.sum()
    summary = ', '.join([f'{categories[keys[iKey]]:.1f} {keys[iKey]}' for iKey in range(len(keys))])
    total = categories.sum()
    st.write('---')
    st.write(f'ammortization: {total:.1f} CHF ({summary})')
    st.progress(total / CONFIG.volume, f'Expected date of full ammortization: {CONFIG.expected_end(total)}')

    fig = px.bar(df)
    fig.update_layout(yaxis_title='Savings [CHF]', xaxis_title='Date')
    st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()