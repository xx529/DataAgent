import time
from typing import List

from pydantic import BaseModel, Field

from tmpl import GEN_OPERATION_TMPL
from utils import call_openai_llm

INDENT_4 = ' ' * 4
INDENT_8 = ' ' * 8


class DataKeyField(BaseModel):
    name: str = Field(description='字段名称')
    desc: str = Field('', description='字段描述')

    def to_string(self):
        return ': '.join([self.name, self.desc])


class DataDesc(BaseModel):
    file_name: str = Field(description='文件名称')
    sheet_name: str = Field(description='sheet名称')
    data_desc: str = Field(description='数据内容')
    key_fields: List[DataKeyField] = Field([], description='字段描述')

    def to_string(self, num):
        if len(self.key_fields) == 0:
            key_field_string = '（建议补充关键字段的名称和描述）'
        else:

            key_field_strings = []
            for i in self.key_fields:
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


if __name__ == '__main__':
    r = RequirementDocDescription(
        task_desc='通过读取并处理品智平台数据与美团外卖订单及账单数据，实现对账结果的汇总、'
                  '差异标注，并将处理后的数据保存为对账结果表。',
        input_data=[
            DataDesc(
                file_name='品智平台数据1201-1231_.xlsx',
                sheet_name='品智平台数据1201-1231',
                data_desc='描述品智平台在12月份的明细交易数据',
                key_fields=[
                    DataKeyField(name='时间-结账时间', desc='交易结账的时间'),
                    DataKeyField(name='支付方式-美团外卖实收', desc='通过美团外卖平台支付的实收金额')
                ]
            ),
            DataDesc(
                file_name='美团外卖-订单明细1201-1231_.xlsx',
                sheet_name='美团外卖-订单明细1201-1231',
                data_desc='描述美团外卖平台12月份的明细交易数据',
                key_fields=[
                    DataKeyField(name='账单日期', desc='交易的时间'),
                    DataKeyField(name='交易描述', desc='交易类型的种类'),
                    DataKeyField(name='商家应收款', desc='这笔订单商家应该收到的款项金额'),
                ]
            )

        ],
        output_data=[
            DataDesc(
                file_name='对账结果.xlsx',
                sheet_name='美团品智对账结果',
                data_desc='描述对账结果的数据',
                key_fields=[
                    DataKeyField(name='日期', desc='按天展示，每天对应一行数据'),
                    DataKeyField(name='美团外卖实收', desc='品智平台数据中关于美团外卖的统计数据'),
                    DataKeyField(name='订单明细汇总', desc='美团外卖订单及账单数据中的统计数据'),
                    DataKeyField(name='差异', desc='计算每天品智平台的统计数据和美团外卖统计数据的差异'),
                ]
            )
        ],
        process_logic=[
            '关于时间的格式统一使用：`yyyy-mm-dd`',
            '金额统一保留3位小数',
            '`美团外卖实收`字段统计方式：统计`品智平台数据1201-1231`表每天的`支付方式-美团外卖实收',
            '`订单明细汇总`字段统计方式：取`美团外卖-订单明细1201-1231`表中交易描述为`外卖订单、订单退款、订单部分退款、神枪手外卖订单`的`商家应收款`金额的和',
            '`差异`字段统计方式：等于`美团外卖实收`-`订单明细汇总`',
        ],
    )
    content = r.to_string()
    prompt = GEN_OPERATION_TMPL.format(content=content)

