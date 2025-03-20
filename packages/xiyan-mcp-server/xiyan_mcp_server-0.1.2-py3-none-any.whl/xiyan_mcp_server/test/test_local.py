from utils.llm_util import call_openai_sdk

messages = [
    {"role": "system", "content": "你是一个SQL助理"},
    {"role": "user", "content": f"用户的问题是: 查询2025年的总销量"}
]
param = {"model": "xyan3b", "messages": messages,"key":"12","url":"http://127.0.0.1:5090"}
print(call_openai_sdk(**param))