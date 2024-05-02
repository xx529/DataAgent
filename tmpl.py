main_tmpl = """
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
df_result = process_data(df_0=df_0, df_1=df_1)

# 保存输出的结果
df_result.to_csv('{file_name}')
```
"""

MAIN_PROMPT_TMPL = """
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
df_result = process_data(df_0=df_0, df_1=df_1)

{export_data}
```

"""