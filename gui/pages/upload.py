import io
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

PAGE_NAME = 'upload'
st.set_page_config(layout='wide')


def preview_data(_file, rows=20) -> pd.DataFrame | Dict[str, pd.DataFrame] | None | Exception:
    try:
        if _file.suffix == '.xlsx':
            df_read_data = {}
            for sheet in pd.ExcelFile(io.BytesIO(_file.read_bytes())).sheet_names:
                df_read_data[sheet] = pd.read_excel(io.BytesIO(_file.read_bytes()), nrows=rows, sheet_name=sheet)
        elif _file.suffix == '.csv':
            df_read_data = pd.read_csv(io.BytesIO(_file.read_bytes()), nrows=rows)
        else:
            st.error('仅支持 csv 和 xlsx 格式')
            df_read_data = None
        return df_read_data
    except Exception as e:
        return e


data_dir = Path().absolute() / '.cache' / 'upload_data'
print(st.session_state['from_page'])
print(st.session_state['from_page'] == PAGE_NAME)
if st.session_state['from_page'] != PAGE_NAME:
    for file in data_dir.glob('*'):
        file.unlink()

if st.button("返回"):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("main.py")

st.title('第一歩：上传文件')
st.caption('请上传需要对账的数据文件，仅支持 csv 和 xlsx 格式。有重复文件自动去重')
files = st.file_uploader("上传文件", type=["csv", "xlsx"], accept_multiple_files=True, label_visibility='collapsed')
st.markdown('---')

for file in files:
    with open(data_dir / file.name, 'wb') as f:
        f.write(file.read())

if list(data_dir.iterdir()):
    cols = st.columns(5)
    with cols[0]:
        st.markdown('## 数据预览')
    with cols[-1]:
        num_rows = st.number_input('显示行数', min_value=1, max_value=1000, value=10, step=1)

    for idx, file in enumerate(sorted(data_dir.iterdir(), key=lambda x: x.stat().st_ino, reverse=False)):
        st.markdown(f'### {idx + 1}. {file.name}')
        with st.spinner('加载中...'):
            preview = preview_data(file, rows=num_rows)
            if preview is None:
                pass
            elif isinstance(preview, pd.DataFrame):
                st.dataframe(preview, hide_index=True, use_container_width=True)
            elif isinstance(preview, Dict):
                all_sheet_names = list(preview.keys())
                tabs = st.tabs(all_sheet_names)
                for tab_idx, sheet_name in enumerate(all_sheet_names):
                    with tabs[tab_idx]:
                        st.dataframe(preview[sheet_name], hide_index=True, use_container_width=True)
            elif isinstance(preview, Exception):
                st.error(f'读取失败：{str(preview)}')

    st.markdown('---')
    st.session_state['from_page'] = PAGE_NAME

if st.button("下一步", use_container_width=True, disabled=len(list(data_dir.iterdir())) == 0):
    st.session_state['from_page'] = PAGE_NAME
    st.switch_page("pages/docs.py")
