import streamlit as st

PAGE_NAME = 'plan'

st.title('第三歩：执行计划')
if st.button("下一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/code.py")

if st.button("上一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/docs.py")
