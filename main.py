import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

from pyrunner import InteractivePythonRunner
from schema import DataFrameInfo, QueryPrompt
from utils import extract_code

require_doc = f"""
1.打开《库存报表》，将《货品报表》的全部字段，根据”货号”匹配到《库存报表》上；
2.然后剔除《库存报表》中” 类别”为”饰品”和”服装”的记录；
3.根据” 渠道编号”聚合计算” 可用库存”和” 默认吊牌价”；
4.最后输出” 仓库编码”即” 渠道编号”，” 仓库名称”即” 渠道简称”，” 库存总量”即” 可用库存”合计，” 库存总价值”即” 默认吊牌价”合计。
"""

if __name__ == '__main__':
    query = require_doc

    dfs_info = [DataFrameInfo(name='货品报表', path=Path('./inputs/货品报表_1713510378313.xlsx')),
                DataFrameInfo(name='库存报表', path=Path('./inputs/库存报表_1713509874777.xlsx'))]

    p = QueryPrompt(dfs=dfs_info, query=query)
    logger.info(p.generate_prompt())

    # 模型请求
    load_dotenv()
    completion = (OpenAI(base_url=os.getenv('BASE_URL'),
                         api_key=os.getenv('API_KEY'))
                  .chat.completions.create(model='gpt-3.5-turbo',
                                           temperature=0.0,
                                           messages=[{'role': 'user',
                                                      'content': p.generate_prompt()}])
                  )

    define_function_code = extract_code(completion)

    ipy_dir = Path('/Users/lzx/miniconda3/envs/py310/bin')
    with InteractivePythonRunner(ipy_dir) as ipy:
        out, err = ipy.run([p.import_package(),
                            p.read_pd_data(),
                            define_function_code,
                            p.exec_function(),
                            p.export_result(),
                            ])
        if err is None:
            logger.info('success to run code')
        else:
            logger.error('error to run code')
            logger.error(err)
