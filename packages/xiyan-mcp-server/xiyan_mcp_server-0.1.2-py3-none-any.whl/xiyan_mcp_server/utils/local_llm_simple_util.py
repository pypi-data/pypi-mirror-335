from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

import torch # require torch==2.2.2,accelerate>=0.26.0,numpy=2.2.3
model_path = "/Users/luozhiling/models/xyan3b"
model_name = 'xyan3b'
local_model = AutoModelForCausalLM.from_pretrained(model_path, device_map='cpu', torch_dtype=torch.float32)
local_tokenizer = AutoTokenizer.from_pretrained(model_path)
app = Flask(__name__)



@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    # 获取请求中的数据
    input_data = request.json

    # 提取提示（prompt）
    messages = input_data.get('messages', [])

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    prompt = messages[-1]['content']  # 假设使用最后一个消息的内容

    # 编码输入并生成响应
    inputs = local_tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
    outputs = local_model.generate(inputs['input_ids'], max_length=150, num_return_sequences=1, do_sample=True)

    # 解码生成的文本
    generated_text = local_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 生成响应格式
    response = {
        'id': 'chatcmpl-1',
        'object': 'chat.completion',
        'created': 1234567890,  # 当前时间的时间戳，您可以用实际时间戳替换
        'model': model_name,
        'choices': [{
            'index': 0,
            'text': generated_text,
            'finish_reason': 'length'
        }]
    }
    print(response)
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090)  # 监听所有可用的网络接口
