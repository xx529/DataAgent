import io
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
from pydantic import BaseModel

PAGE_NAME = 'docs'
REFORMAT_DIR = Path().absolute() / '.cache' / 'reformat_data'
REFORMAT_DATA_DIR = REFORMAT_DIR / 'data'
REFORMAT_TEMPLATE_DIR = REFORMAT_DIR / 'template'


class TableInfo(BaseModel):
    file_name: str
    sheet_name: str = None
    columns: List[str | int]


class TableInfoOutput(TableInfo):
    desc: str
    cols_type: List[str]
    cols_desc: List[str]


def get_all_tables():
    all_tables = []
    for file in REFORMAT_DATA_DIR.iterdir():
        if file.name.endswith('.xlsx'):
            for sheet in pd.ExcelFile(io.BytesIO(file.read_bytes())).sheet_names:
                df = pd.read_excel(io.BytesIO(file.read_bytes()), nrows=1, sheet_name=sheet, header=0)
                all_tables.append(TableInfo(file_name=file.name, sheet_name=sheet, columns=df.columns.tolist()))
        elif file.name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read_bytes()), nrows=1, header=0)
            all_tables.append(TableInfo(file_name=file.name, columns=df.columns.tolist()))
        else:
            raise Exception('仅支持 csv 和 xlsx 格式')

    return all_tables


def input_data_component():
    output = []
    for idx, table in enumerate(get_all_tables()):
        title = f'{table.file_name}'
        title = title if table.sheet_name is None else f'{title}（sheet：{table.sheet_name}）'
        st.markdown(f'##### {idx + 1}. {title}')

        st.markdown('- **数据描述**（填写这份数据的描述的内容）')
        table_desc = st.text_input(f'{idx}数据描述', label_visibility='collapsed', max_chars=100)

        st.markdown('- **字段描述**（填写这份数据的字段描述的内容）')
        data = {'序号': range(1, len(table.columns) + 1),
                '字段': table.columns,
                '类型': [''] * len(table.columns),
                '描述': [''] * len(table.columns)}
        df_data = st.data_editor(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.caption('')
        st.caption('')

    return output


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/reformat.py")
    else:

        st.title('第4歩：需求文档')
        st.markdown('---')

        st.markdown('### 1. 需求文档的标题')
        st.caption('请填写需求文档的标题，尽量明确简洁，不要超过 20 个字')
        task_title = st.text_input('文档标题', label_visibility='collapsed', max_chars=20)
        st.markdown('---')

        st.markdown('### 2. 任务目标描述')
        st.caption('描述你的文档内容需要完成的任务目标')
        task_description = st.text_area('任务目标描述', label_visibility='collapsed', max_chars=180)
        st.markdown('---')

        st.markdown('### 3. 输入数据描述')
        st.caption('定义明确输入的数据的字段名称，类型和含义')
        input_data_component()
        st.markdown('---')

        st.markdown('### 4. 输出数据描述')
        st.caption('定义明确输出的数据的字段名称，类型和含义')
        st.markdown('---')

        st.markdown('### 5. 任务逻辑流程')
        st.caption('描述任务的逻辑核心流程，包括输入数据的处理和输出数据的生成，字段之间的关联等等内容')
        st.text_input('任务逻辑流程', label_visibility='collapsed')
        st.markdown('---')

        if st.button("下一步", use_container_width=True):
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/plan.py")


run()
