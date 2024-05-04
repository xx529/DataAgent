import re

from openai.types.chat import ChatCompletion


def extract_code(completion: ChatCompletion):
    content = completion.choices[0].message.content
    match_code = re.search(r'```python(.*?)```', content, re.DOTALL)
    fill_code = match_code.group(1)
    return fill_code
