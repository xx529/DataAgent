from pathlib import Path
import streamlit as st
from st_pages import Page, show_pages, add_page_title


current_path = Path().absolute()
cache_path = current_path / '.cache'
cache_data_path = cache_path / 'upload_data'

if not cache_path.exists():
    cache_path.mkdir()

if not cache_data_path.exists():
    cache_data_path.mkdir()

st.set_page_config(layout='wide')

add_page_title()
show_pages([Page('main.py', '对账系统演示 Demo'),
            Page('pages/upload.py', '第一歩：上传数据'),
            Page('pages/docs.py', '第二歩：需求文档'),
            Page('pages/plan.py', '第三歩：执行计划'),
            Page('pages/code.py', '第四歩：代码生成')])

st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')
st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')
st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')

st.markdown('---')
st.caption('配置 OpenAI Key')

_api_key = st.session_state.get('api_key', '')
api_key = st.text_input('API KEY', type='password', value=_api_key)

_base_url = st.session_state.get('base_url', '')
base_url = st.text_input('BASE URL', value=_base_url)

st.session_state['api_key'] = api_key
st.session_state['base_url'] = base_url

st.markdown('---')
if st.button("开始", use_container_width=True, disabled=not api_key or not base_url):
    st.session_state['from_page'] = 'home'
    st.switch_page('pages/upload.py')

