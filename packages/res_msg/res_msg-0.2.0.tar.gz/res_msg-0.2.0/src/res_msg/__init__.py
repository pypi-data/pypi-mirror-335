"""一个简单的示例包，用于演示Python虚拟环境和包管理工具。"""

import random
import requests
import sys

def greet(name="World"):
    """返回一个友好的问候。"""
    return f"Hello, {name}! 欢迎关注点赞收藏我的频道"

def get_python_version():
    """返回格式化的Python版本号。"""
    version = sys.version.split()[0]  # 只获取版本号部分，如 "3.11.11"
    return version

def get_simple_api():
    """调用一个简单的公共API - httpbin，它会返回我们发送的数据"""
    
    # 定义一些本地名言作为备份
    quotes = [
        "生活就像骑自行车，要保持平衡就要保持运动。 — 爱因斯坦",
        "人生最大的荣耀不在于永不跌倒，而在于每次跌倒后都能爬起来。 — 纳尔逊·曼德拉",
        "成功不是最终的，失败也不是致命的，重要的是继续前进的勇气。 — 温斯顿·丘吉尔"
    ]
    
    try:
        response = requests.get("https://httpbin.org/get", params={"message": "Hello from res-msg!"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"API调用成功! 发送的消息: {data['args']['message']}"
        else:
            return f"API调用失败，状态码: {response.status_code}，使用本地名言代替: {random.choice(quotes)}"
    except Exception as e:
        # 如果API调用失败，返回本地名言
        return f"API调用异常: {str(e)}，使用本地名言代替: {random.choice(quotes)}" 