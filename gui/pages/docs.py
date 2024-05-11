import streamlit as st

st.title('需求文档')
if st.button("下一步"):
    st.switch_page("pages/plan.py")

if st.button("上一步"):
    st.switch_page("pages/upload.py")
