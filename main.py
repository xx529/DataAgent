import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from pyrunner import InteractivePythonRunner
from schema import DataFrameInfo, QueryPrompt

require_doc = f"""
1.打开《库存报表》，将《货品报表》的全部字段，根据”货号”匹配到《库存报表》上；
2.然后剔除《库存报表》中” 类别”为”饰品”的记录；
3.根据” 渠道编号”聚合计算” 可用库存”和” 默认吊牌价”；
4.最后输出” 仓库编码”即” 渠道编号”，” 仓库名称”即” 渠道简称”，” 库存总量”即” 可用库存”合计，” 库存总价值”即” 默认吊牌价”合计。
"""

if __name__ == '__main__':
    query = require_doc

    dfs_info = [DataFrameInfo(name='货品报表', path=Path('./inputs/货品报表_1713510378313.xlsx')),
                DataFrameInfo(name='库存报表', path=Path('./inputs/库存报表_1713509874777.xlsx'))]

    p = QueryPrompt(dfs=dfs_info, query=query)
    print(p.generate_prompt())

    # 模型请求
    # load_dotenv()
    # completion = (OpenAI(base_url=os.getenv('BASE_URL'),
    #                      api_key=os.getenv('API_KEY'))
    #               .chat.completions.create(model='gpt-3.5-turbo',
    #                                        temperature=0.0,
    #                                        messages=[{'role': 'user',
    #                                                   'content': p.generate_prompt()}])
    #               )
    #
    # content = completion.choices[0].message.content
    # match_code = re.search(r'```python(.*?)```', content, re.DOTALL)
    # fill_code = match_code.group(1)
    # print(fill_code)
    #
    # ipy_dir = Path('/Users/lzx/miniconda3/envs/py310/bin')
    # with InteractivePythonRunner(ipy_dir) as ipy:
    #     ipy.run(p.import_package())
    #     ipy.run(p.read_pd_data())
    #     ipy.run(fill_code)
    #     out, err = ipy.run('df_result = process_data(df_0, df_1)')
    #     out, err = ipy.run('print(df_result)')
    #     print(out)
    #     print(err)
