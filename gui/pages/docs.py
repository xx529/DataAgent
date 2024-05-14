import io
import time
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
from pydantic import BaseModel
from functools import partial
import openai

if st.session_state.get('run') is True:
    from utils.config import CACHE_REFORMAT_DATA_PATH, CACHE_REFORMAT_TEMPLATE_PATH, CACHE_REFORMAT_PATH
    from utils.alignment import RequirementDoc, ColumnField, DataDesc, PlanningDoc

else:
    from ..utils.config import CACHE_REFORMAT_DATA_PATH, CACHE_REFORMAT_TEMPLATE_PATH, CACHE_REFORMAT_PATH
    from ..utils.alignment import RequirementDoc, ColumnField, DataDesc, PlanningDoc

PAGE_NAME = 'docs'

REFORMAT_DATA_DIR = CACHE_REFORMAT_DATA_PATH
REFORMAT_TEMPLATE_DIR = CACHE_REFORMAT_TEMPLATE_PATH
REFORMAT_DIR = CACHE_REFORMAT_PATH

st.set_page_config(layout='wide')


class TableInfo(BaseModel):
    file_name: str
    sheet_name: str = None
    columns: List[str | int]


class TableInfoOutput(TableInfo):
    desc: str
    cols_type: List[str]
    cols_desc: List[str]


def get_all_tables(dir_path: Path):
    all_tables = []
    for file in dir_path.iterdir():
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


def data_component(dir_path: Path) -> List[DataDesc]:
    output = []
    for idx, table in enumerate(get_all_tables(dir_path)):
        title = f'{table.file_name}'
        title = title if table.sheet_name is None else f'{title}（sheet：{table.sheet_name}）'
        st.markdown(f'##### {idx + 1}. {title}')

        st.markdown('- **数据描述**（填写这份数据的描述的内容）')
        table_desc = st.text_input(f'{idx}{dir_path}数据描述', label_visibility='collapsed', max_chars=100)

        st.markdown('- **字段描述**（填写这份数据的字段描述的内容）')
        data = {'序号': range(1, len(table.columns) + 1),
                '字段': table.columns,
                '类型': [''] * len(table.columns),
                '描述': [''] * len(table.columns)}
        df_data = st.data_editor(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.caption('')
        st.caption('')

        df_desc = df_data.astype(str).rename({'字段': 'name', '类型': 'type', '描述': 'desc'}, axis=1)
        df_desc = df_desc[['name', 'type', 'desc']]

        output.append(
            DataDesc(
                file_name=table.file_name,
                sheet_name=table.sheet_name,
                data_desc=table_desc,
                column_fields=[ColumnField(**x) for x in df_desc.to_dict(orient='records')]
            )
        )

    return output


def save_doc(content):
    with open(REFORMAT_DIR / 'doc.md', 'w') as f:
        f.write(content)


def get_plan(prompt):
    st.session_state['plan_string'] = ''

    client = openai.OpenAI(api_key=st.session_state['api_key'],
                           base_url=st.session_state['base_url'])

    response = client.chat.completions.create(
        model='gpt-4-1106-preview',
        temperature=1e-3,
        stream=True,
        messages=[{'role': 'user', 'content': prompt}]
    )

    for x in response:
        if len(x.choices) > 0:
            if (string := x.choices[0].delta.content) is not None:
                time.sleep(0.1)
                st.session_state['plan_string'] += string
                yield string


def run():
    if st.button("返回"):
        st.session_state['from_page'] = PAGE_NAME
        st.switch_page("pages/preview.py")
    else:

        st.title('第3歩：需求文档')
        st.markdown('---')
        cols = st.columns(3)
        with cols[0]:
            st.markdown('### 必要信息填写')
            st.markdown('#### 1. 需求文档的标题')
            st.caption('请填写需求文档的标题，尽量明确简洁，不要超过 20 个字')
            task_title = st.text_input('文档标题', label_visibility='collapsed', max_chars=20)
            st.markdown('---')

            st.markdown('#### 2. 任务目标描述')
            st.caption('描述你的文档内容需要完成的任务目标')
            task_description = st.text_area('任务目标描述', label_visibility='collapsed', max_chars=180)
            st.markdown('---')

            st.markdown('#### 3. 输入数据描述')
            st.caption('定义明确输入的数据的字段名称，类型和含义')
            data_info = data_component(REFORMAT_DATA_DIR)
            st.markdown('---')

            st.markdown('#### 4. 输出数据描述')
            st.caption('定义明确输出的数据的字段名称，类型和含义')
            result_info = data_component(REFORMAT_TEMPLATE_DIR)
            st.markdown('---')

            st.markdown('#### 5. 任务逻辑流程')
            st.caption('描述任务的逻辑核心流程，包括输入数据的处理和输出数据的生成，字段之间的关联等等内容')
            process_logic = st.text_area('任务逻辑流程', label_visibility='collapsed')

        with cols[1]:
            r = RequirementDoc(
                task_title=task_title,
                task_desc=task_description,
                process_logic=process_logic.split('\n'),
                input_data=data_info,
                output_data=result_info
            )
            st.markdown(f'### {r.task_title}')
            st.write(f'```markdown{r.to_description()}```')
        with cols[2]:
            st.markdown('### 任务大纲')
            if st.button('生成执行大纲', use_container_width=True):
                p_get_plan = partial(get_plan, prompt=PlanningDoc.gen_planning_prompt(r))
                try:
                    st.write_stream(p_get_plan)
                    st.write(PlanningDoc.parse_from_llm_output(st.session_state['plan_string']).model_dump())
                    st.caption('')

                except Exception as e:
                    st.error(str(e))
            else:
                st.write(st.session_state.get('plan_string', ''))

        st.markdown('---')

        if st.button("下一步", use_container_width=True):
            save_doc(st.session_state['plan_string'])
            st.session_state['from_page'] = PAGE_NAME
            st.switch_page("pages/code.py")


run()
