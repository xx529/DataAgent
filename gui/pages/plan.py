import streamlit as st

PAGE_NAME = 'plan'


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/docs.py")
    else:
        st.title('第5歩：执行计划')
        st.markdown('---')
        if st.button("下一步", use_container_width=True):
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/code.py")


run()
