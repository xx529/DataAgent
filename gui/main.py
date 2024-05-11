# import streamlit as st
#
# st.set_page_config(layout='wide')
#
# with st.sidebar:
#     st.title('Configure')
#     api_key = st.text_input('API KEY')
#     base_url = st.text_input('BASE URL')
#
# session_state = st.session_state
# current_tab = session_state.get('current_tab', 0)
#
# # 定义一个状态变量来跟踪当前选中的Tab
# tab_state = st.session_state.get('tab_state', 0)
#
# st.title('对账系统演示 Demo')
# tab1, tab2, tab3, tab4 = st.tabs(["1.上传数据", "2.需求录入", "3.生成大纲", "4.代码生成"])
#
# with tab1:
#     files = st.file_uploader('上传数据文件', accept_multiple_files=True)
#     print(files)
#     if st.button('确认上传'):
#         current_tab = session_state.current_tab = (current_tab + 1)
#
#
# with tab2:
#     ...
#
# if current_tab != session_state.current_tab:
#     session_state.current_tab = current_tab
#     # 根据当前激活的标签页索引，设置标签页的选中状态
#     st.tabs.set_active_tab(current_tab)

import streamlit as st

st.set_page_config(layout='wide')


st.title('对账系统演示 Demo')
st.text('这是一个对账系统的演示 Demo，用于展示如何使用 OpenAI 的 API 来生成对账系统的执行计划。')
if st.button("开始"):
    st.switch_page("pages/upload.py")
