import shutil
from pathlib import Path

import streamlit as st

PAGE_NAME = 'reformat'
UPLOAD_DIR = Path().absolute() / '.cache' / 'upload_data'
UPLOAD_DATA_DIR = UPLOAD_DIR / 'data'
UPLOAD_TEMPLATE_DIR = UPLOAD_DIR / 'template'
REFORMAT_DIR = Path().absolute() / '.cache' / 'reformat_data'
REFORMAT_DATA_DIR = REFORMAT_DIR / 'data'
REFORMAT_TEMPLATE_DIR = REFORMAT_DIR / 'template'

st.set_page_config(layout='wide')


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/preview.py")
    else:
        st.title('第3歩：表头对齐')
        st.markdown('---')

        for file in REFORMAT_DATA_DIR.iterdir():
            file.unlink()

        for file in UPLOAD_DATA_DIR.glob('*'):
            shutil.copy2(file, REFORMAT_DATA_DIR / file.name)

        if st.button("下一步", use_container_width=True):
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/docs.py")


run()
