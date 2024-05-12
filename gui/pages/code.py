import streamlit as st

PAGE_NAME = 'code'

st.title('第四歩：代码生成')
if st.button("上一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/docs.py")
