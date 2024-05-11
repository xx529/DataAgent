import time
from typing import List

from pydantic import BaseModel, Field

from tmpl import GEN_OPERATION_TMPL
from utils import call_openai_llm

INDENT_4 = ' ' * 4
INDENT_8 = ' ' * 8


class ColumnField(BaseModel):
    name: str = Field(description='字段名称')
    type: str = Field(None, description='字段类型')
    desc: str = Field(None, description='字段描述')

    def to_string(self):
        col_desc = f'`{self.name}`'
        if self.type:
            col_desc += f'（{self.type}类型）'
        if self.desc:
            col_desc += f': {self.desc}'
        return col_desc


class DataDesc(BaseModel):
    file_name: str = Field(description='文件名称')
    sheet_name: str = Field(description='sheet名称')
    data_desc: str = Field(description='数据内容')
    column_fields: List[ColumnField] = Field([], description='字段描述')

    def to_string(self, num):
        if len(self.column_fields) == 0:
            key_field_string = '（建议补充关键字段的名称和描述）'
        else:

            key_field_strings = []
            for i in self.column_fields:
                key_field_strings.append(f"{INDENT_8}- {i.to_string()}")
            key_field_string = '\n' + '\n'.join(key_field_strings)

        return (f"{num}. {self.file_name}\n"
                f"{INDENT_4}- sheet名称：{self.sheet_name}\n"
                f"{INDENT_4}- 数据内容：{self.data_desc}\n"
                f"{INDENT_4}- 关键字段：{key_field_string}\n")


class RequirementDocDescription(BaseModel):
    task_desc: str = Field('', description='任务目标描述')
    input_data: List[DataDesc] = Field(default_factory=list, description='输入数据描述')
    process_logic: List[str] = Field(default_factory=list, description='数据逻辑')
    output_data: List[DataDesc] = Field(default_factory=list, description='成果输出描述')

    def to_string(self):

        if len(self.input_data) == 0:
            input_data_string = '需要补充相关内容\n'
        else:
            input_data_strings = []
            for i, data in enumerate(self.input_data):
                input_data_strings.append(data.to_string(i + 1))
            input_data_string = '\n'.join(input_data_strings)

        if len(self.process_logic) == 0:
            process_logic_string = '需要补充相关内容'
        else:
            process_logic_string = '\n'.join([f"{idx + 1}. {i}" for idx, i in enumerate(self.process_logic)])

        if len(self.output_data) == 0:
            output_data_string = '需要补充相关内容\n'
        else:
            output_data_strings = []
            for i, data in enumerate(self.output_data):
                output_data_strings.append(data.to_string(i + 1))
            output_data_string = '\n'.join(output_data_strings)

        return (f"# 数据处理需求文档 \n\n"
                f"## 任务目标描述\n"
                f"{'需要补充相关内容' if not self.task_desc else self.task_desc}\n\n"
                f"## 输入数据描述\n"
                f"{input_data_string}\n"
                f"## 结果输出描述\n"
                f"{output_data_string}\n"
                f"## 数据逻辑\n"
                f"{process_logic_string}\n")


r = RequirementDocDescription(
    task_desc='通过读取并处理品智平台数据与美团外卖订单及账单数据，实现对账结果的汇总、'
              '差异标注，并将处理后的数据保存为对账结果表。',
    input_data=[
        DataDesc(
            file_name='品智平台数据1201-1231_.xlsx',
            sheet_name='品智平台数据1201-1231',
            data_desc='描述品智平台在12月份的明细交易数据',
            column_fields=[
                ColumnField(name='时间-结账时间', type='datetime', desc='交易结账的时间'),
                ColumnField(name='支付方式-美团外卖实收', type='float', desc='通过美团外卖平台支付的实收金额')
            ]
        ),
        DataDesc(
            file_name='美团外卖-订单明细1201-1231_.xlsx',
            sheet_name='美团外卖-订单明细1201-1231',
            data_desc='描述美团外卖平台12月份的明细交易数据',
            column_fields=[
                ColumnField(name='账单日期', type='datetime', desc='交易的时间'),
                ColumnField(name='交易描述', type='string', desc='交易类型的种类'),
                ColumnField(name='商家应收款', type='float', desc='这笔订单商家应该收到的款项金额'),
            ]
        )

    ],
    output_data=[
        DataDesc(
            file_name='对账结果.xlsx',
            sheet_name='美团品智对账结果',
            data_desc='描述对账结果的数据',
            column_fields=[
                ColumnField(name='日期', desc='按天展示，每天对应一行数据', type='datetime'),
                ColumnField(name='美团外卖实收', desc='品智平台数据中关于美团外卖的统计数据', type='float'),
                ColumnField(name='订单明细汇总', desc='美团外卖订单及账单数据中的统计数据', type='float'),
                ColumnField(name='差异', desc='计算每天品智平台的统计数据和美团外卖统计数据的差异', type='float'),
            ]
        )
    ],
    process_logic=[
        '关于时间的格式统一使用：`yyyy-mm-dd`',
        '金额相关的字段统一保留3位小数',
        '`美团外卖实收`字段统计方式：统计`品智平台数据1201-1231`表每天的`支付方式-美团外卖实收',
        '`订单明细汇总`字段统计方式：取`美团外卖-订单明细1201-1231`表中交易描述为`外卖订单、订单退款、订单部分退款、神枪手外卖订单`的`商家应收款`金额的和',
        '`差异`字段统计方式：等于`美团外卖实收`-`订单明细汇总`',
    ],
)

content = r.to_string()
# print(content)
prompt = GEN_OPERATION_TMPL.format(content=content)
print(prompt)


print('-' * 30)
result = call_openai_llm(model='gpt-4-1106-preview',
                         messages=[{'role': 'user', 'content': prompt}],
                         temperature=1e-3,
                         stream=True)

plan_string = ''
for x in result:
    if len(x.choices) > 0:
        if (string := x.choices[0].delta.content) is not None:
            time.sleep(0.1)
            print(string, end='')
            plan_string += string

print('-' * 30)
result = call_openai_llm(model='gpt-4-1106-preview',
                         messages=[{'role': 'user', 'content': f'根据以下数据处理需求，生成 python 代码\n{plan_string}'}],
                         temperature=1e-3,
                         stream=True)

for x in result:
    if len(x.choices) > 0:
        if (string := x.choices[0].delta.content) is not None:
            time.sleep(0.1)
            print(string, end='')
