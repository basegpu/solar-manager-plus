import streamlit as st
from streamlit.logger import get_logger
from utils import page_config
from races import RACES
from data import get_call


LOGGER = get_logger(__name__)


def run():
    page_config()
    st.title("Home")

    st.write(RACES)

    response = get_call('overview')
    st.write(response.json())


if __name__ == '__main__':
    LOGGER.info('Starting app')
    run()