# -*- coding: utf-8 -*-
"""
春节祝福语生成应用 - Flask后端
"""

import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from lunar_utils import get_lunar_info

app = Flask(__name__)

# 从环境变量获取配置
API_URL = os.environ.get('API_URL')
MODEL_NAME = os.environ.get('MODEL_NAME')
API_KEY = os.environ.get('API_KEY')


def generate_blessing(year, category, style, keyword=None):
    """
    调用ModelArts Studio API生成春节祝福语
    :param year: 年份
    :param category: 祝福语类别（朋友圈/微博/新春贺词）
    :param style: 祝福语风格（现代创新/古色古香/传统）
    :param keyword: 关键词（可选，如果提供则围绕关键词生成）
    :return: 生成的祝福语
    """
    # 获取农历信息
    lunar_info = get_lunar_info(year)

    # 根据类别设置字数限制
    length_limit = ""
    if category == "朋友圈":
        length_limit = "字数控制在50-80字左右，适合微信朋友圈发布"
    elif category == "微博":
        length_limit = "字数控制在140字以内，适合微博发布"
    elif category == "新春贺词":
        length_limit = "字数可以稍微多一点，内容更丰富，适合用于海报或贺卡"

    # 根据风格调整提示词
    style_instruction = ""
    if style == "现代创新风格":
        style_instruction = "语言要现代、活泼、有创意，可以适当使用一些网络流行语，但要保持节日氛围"
    elif style == "古色古香风格":
        style_instruction = "语言要古雅、有韵味，使用文言文或半文半白的表达方式，体现传统文化底蕴"
    elif style == "传统风格":
        style_instruction = "语言要正式、庄重，使用传统的祝福语表达方式，体现春节的传统习俗"

    # 构建关键词相关提示
    keyword_instruction = ""
    if keyword:
        keyword_instruction = f"\n5. 祝福语需要围绕关键词「{keyword}」进行创作，将关键词自然融入祝福语中"

    # 构建提示词
    system_prompt = f"""你是一位擅长创作春节祝福语的专家。请根据以下信息创作一条春节祝福语：

年份信息：{year}年是{lunar_info['lunar_year']}，生肖是{lunar_info['zodiac']}年
祝福语类别：{category}（{length_limit}）
祝福语风格：{style}（{style_instruction}）{f'关键词：{keyword}' if keyword else ''}

要求：
1. 祝福语要体现出年份特色，包含{lunar_info['zodiac']}年的元素
2. 语言要符合指定的风格要求
3. 内容要积极向上，充满节日祝福
4. {length_limit}{keyword_instruction}

请直接输出祝福语内容，不要包含任何其他解释或说明。"""

    # 调用API
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': MODEL_NAME,
        'messages': [
            {'role': 'user', 'content': system_prompt}
        ],
        'temperature': 0.8,
        'max_tokens': 500
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 提取祝福语
        if 'choices' in result and len(result['choices']) > 0:
            blessing = result['choices'][0]['message']['content'].strip()
            return blessing
        else:
            return "生成祝福语失败，请重试。"

    except Exception as e:
        print(f"API调用错误: {str(e)}")
        return f"生成祝福语时出错: {str(e)}"


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """生成祝福语接口"""
    data = request.json

    # 获取参数
    year = data.get('year', 2025)
    category = data.get('category', '朋友圈')
    style = data.get('style', '传统风格')
    keyword = data.get('keyword', '').strip() or None  # 空字符串转为None

    # 验证年份
    try:
        year = int(year)
        if year < 1900 or year > 2100:
            return jsonify({'error': '请输入1900-2100之间的年份'}), 400
    except ValueError:
        return jsonify({'error': '请输入有效的年份'}), 400

    # 生成祝福语
    blessing = generate_blessing(year, category, style, keyword)

    # 获取农历信息
    lunar_info = get_lunar_info(year)

    return jsonify({
        'blessing': blessing,
        'lunar_year': lunar_info['lunar_year'],
        'zodiac': lunar_info['zodiac']
    })


@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # 检查环境变量
    if not API_URL or not MODEL_NAME or not API_KEY:
        print("警告：环境变量未设置！")
        print(f"API_URL: {API_URL}")
        print(f"MODEL_NAME: {MODEL_NAME}")
        print(f"API_KEY: {API_KEY[:10] if API_KEY else 'None'}...")

    app.run(host='0.0.0.0', port=5000, debug=True)
