from flask import Flask, request, jsonify
import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer

model_name = "/Users/luozhiling/models/xyan3b"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

# 初始化 Flask 应用
app = Flask(__name__)

# 加载模型和 tokenizer
#model_name = "/Users/luozhiling/models/xyan3b"  # 或者使用其他模型，例如 "EleutherAI/gpt-neo-2.7B"



@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    # 获取请求中的数据
    input_data = request.json

    # 提取提示（prompt）
    messages = input_data.get('messages', [])

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    prompt = messages[-1]['content']  # 假设使用最后一个消息的内容

    # 编码输入并生成响应
    inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
    outputs = model.generate(inputs['input_ids'], max_length=150, num_return_sequences=1, do_sample=True)

    # 解码生成的文本
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

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

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 监听所有可用的网络接口
