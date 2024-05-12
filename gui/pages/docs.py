import streamlit as st

PAGE_NAME = 'docs'

st.title('第二歩：需求文档')
if st.button("下一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/plan.py")

if st.button("上一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/upload.py")
