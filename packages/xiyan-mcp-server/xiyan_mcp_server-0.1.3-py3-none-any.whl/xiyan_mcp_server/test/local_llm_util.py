from openai import BaseModel
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

response = {
    'id': 'chatcmpl-1',
    'object': 'chat.completion',
    'created': 1234567890,  # 当前时间的时间戳，您可以用实际时间戳替换
    'model': "ss",
    'choices': [{
        'index': 0,
        'message': {
            "content": "helloworld"
        },
        'finish_reason': 'length'
    }]
}
model='xyan3b'
response = '{"id": "chatcmpl-1","object": "hat.completion","created": 1234567890,"model": %s,"choices": [{"index": 0,"message": {"content": "helloworld"},"finish_reason": "length"}]}' % (model)

print(response)
message=BaseModel()
message.content = 'helloworld'
choice = BaseModel()
choice.message=message
chat_completions = BaseModel()
chat_completions.id='chatcmpl-1'
chat_completions.object='chat.completion'
chat_completions.created=1234567890
chat_completions.choices=[choice]
chat_completions.model=model

print(chat_completions.choices[0].message.content)