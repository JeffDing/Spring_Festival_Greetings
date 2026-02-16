# -*- coding: utf-8 -*-
"""
春节祝福语生成应用 - Flask后端
"""

import os
import re
import json
import requests
from flask import Flask, render_template, request, jsonify
from lunar_utils import get_lunar_info

app = Flask(__name__)

# 从环境变量获取配置
API_URL = os.environ.get('API_URL')
MODEL_NAME = os.environ.get('MODEL_NAME')
API_KEY = os.environ.get('API_KEY')


def clean_markdown(text, is_weibo=False):
    """
    清除文本中的markdown语法和emoji表情，返回纯文字内容
    :param text: 包含markdown语法或emoji的文本
    :param is_weibo: 是否为微博风格，如果是则去掉包含##关键词的行
    :return: 纯文字内容
    """
    if not text:
        return text
    
    # 如果是微博风格，去掉包含##关键词的整行
    if is_weibo:
        # 匹配包含 ##xxx## 或 ## xxx ## 格式的整行并删除
        text = re.sub(r'^.*##.*##.*$', '', text, flags=re.MULTILINE)
        # 也匹配单独的 ##xxx 格式（没有闭合的）
        text = re.sub(r'^.*##.*$', '', text, flags=re.MULTILINE)
    
    # 清除加粗语法 **text** 或 __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # 清除斜体语法 *text* 或 _text_
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # 清除删除线语法 ~~text~~
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # 清除标题语法 # ## ### 等
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 清除链接语法 [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # 清除图片语法 ![alt](url)
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
    
    # 清除代码块语法 ```code```
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # 清除行内代码语法 `code`
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # 清除引用语法 > text
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # 清除列表语法 - * + 开头的列表项
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    
    # 清除有序列表语法 1. 2. 等
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 清除水平线语法 --- *** ___
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # 清除emoji表情符号
    # 使用精确的Unicode范围，避免匹配中文字符
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 表情符号
        "\U0001F300-\U0001F5FF"  # 符号和象形文字
        "\U0001F680-\U0001F6FF"  # 交通和地图符号
        "\U0001F1E0-\U0001F1FF"  # 旗帜
        "\U0001F900-\U0001F9FF"  # 补充符号和象形文字
        "\U0001FA00-\U0001FA6F"  # 国际象棋符号
        "\U0001FA70-\U0001FAFF"  # 符号和象形文字扩展A
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # 清除多余的空行，保留段落结构
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


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
    elif category == "拜年词":
        length_limit = "字数控制在8-16字，简短精巧，语言凝练，适合拜年问候"

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
            # 清除markdown语法和emoji，返回纯文字
            # 如果是微博风格，传入is_weibo=True以去掉##关键词行
            is_weibo = (category == "微博")
            blessing = clean_markdown(blessing, is_weibo=is_weibo)
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
