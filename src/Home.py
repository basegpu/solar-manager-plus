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
    
    tab1, tab2 = st.tabs(['Daily View', 'Yearly View'])

    with tab1:
        col1, _, col2 = st.columns([3, 1, 2])
        with col1:
            month = st.select_slider('Select Month', months_dict.keys(), cfg.now.month, format_func=lambda x: months_dict[x])
            data = hours.day_view(month, 1000)
        with col2:
            st.dataframe(data.sum(), column_config={'0': 'total [kWh]'})

        st.write(f'Average daily data [kWh] for {months_dict[month]}')
        st.area_chart(
            data,
            use_container_width=True,
            color=['#ff6666', '#ffff66', '#66ffff'])

    with tab2:
        col1, _, col2 = st.columns([3, 1, 2])
        with col1:
            hour = st.slider('Select Hour', 1, 24, cfg.now.hour)
            data = hours.year_view(hour, 1000)
        with col2:
            st.dataframe(data.sum(), column_config={'0': 'total [kWh]'})
        
        st.write(f'Average yearly data [kWh] for {hour} of the day')
        st.area_chart(
            data,
            use_container_width=True,
            color=['#ff6666', '#ffff66', '#66ffff'])

if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()