import streamlit as st
from st_pages import add_page_title, Page, show_pages

from utils.config import (
    CACHE_PATH, CACHE_REFORMAT_DATA_PATH, CACHE_REFORMAT_PATH, CACHE_REFORMAT_TEMPLATE_PATH, CACHE_UPLOAD_DATA_PATH,
    CACHE_UPLOAD_PATH, CACHE_UPLOAD_TEMPLATE_PATH,
)

path_ls = [CACHE_PATH,
           CACHE_UPLOAD_PATH,
           CACHE_UPLOAD_DATA_PATH,
           CACHE_UPLOAD_TEMPLATE_PATH,
           CACHE_REFORMAT_PATH,
           CACHE_REFORMAT_DATA_PATH,
           CACHE_REFORMAT_TEMPLATE_PATH]

for p in path_ls:
    if not p.exists():
        p.mkdir(parents=True)

add_page_title()
show_pages([Page('main.py', '对账系统演示 Demo'),
            Page('pages/upload.py', '第1歩：上传数据'),
            Page('pages/preview.py', '第2歩：数据对齐'),
            Page('pages/reformat.py', '第3歩：表头对齐'),
            Page('pages/docs.py', '第4歩：需求文档'),
            Page('pages/plan.py', '第5歩：执行计划'),
            Page('pages/code.py', '第6歩：代码生成')])

st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')
st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')
st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')

st.markdown('---')
st.caption('配置 OpenAI Key')

_api_key = st.session_state.get('api_key', '')
api_key = st.text_input('API KEY', value=_api_key)

_base_url = st.session_state.get('base_url', '')
base_url = st.text_input('BASE URL', value=_base_url)

st.session_state['api_key'] = api_key
st.session_state['base_url'] = base_url
st.session_state['from_page'] = ''

st.markdown('---')
if st.button("开始", use_container_width=True, disabled=not api_key or not base_url):
    st.session_state['from_page'] = 'home'
    st.switch_page('pages/upload.py')
