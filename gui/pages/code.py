import streamlit as st

PAGE_NAME = 'code'
st.set_page_config(layout='wide')

st.title('第4歩：代码生成')
if st.button("上一步"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/docs.py")
