from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 配置 Ollama API 地址
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # 请根据实际情况修改


@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    # 从请求中获取数据
    input_data = request.json
    messages = input_data.get('messages', [])

    if not messages or (len(messages) == 0):
        return jsonify({'error': 'Messages not provided'}), 400

    # 获取用户最后的输入
    prompt = messages[-1]['content']

    # 构建对 Ollama 的请求数据
    ollama_payload = {
        "model":"xyan3b",
        "prompt": prompt,
        "max_length": 150,  # 可选，设定生成文本的最大长度
        "temperature": 0.7  # 可选，控制生成的随机性
    }

    # 发送请求到 Ollama 模型
    response = requests.post(OLLAMA_API_URL, json=ollama_payload)

    if response.status_code != 200:
        return jsonify({'error': 'Error while communicating with Ollama model'}), response.status_code

    generated_text = response.json().get('text', '')

    # 格式化响应以与 OpenAI API 兼容
    openai_response = {
        'id': 'chatcmpl-1',
        'object': 'chat.completion',
        'created': 1234567890,  # 当前时间的时间戳
        'model': 'xyan3b',  # 具体模型名称
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': generated_text
            },
            'finish_reason': 'stop'
        }]
    }

    return jsonify(openai_response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
