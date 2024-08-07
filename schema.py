import io
from pathlib import Path
from typing import List

import pandas as pd
from pydantic import BaseModel, Field

from tmpl import MAIN_TMPL


class DataFrameInfo(BaseModel):
    name: str = Field(description='表格名称')
    path: Path = Field(description='存储路径')

    @property
    def df(self):
        suffix = self.path.suffix
        if suffix == '.xlsx':
            return pd.read_excel(self.path)
        if suffix == '.csv':
            return pd.read_csv(self.path)
        raise Exception('not found')


class QueryPrompt(BaseModel):
    dfs: List[DataFrameInfo] = Field(description='表名称以及描述')
    query: str = Field(description='用户提问')
    file_name: Path = Field(Path().absolute() / 'outputs/output.csv', description='输出文件路径名称')

    def generate_prompt(self):
        return MAIN_TMPL.format(dataframe_desc=self.get_df_info_str(),
                                query=self.query,
                                import_package=self.import_package(),
                                read_pd_data=self.read_pd_data(),
                                export_result=self.export_result(),
                                exec_function=self.exec_function())

    def get_df_info_str(self):
        result = []
        for n, x in enumerate(self.dfs):
            buffer = io.StringIO()
            x.df.info(buf=buffer)
            string = f'df_{n}: ' + x.name + '\n' + '```\n' + buffer.getvalue() + '```\n'
            result.append(string)
        return '\n'.join(result)

    def read_pd_data(self):
        result = []
        for n, x in enumerate(self.dfs):
            string = f'# {x.name}\n'
            string += f'df_{n}: pd.DataFrame = {self.pd_read_method(x.path)}("{str(x.path.absolute())}")\n'
            self.pd_read_method(x.path)
            result.append(string)
        return '\n'.join(result)

    @staticmethod
    def pd_read_method(path: Path):
        suffix = path.suffix
        if suffix == '.xlsx':
            return 'pd.read_excel'
        if suffix == '.csv':
            return 'pd.read_csv'
        raise Exception('not found')

    @staticmethod
    def import_package():
        return 'import pandas as pd'

    def export_result(self):
        return f'df_result.to_csv("{self.file_name}")'

    def exec_function(self):
        args_string = [f'df_{n}=df_{n}' for n in range(len(self.dfs))]
        return f'df_result = process_data({", ".join(args_string)})'
