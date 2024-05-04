MAIN_TMPL = """
# 任务描述
1. 根据提示的内容，补充缺失的 process_data 函数的代码

# DataFrame 表信息描述
{dataframe_desc}

# 提示内容
{query}


# 代码生成
```python
{import_package}

{read_pd_data}

def process_data(*args, **kwargs) -> pd.DataFrame:
    # 补充代码
    ...

# 最终结果的 DataFrame 对象
{exec_function}

# 保存输出的结果
{export_result}
```
"""