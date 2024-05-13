import io
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

PAGE_NAME = 'data'
UPLOAD_DIR = Path().absolute() / '.cache' / 'upload_data'
UPLOAD_DATA_DIR = UPLOAD_DIR / 'data'
UPLOAD_TEMPLATE_DIR = UPLOAD_DIR / 'template'

st.set_page_config(layout='wide')


def read_data(_file, nrows=20) -> Dict[str | None, pd.DataFrame | Exception]:
    try:
        if _file.suffix == '.xlsx':
            df_read_data = {}
            for sheet in pd.ExcelFile(io.BytesIO(_file.read_bytes())).sheet_names:
                df_read_data[sheet] = pd.read_excel(io.BytesIO(_file.read_bytes()), nrows=nrows, sheet_name=sheet,
                                                    header=None)
            return df_read_data

        elif _file.suffix == '.csv':
            df_read_data = pd.read_csv(io.BytesIO(_file.read_bytes()), nrows=nrows, header=None)
            return {None: df_read_data}

        else:
            raise Exception('仅支持 csv 和 xlsx 格式')

    except Exception as e:
        return {None: e}


def show_single_table(file_name, df, title_count):
    if df is None:
        st.error(f'读取失败：{str(file_name)}')
        return

    df = df.astype(str)
    df.columns = list(range(1, len(df.columns) + 1))

    cols = st.columns(3)
    with cols[0]:
        st.markdown('- 选择表头行')
        st.number_input(f'{title_count}表头行', min_value=1, max_value=len(df), value=1, step=1,
                        label_visibility='collapsed')
    with cols[1]:
        st.markdown('- 筛选列字段')
        select_cols = st.multiselect(f'{title_count}选取列', df.columns, label_visibility='collapsed')

    with cols[2]:
        st.markdown('- 仅显示选择字段')
        is_only_select_cols = st.toggle(f'{title_count}仅显示选择列', value=False, label_visibility='collapsed')

    if is_only_select_cols:
        df = df[select_cols]

    if select_cols:
        df = df.style.set_properties(**{'background-color': '#ffffb3'}, subset=select_cols)


    st.dataframe(df, hide_index=True, use_container_width=True)

    return


def data_preview_component(nrows=10):
    count = 0
    for idx, file in enumerate(sorted(UPLOAD_DATA_DIR.iterdir(), key=lambda x: x.stat().st_ino, reverse=False)):
        with st.spinner('加载中...'):
            preview = read_data(file, nrows=nrows)
            for sheet_name, df in preview.items():
                count += 1
                st.markdown(f'##### {count}. {file.name}（sheet：{sheet_name}）' if sheet_name else f'##### {file.name}')
                show_single_table(file_name=file.name, df=df, title_count=str(count) + 'data')

                for i in range(5):
                    st.caption('')


def clear_data_component():
    if st.button('清除缓存数据'):
        for file in UPLOAD_DATA_DIR.glob('*'):
            file.unlink()


def template_preview_component(nrows=10):
    if len(list(UPLOAD_TEMPLATE_DIR.iterdir())) == 0:
        st.error('请上传结果模板')
        return

    file = list(UPLOAD_TEMPLATE_DIR.iterdir())[0]
    count = 0
    with st.spinner('加载中...'):
        preview = read_data(file, nrows=nrows)
        for sheet_name, df in preview.items():
            count += 1
            st.markdown(f'##### {count}. {file.name}（sheet：{sheet_name}）' if sheet_name else f'##### {file.name}')
            show_single_table(file_name=file.name, df=df, title_count=str(count) + 'template')

            for i in range(5):
                st.caption('')


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/upload.py")
    else:
        st.title('第2歩：数据对齐')
        clear_data_component()

        st.markdown('### 1. 所有数据')
        data_preview_component()
        st.markdown('---')

        st.markdown('## 2. 结果模板')
        template_preview_component()
        st.markdown('---')

        if st.button("下一步", use_container_width=True):
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/reformat.py")


run()
