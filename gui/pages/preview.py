import io
from typing import Dict, List

import numpy as np
import pandas as pd
import streamlit as st
from pydantic import BaseModel

if st.session_state.get('run') is True:
    from utils.config import (
    CACHE_REFORMAT_DATA_PATH,
    CACHE_REFORMAT_TEMPLATE_PATH,
    CACHE_UPLOAD_DATA_PATH,
    CACHE_UPLOAD_TEMPLATE_PATH,
)
else:
    from ..utils.config import (
        CACHE_REFORMAT_DATA_PATH,
        CACHE_REFORMAT_TEMPLATE_PATH,
        CACHE_UPLOAD_DATA_PATH,
        CACHE_UPLOAD_TEMPLATE_PATH
)

PAGE_NAME = 'data'

UPLOAD_DATA_DIR = CACHE_UPLOAD_DATA_PATH
UPLOAD_TEMPLATE_DIR = CACHE_UPLOAD_TEMPLATE_PATH

REFORMAT_DATA_DIR = CACHE_REFORMAT_DATA_PATH
REFORMAT_TEMPLATE_DIR = CACHE_REFORMAT_TEMPLATE_PATH

st.set_page_config(layout='wide')


class DataAlignmentConfig(BaseModel):
    file_name: str
    sheet_name: str | None = None
    header: int
    select_cols: list[int]


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


def show_single_table(file, df, count, sheet_name, label_prefix) -> DataAlignmentConfig | None:
    st.markdown(f'##### {count}. {file.name}（sheet：{sheet_name}）' if sheet_name else f'##### {file.name}')

    is_select_table = st.toggle(f'{count}{label_prefix}是否选择', value=False, label_visibility='collapsed')
    if not is_select_table:
        return None

    if df is None:
        st.error(f'读取失败：{str(file.name)}')
        return

    df = df.astype(str)
    df.columns = list(range(1, len(df.columns) + 1))

    cols = st.columns(3)
    with cols[0]:
        st.markdown('- 选择表头行（红色字体）')
        header = st.number_input(f'{count}{label_prefix}表头行', min_value=1, max_value=len(df), value=1, step=1,
                                 label_visibility='collapsed')

    with cols[1]:
        st.markdown('- 筛选列字段（带背景色）')
        select_cols = st.multiselect(f'{count}{label_prefix}选取列', df.columns, label_visibility='collapsed')

    with cols[2]:
        st.markdown('- 仅显示选择字段')
        is_only_select_cols = st.toggle(f'{count}{label_prefix}仅显示选择列', value=False, label_visibility='collapsed')

    if is_only_select_cols:
        df = df[select_cols]

    df_style = df.style.map(lambda x: 'color: red;', subset=pd.IndexSlice[:header - 1, :])

    if select_cols:
        df_style = df_style.set_properties(**{'background-color': '#ffffb3'}, subset=select_cols)

    st.dataframe(df_style, hide_index=True, use_container_width=True)

    if not select_cols:
        st.error('请至少选择一列')

    return DataAlignmentConfig(file_name=file.name, header=header, select_cols=select_cols, sheet_name=sheet_name)


def data_preview_component(nrows=10) -> List[DataAlignmentConfig]:
    count = 0
    cfg_ls = []

    if len(list(UPLOAD_DATA_DIR.iterdir())) == 0:
        st.error('请上传数据文件')

    for idx, file in enumerate(sorted(UPLOAD_DATA_DIR.iterdir(), key=lambda x: x.stat().st_ino, reverse=False)):
        with st.spinner('加载中...'):
            preview = read_data(file, nrows=nrows)
            for sheet_name, df in preview.items():
                count += 1
                cfg = show_single_table(file=file, df=df, count=count, sheet_name=sheet_name, label_prefix='data')

                if cfg is not None:
                    cfg_ls.append(cfg)

                for i in range(3):
                    st.caption('')
    return cfg_ls


