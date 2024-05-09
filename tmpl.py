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

GEN_OPERATION_TMPL = """
1. 现在你要作为一个产品的角色，针对以下需求文档的描述，生成一份数据逻辑处理过程的简要描述大纲文档
2. 这份描述必须写清楚每一个步骤的主要操作要点和流程，让程序编写人员能够根据步骤完成开发工作
3. 文档中内容的步骤写到数据输出或者成果导出环节即可
4. 文档结构需要符合markdown的标题层次结构

例如
```markdown
# 1. 数据读取
## 1.1 读取数据
## 1.2 ...

# 2. 数据处理
## 2.2 ...
...

# n. 数据输出
## n.1 ...
## n.2 ...
```

# 以下是需求文档
```markdown
{content}
```
"""
