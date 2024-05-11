import streamlit as st

st.title('上传文件')
if st.button("下一步"):
    st.switch_page("pages/docs.py")

if st.button("上一步"):
    st.switch_page("main.py")
