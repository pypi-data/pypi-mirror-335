# payload = {
#         "uia_data": None,
#         "screenshot_path": "/home/ubuntu/workspace/oymy/honkai-star-rail-menu-resized.jpg",
#         "query": "Help me to complete the mission 'Buds of Memories' in Star Rail",
#         "action_history": "Open the menu interface.",
#         "mode": "teach",
        
#         # Optional parameters
#         "user_id": "star_rail",
#         "trace_id": "default_trace",
#         "scale_factor": "1.0x",
#         "os_name": "Windows",
#         "date_time": "2024-01-01",
#         "llm_model": "gpt-4"
#     }

# import requests

# response = requests.post("http://ec2-35-81-81-242.us-west-2.compute.amazonaws.com/generate_action", json=payload)
# print(response.json())

import re

def convert_to_utf8(obj):
    # 定义正则表达式模式，匹配emoji和控制字符
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # 表情符号
        u"\U0001F300-\U0001F5FF"  # 符号和象形文字
        u"\U0001F680-\U0001F6FF"  # 交通和地图符号
        u"\U0001F1E0-\U0001F1FF"  # 国家旗帜（iOS）
        u"\U00002500-\U00002BEF"  # 中文/日文/韩文符号
        u"\U00002702-\U000027B0"  # 杂项符号
        u"\U000024C2-\U0001F251"  # 封闭字符
        u"\U0001f926-\U0001f937"  # 人物表情
        u"\U00010000-\U0010FFFF"  # 扩展字符
        u"\u2640-\u2642"          # 性别符号
        u"\u2600-\u2B55"          # 杂项符号
        u"\u200d"                 # 零宽度连字
        u"\u23cf\u23e9\u231a"     # 技术符号
        u"\ufe0f"                 # 变体选择器
        u"\u3030"                 # 波浪符
        "]+",
        flags=re.UNICODE
    )
    
    # 匹配控制字符（保留换行符\n和制表符\t）
    control_char_pattern = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]')

    def _clean_string(s):
        # 移除emoji
        s = emoji_pattern.sub(r'', s)
        # 移除控制字符（保留\n和\t）
        s = control_char_pattern.sub(r'', s)
        # 确保UTF-8编码（处理异常字符）
        return s.encode('utf-8', errors='ignore').decode('utf-8')

    if isinstance(obj, dict):
        return {convert_to_utf8(k): convert_to_utf8(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_utf8(elem) for elem in obj]
    elif isinstance(obj, str):
        return _clean_string(obj)
    else:
        return obj

data = {
    "text": "Hello 😊👋🏼",
    "list": [1, "🚀 Rocket", {"key": "Value with\tTab\nNewLine"}],
    "meta": {"🐍": "Python", "控制字符": "\x01\x02"}
}

print(convert_to_utf8(data))