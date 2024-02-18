import streamlit as st
from streamlit.logger import get_logger
from hourlyStats import HourlyStats
from utils import months_dict, page_config


LOGGER = get_logger(__name__)
LOGGER.setLevel('DEBUG')

def run():
    cfg = page_config()

    # load hourly stats
    hours = HourlyStats(cfg)

    st.title(cfg.name)
    st.write(f'Location: {cfg.location}, Timezone: {cfg.timezone}')
    
    month = st.select_slider('Select Month', months_dict.keys(), value=2, format_func=lambda x: months_dict[x])
    st.write(f'Average hourly data [kWh] for {months_dict[month]}')
    st.area_chart(
        hours.day_view(month, 1000),
        use_container_width=True,
        color=['#ff6666', '#ffff66', '#66ffff'])

    hour = st.slider('Select Hour', 1, 24, 12)
    st.write(f'Average yearly data [kWh], for {hour}')
    st.area_chart(
        hours.year_view(hour, 1000),
        use_container_width=True,
        color=['#ff6666', '#ffff66', '#66ffff'])

if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()