def clear_data_component():
    if st.button('清除缓存数据'):
        for file in UPLOAD_DATA_DIR.glob('*'):
            file.unlink()

        for file in UPLOAD_TEMPLATE_DIR.glob('*'):
            file.unlink()


def template_preview_component(nrows=10) -> List[DataAlignmentConfig]:
    if len(list(UPLOAD_TEMPLATE_DIR.iterdir())) == 0:
        st.error('请上传结果模板')
        return []

    file = list(UPLOAD_TEMPLATE_DIR.iterdir())[0]
    count = 0
    cfg_ls = []
    with st.spinner('加载中...'):
        preview = read_data(file, nrows=nrows)
        for sheet_name, df in preview.items():
            count += 1
            cfg = show_single_table(file=file, df=df, count=count, sheet_name=sheet_name, label_prefix='template')

            if cfg is not None:
                cfg_ls.append(cfg)

            for i in range(3):
                st.caption('')
    return cfg_ls


def validate_cfg(data_cfg_ls: List[DataAlignmentConfig], template_cfg_ls: List[DataAlignmentConfig]) -> bool:
    if len(data_cfg_ls) == 0 or len(template_cfg_ls) == 0:
        return False

    for c in data_cfg_ls + template_cfg_ls:
        if not c.select_cols:
            return False
    return True


def create_file_for_docs(data_cfg_ls: List[DataAlignmentConfig], template_cfg_ls: List[DataAlignmentConfig]):
    for file in REFORMAT_DATA_DIR.glob('*'):
        file.unlink()

    for file in REFORMAT_TEMPLATE_DIR.glob('*'):
        file.unlink()

    count = 0
    for data in data_cfg_ls:
        if data.file_name.endswith('.xlsx'):
            df = pd.read_excel(UPLOAD_DATA_DIR / data.file_name, sheet_name=data.sheet_name, header=data.header - 1)
            col_idx = np.array(data.select_cols) - 1
            df = df[df.columns[col_idx]]
            df.to_excel(REFORMAT_DATA_DIR / f'数据{count}.xlsx', index=False, sheet_name=data.sheet_name)

        elif data.file_name.endswith('.csv'):
            df = pd.read_csv(UPLOAD_DATA_DIR / data.file_name, header=data.header - 1)
            col_idx = np.array(data.select_cols) - 1
            df = df[df.columns[col_idx]]
            df.to_csv(REFORMAT_DATA_DIR / f'数据{count}.csv', index=False)
        count += 1

    for data in template_cfg_ls:
        if data.file_name.endswith('.xlsx'):
            df = pd.read_excel(UPLOAD_TEMPLATE_DIR / data.file_name, sheet_name=data.sheet_name, header=data.header - 1)
            col_idx = np.array(data.select_cols) - 1
            df = df[df.columns[col_idx]]
            df.to_excel(REFORMAT_TEMPLATE_DIR / f'数据{count}.xlsx', index=False, sheet_name=data.sheet_name)

        elif data.file_name.endswith('.csv'):
            df = pd.read_csv(UPLOAD_TEMPLATE_DIR / data.file_name, header=data.header - 1)
            col_idx = np.array(data.select_cols) - 1
            df = df[df.columns[col_idx]]
            df.to_csv(REFORMAT_TEMPLATE_DIR / f'数据{count}.csv', index=False)
        count += 1


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/upload.py")
    else:
        st.title('第2歩：数据对齐')
        clear_data_component()

        st.markdown('### 1. 所有数据')
        data_cfg_ls = data_preview_component()
        st.markdown('---')

        st.markdown('## 2. 结果模板')
        template_cfg_ls = template_preview_component()
        st.markdown('---')

        is_pass = validate_cfg(data_cfg_ls, template_cfg_ls)

        if st.button("下一步", use_container_width=True, disabled=not is_pass):
            st.session_state['from_page'] = PAGE_NAME
            create_file_for_docs(data_cfg_ls, template_cfg_ls)
            st.switch_page("pages/docs.py")


run()
