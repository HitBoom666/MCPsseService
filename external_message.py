#!/usr/bin/env python3
"""
外部消息推送测试脚本
用于测试向AI聊天界面发送外部消息的功能
"""

import requests
import json
import time
import random
from datetime import datetime

# 配置
WEB_SERVER_URL = "http://localhost:5000"  # 修改为您的Web服务器地址
EXTERNAL_MESSAGE_API = f"{WEB_SERVER_URL}/api/external-message"

def send_external_message(message, sender="算法系统", message_type="info"):
    """
    发送外部消息到聊天界面
    
    Args:
        message (str): 消息内容
        sender (str): 发送者名称
        message_type (str): 消息类型 (info, success, warning, error)
    
    Returns:
        dict: 响应结果
    """
    data = {
        "message": message,
        "sender": sender,
        "type": message_type,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(EXTERNAL_MESSAGE_API, json=data, timeout=10)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ 消息发送成功: {result['message']}")
            print(f"   消息ID: {result['message_id']}")
        else:
            print(f"❌ 消息发送失败: {result.get('error', '未知错误')}")
            
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {WEB_SERVER_URL}")
        print("请确保Web服务器正在运行")
        return None
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return None
    except Exception as e:
        print(f"❌ 发送消息时出错: {str(e)}")
        return None

def demo_algorithm_results():
    """演示算法结果推送"""
    print("🔬 模拟算法运行...")
    
    # 模拟算法开始
    send_external_message(
        "深度学习模型训练已开始\n- 数据集: ImageNet\n- 模型: ResNet-50\n- 预计用时: 2小时",
        sender="深度学习系统",
        message_type="info"
    )
    
    time.sleep(2)
    
    # 模拟算法进度更新
    for epoch in [10, 20, 30]:
        progress_message = f"""训练进度更新:
        
**Epoch {epoch}/50 完成**
- 训练准确率: {85 + random.randint(0, 10):.1f}%
- 验证准确率: {82 + random.randint(0, 8):.1f}%
- 损失值: {0.5 - epoch * 0.01:.3f}
- 剩余时间: {90 - epoch * 2} 分钟"""
        
        send_external_message(
            progress_message,
            sender="深度学习系统",
            message_type="success"
        )
        time.sleep(1)
    
    # 模拟算法完成
    final_result = """🎉 模型训练完成！

**最终结果:**
- 最佳验证准确率: 94.2%
- 最佳模型保存至: /models/resnet50_best.pth
- 训练总时长: 1小时45分钟
- 总迭代次数: 50 epochs

**性能指标:**
- Top-1 准确率: 94.2%
- Top-5 准确率: 98.1%
- 模型大小: 97.8 MB
- 推理速度: 156 FPS (GTX 3080)

模型已自动部署到生产环境 🚀"""
    
    send_external_message(
        final_result,
        sender="深度学习系统",
        message_type="success"
    )

def demo_system_monitoring():
    """演示系统监控消息"""
    print("📊 模拟系统监控...")
    
    # 警告消息
    send_external_message(
        "⚠️ 系统资源警告\n\n- CPU使用率: 85%\n- 内存使用率: 78%\n- 磁盘空间: 仅剩15GB\n\n建议及时清理临时文件",
        sender="系统监控",
        message_type="warning"
    )
    
    time.sleep(2)
    
    # 错误消息
    send_external_message(
        "❌ 数据库连接异常\n\n错误详情:\n- 连接池已满 (20/20)\n- 响应时间超时 (>30s)\n- 错误代码: DB_CONNECTION_TIMEOUT\n\n请检查数据库服务器状态",
        sender="数据库监控",
        message_type="error"
    )
    
    time.sleep(2)
    
    # 恢复消息
    send_external_message(
        "✅ 系统状态已恢复正常\n\n当前状态:\n- 数据库连接: 正常\n- 响应时间: 150ms\n- 所有服务运行正常",
        sender="系统监控",
        message_type="success"
    )

def demo_data_analysis():
    """演示数据分析结果"""
    print("📈 模拟数据分析...")
    
    analysis_result = """📊 **用户行为分析报告**

**分析时间段:** 2024-01-01 至 2024-01-31

**关键指标:**
- 总用户数: 15,623 (+12.3% vs 上月)
- 活跃用户数: 8,947 (+8.7% vs 上月)
- 平均会话时长: 14.2分钟 (+2.1分钟)
- 页面浏览量: 127,456 (+15.6% vs 上月)

**用户行为洞察:**
1. 🕒 **峰值时段:** 19:00-21:00 (用户活跃度最高)
2. 📱 **设备偏好:** 移动端占比68.4% (持续上升)
3. 🌍 **地域分布:** 一线城市用户占比54.2%
4. ⏱️ **停留时长:** 首页平均停留3.2分钟

**建议措施:**
- 在峰值时段投放更多内容
- 优化移动端用户体验
- 针对一线城市用户推出专属服务

**数据来源:** Google Analytics + 用户行为埋点
**分析模型:** 机器学习聚类分析"""

    send_external_message(
        analysis_result,
        sender="数据分析系统",
        message_type="info"
    )

def interactive_mode():
    """交互式发送消息"""
    print("🎮 进入交互模式 (输入 'quit' 退出)")
    print("-" * 50)
    
    while True:
        try:
            message = input("\n💬 输入消息内容: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not message:
                print("消息不能为空")
                continue
            
            sender = input("👤 发送者名称 (默认: 用户): ").strip() or "用户"
            
            print("📋 消息类型:")
            print("1. info (信息)")
            print("2. success (成功)")
            print("3. warning (警告)")
            print("4. error (错误)")
            
            type_choice = input("选择类型 (1-4, 默认1): ").strip()
            type_map = {"1": "info", "2": "success", "3": "warning", "4": "error"}
            message_type = type_map.get(type_choice, "info")
            
            send_external_message(message, sender, message_type)
            
        except KeyboardInterrupt:
            print("\n\n👋 退出交互模式")
            break
        except Exception as e:
            print(f"❌ 输入处理错误: {str(e)}")

def main():
    """主函数"""
    print("🚀 外部消息推送测试工具")
    print("=" * 50)
    
    # 检查服务器连接
    try:
        response = requests.get(WEB_SERVER_URL, timeout=5)
        print(f"✅ Web服务器连接正常: {WEB_SERVER_URL}")
    except:
        print(f"❌ 无法连接到Web服务器: {WEB_SERVER_URL}")
        print("请确保Web服务器正在运行，并检查地址是否正确")
        return
    
    while True:
        print("\n🛠️  测试选项:")
        print("1. 模拟算法结果推送")
        print("2. 模拟系统监控消息")
        print("3. 模拟数据分析报告")
        print("4. 交互式发送消息")
        print("5. 发送单条测试消息")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ").strip()
        
        try:
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                demo_algorithm_results()
            elif choice == "2":
                demo_system_monitoring()
            elif choice == "3":
                demo_data_analysis()
            elif choice == "4":
                interactive_mode()
            elif choice == "5":
                send_external_message(
                    "这是一条测试消息，用于验证外部消息推送功能是否正常工作。\n\n当前时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    sender="测试系统",
                    message_type="info"
                )
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断")
            break
        except Exception as e:
            print(f"❌ 执行时出错: {str(e)}")

if __name__ == "__main__":
    main() 