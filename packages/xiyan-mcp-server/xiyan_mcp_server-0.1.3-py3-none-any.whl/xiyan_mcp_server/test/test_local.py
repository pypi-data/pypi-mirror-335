from utils.file_util import extract_sql_from_qwen
from utils.llm_util import call_openai_sdk
import time
messages = [
    {"role": "system", "content": "你是一个SQL助理,你需要生成SQL，结果由```sql和```包起来"},
    {"role": "user", "content": f"用户的问题是: 查询2025年的总销量"}
]
param = {"model": "xyan3b", "messages": messages,"key":"12","url":"http://127.0.0.1:5090"}
start = time.time()
response=call_openai_sdk(**param)
print(response)
print(response.choices[0].message.content)
print(extract_sql_from_qwen(response.choices[0].message.content))
end = time.time()
print(end-start)