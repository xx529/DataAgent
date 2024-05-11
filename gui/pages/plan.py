import streamlit as st

st.title('执行计划')
if st.button("下一步"):
    st.switch_page("pages/code.py")

if st.button("上一步"):
    st.switch_page("pages/docs.py")
