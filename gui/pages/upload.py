import copy
import io

import pandas as pd
import streamlit as st

if st.session_state.get('run') is True:
    from utils.config import CACHE_UPLOAD_DATA_PATH, CACHE_UPLOAD_TEMPLATE_PATH
else:
    from ..utils.config import CACHE_UPLOAD_DATA_PATH, CACHE_UPLOAD_TEMPLATE_PATH

PAGE_NAME = 'upload'

UPLOAD_DATA_DIR = CACHE_UPLOAD_DATA_PATH
CACHE_UPLOAD_TEMPLATE_PATH = CACHE_UPLOAD_TEMPLATE_PATH

st.set_page_config(layout='wide')


def save_files(data_files=None, template_file=None):
    if data_files is not None:
        for file in data_files:
            with open(UPLOAD_DATA_DIR / file.name, 'wb') as f:
                f.write(file.read())

    if template_file is not None:
        with open(CACHE_UPLOAD_TEMPLATE_PATH / template_file.name, 'wb') as f:
            f.write(template_file.read())


@st.cache_data(show_spinner=False)
def check_file(file):
    try:
        if file.name.endswith('.xlsx'):
            pd.read_excel(io.BytesIO(copy.deepcopy(file).read()))
            return
        elif file.name.endswith('.csv'):
            pd.read_csv(io.BytesIO(copy.deepcopy(file).read()))
            return
        else:
            raise Exception('仅支持 csv 和 xlsx 格式')
    except Exception as e:
        return e


def upload_data_files_component():
    upload_data_files = st.file_uploader("上传数据文件",
                                         type=["csv", "xlsx"],
                                         accept_multiple_files=True,
                                         label_visibility='collapsed')
    exist_files_name = []
    check_files_ls = []
    for file in upload_data_files:
        if file.name not in exist_files_name:
            exist_files_name.append(file.name)
            check_files_ls.append(file)

    validate_files_ls = []
    for file in check_files_ls:
        with st.spinner(f'《{file.name}》解析中...'):
            if err := check_file(file) is None:
                validate_files_ls.append(file)
                st.success(f'《{file.name}》解析成功')
            elif isinstance(err, Exception):
                st.error(f'《{file.name}》解析失败：{str(err)}')
    return validate_files_ls


def upload_template_file_component():
    result_template = st.file_uploader("上传结果模板",
                                       type=["csv", "xlsx"],
                                       label_visibility='collapsed')

    validate_template_file = None
    if result_template:
        if err := check_file(result_template) is None:
            validate_template_file = result_template
            st.success('结果模板解析成功')
        else:
            st.error(f'结果模板解析失败：{str(err)}')
    return validate_template_file


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("main.py")
    else:
        st.title('第1歩：上传文件')

        st.markdown('### 1. 数据文件')
        st.caption('请上传需要对账的数据文件，仅支持 csv 和 xlsx 格式。有重复文件自动去重')
        validate_files_ls = upload_data_files_component()
        st.markdown('---')

        st.markdown('### 2. 结果模板')
        validate_template_file = upload_template_file_component()
        st.markdown('---')

        button_label = "确认上传" if len(validate_files_ls) > 0 or validate_template_file else "跳过"
        if st.button(button_label, use_container_width=True):
            save_files(validate_files_ls, validate_template_file)
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/preview.py")


run()