#     prompt = f"""
#     “东方宝泰小馆-美团外卖”对账需求文档
#
# I.整体对账逻辑
# （I）获取数据
# 1、从品智平台获取配置的时间区间的账单数据
# 2、从美团外卖平台获取时间区间内的账单数据
# （II）数据填充“对账结果表”
# 1、将品智平台账单中与美团外卖平台关联的数据，按天汇总填入进“对账结果表”
# 2、将美团外卖数据，汇总数据按天填入“对账结果表”、明细数据汇总后填入“对账结果表”
# （III）数据对比
# 1、分别对比“品智平台数据”和“美团外卖的汇总数据”、“美团外卖的汇总数据” 和 “美团外卖明细数据的和”，计算数据差异
# （IV）明细数据呈现
# 1.若品智平台与美团外卖平台的汇总数据无差异，则无需对比明细数据
# 2.若品智平台与美团外卖平台的汇总数据有差异，则逐条对比明细数据。
# A、将品智明细表中明确未能匹配美团外卖明细的数据在品智明细表“是否差异”中标识为是。
# B、将美团外卖中明确未能匹配品智明细表的数据在细表“是否差异”中标识为是。
# II.数据填充逻辑 和 数据对比
# 美团外卖对账结果表样式如下
#
#
# 对账结果表分4个sheet：对账结果、品智明细表、美团外卖-账单明细、美团外卖-订单明细
# 对账结果表：按月展示行（即，每月多次对账，对账结果数据均汇总入该sheet）
# 品智明细表：展示单次获取的时间周期内的数据（即，每对账一次，按照时间周期生成一个sheet）
# 美团外卖-账单明细表：展示单次获取的时间周期内的数据（即，每对账一次，按照时间周期生成一个sheet）
# 美团外卖-订单明细表：展示单次获取的时间周期内的数据（即，每对账一次，按照时间周期生成一个sheet）
# 对账明细表字段填充逻辑
# 日期：按天展示，每天对应一行数据
# 第一部分：品智平台数据、美团外卖、差异
# 美团外卖实收：取品智明细表每天的“美团外卖实收”
# 订单明细汇总（仅含外卖订单、订单退款、订单部分退款、神枪手外卖订单）：以账单时间为对账日期筛选数据后，取美团外卖“订单明细”表中交易描述为“外卖订单、订单退款、订单部分退款、神枪手外卖订单”的“商家应收款”金额的和
# 差异（品智-美团外卖）（自动结算）：等于“美团外卖实收”-“订单明细汇总”
#
# 第二部分：美团外卖平台数据核对
# 账单金额：取美团外卖“账单明细”表中的“账单金额”
# 订单明细汇总（全）：以账单时间为对账日期筛选数据后，取美团外卖“订单明细”表中的“商家应收款”金额的和
# 美团账单差异：等于“账单金额”-“订单明细汇总（全）”
#
# III.明细数据呈现
# 查找时间间隔分4个阶梯，依次查找20秒内，1 分钟内，5分钟内，15分钟内
# 1、若日总金额无差异，则无需对比明细数据
# 2、若日总金额有差异（即 “差异（品智-美团外卖）”一列金额有一条数据不为0），则逐条对比
# “品智明细-美团外卖实收”对比 美团外卖“订单明细”中的“商家应收款”
# 品智平台的“结账时间”对比“美团外卖-订单明细”的“账单时间”
# 将品智明细表中明确未能匹配美团外卖订单明细的数据并在“是否差异”中标识为“是”。可以匹配上的数据，“是否差异”标识为“否”。未匹配规则如下
# 以品智明细表中的“结账时间”为基础，在美团外卖订单明细中找到“账单时间”少于20秒内（按时间阶梯逐个阶梯查找）的同一行数据，识别该行数据的“商家实应收款”金额  是否等于 品智明细表的“美团外卖实收”金额。若不等则视为未匹配数据。识别后在品智明细表的“是否差异”列中标识为“是”
# 将美团外卖订单明细表中明确未能匹配品智明细表的数据在“是否差异”中标识为是。未匹配规则如下
# 以美团外卖订单明细表中的“账单时间”为基础，在品智明细表中找到“结账时间”多出20秒内（按时间阶梯逐个阶梯查找）的同一行数据，识别该行数据的“美团外卖外卖实收”金额 是否等于 美团外卖订单明细表的“商家应收款”。若不等则视为未匹配数据。识别后在美团外卖订单明细表的“是否差异”列中标识为“是”
#     """

    r: RequirementDocDescription = call_openai_llm(messages=[{"role": "user", "content": prompt}],
                                                   response_model=RequirementDocDescription)
    print(r.to_string())
    # print(prompt)
    # print('-' * 30)
    # result = call_openai_llm(model='gpt-4-1106-preview',
    #                          messages=[{'role': 'user', 'content': prompt}],
    #                          temperature=1e-3,
    #                          stream=True)
    #
    # for x in result:
    #     if len(x.choices) > 0:
    #         if (string := x.choices[0].delta.content) is not None:
    #             time.sleep(0.1)
    #             print(string, end='')
    #