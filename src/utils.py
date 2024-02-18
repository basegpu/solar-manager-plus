import streamlit as st

RESOURCES_PATH = 'resources'

def page_config():
    st.set_page_config(
        page_title='Solar Manager - Addons',
        page_icon=':sun:',
    )

months_dict = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}