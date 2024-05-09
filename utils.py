import os
import re

import instructor
from dotenv import load_dotenv
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

load_dotenv()


def extract_code(completion: ChatCompletion):
    content = completion.choices[0].message.content
    match_code = re.search(r'```python(.*?)```', content, re.DOTALL)
    fill_code = match_code.group(1)
    return fill_code


def call_openai_llm(messages,
                    model='gpt-3.5-turbo',
                    temperature=0.0,
                    stream=False,
                    response_model=None,
                    ):

    client = OpenAI(base_url=os.getenv('BASE_URL'), api_key=os.getenv('API_KEY'))
    if response_model is None:
        return client.chat.completions.create(model=model,
                                              stream=stream,
                                              temperature=temperature,
                                              messages=messages)
    else:
        return instructor.from_openai(client).chat.completions.create(model=model,
                                                                      stream=stream,
                                                                      response_model=response_model,
                                                                      temperature=temperature,
                                                                      messages=messages)
