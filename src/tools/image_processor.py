import requests
import io
from PIL import Image

def get_image_from_esp32():
    """从ESP32摄像头获取图像"""
    try:
        response = requests.get('http://192.168.31.18/capture')
        if response.status_code == 200:
            return response.content
        else:
            print(f"获取图像失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"获取图像错误: {e}")
        return None

def get_image_description(img_bytes):
    # 准备要发送的数据
    files = {
        'file': ('image.jpg', img_bytes, 'image/jpeg')
    }
    
    data = {
        'question': "请描述一下图片"
    }
    
    # 发送POST请求
    response = requests.post('http://api.xiaozhi.me/mcp/vision/explain', files=files, data=data)
    return response.json() 