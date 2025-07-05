#!/usr/bin/env python3
"""
HTML动态图表演示脚本
展示各种图表类型和功能
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.tools.html_chart_utils import draw_html_chart
    print("✅ HTML图表工具导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保 src/tools/html_chart_utils.py 文件存在")
    sys.exit(1)

def demo_sales_chart():
    """演示销售数据图表"""
    print("\n📊 生成销售数据图表...")
    
    sales_data = {
        "x_data": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "series": [
            {
                "name": "销售额",
                "data": [120, 150, 180, 200, 160, 190],
                "type": "bar",
                "y_unit": "万元",
                "color": "#00ff9f"
            },
            {
                "name": "增长率",
                "data": [15, 25, 20, 35, 30, 28],
                "type": "line",
                "y_unit": "百分比",
                "color": "#ff6b6b"
            },
            {
                "name": "成本",
                "data": [80, 90, 110, 120, 100, 115],
                "type": "bar",
                "y_unit": "万元",
                "color": "#4ecdc4"
            }
        ]
    }
    
    result = draw_html_chart(
        sales_data,
        title="📈 销售数据动态分析",
        x_label="月份"
    )
    print(f"✅ {result}")
    return result

def demo_performance_chart():
    """演示性能监控图表"""
    print("\n🖥️ 生成性能监控图表...")
    
    performance_data = {
        "x_data": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "series": [
            {
                "name": "CPU使用率",
                "data": [25, 30, 65, 80, 75, 45],
                "type": "line",
                "y_unit": "百分比",
                "color": "#ff6b6b"
            },
            {
                "name": "内存使用率",
                "data": [40, 42, 58, 70, 68, 50],
                "type": "line",
                "y_unit": "百分比",
                "color": "#4ecdc4"
            },
            {
                "name": "网络流量",
                "data": [100, 80, 200, 350, 300, 150],
                "type": "bar",
                "y_unit": "MB/s",
                "color": "#45b7d1"
            }
        ]
    }
    
    result = draw_html_chart(
        performance_data,
        title="🖥️ 系统性能监控",
        x_label="时间"
    )
    print(f"✅ {result}")
    return result

def demo_user_analytics():
    """演示用户分析图表"""
    print("\n👥 生成用户分析图表...")
    
    user_data = {
        "x_data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "series": [
            {
                "name": "新用户",
                "data": [120, 132, 101, 134, 90, 230, 210],
                "type": "bar",
                "y_unit": "人数",
                "color": "#00ff9f"
            },
            {
                "name": "活跃用户",
                "data": [850, 920, 880, 950, 1200, 1400, 1300],
                "type": "line",
                "y_unit": "人数",
                "color": "#ff6b6b"
            },
            {
                "name": "留存率",
                "data": [85, 87, 82, 89, 92, 88, 90],
                "type": "line",
                "y_unit": "百分比",
                "color": "#f9ca24"
            }
        ]
    }
    
    result = draw_html_chart(
        user_data,
        title="👥 用户行为分析",
        x_label="星期"
    )
    print(f"✅ {result}")
    return result

def demo_simple_chart():
    """演示简单图表（向后兼容）"""
    print("\n📊 生成简单图表...")
    
    # 使用旧格式（向后兼容）
    x_data = "产品A,产品B,产品C,产品D,产品E"
    y_data = "45,38,52,61,33"
    
    result = draw_html_chart(
        (x_data, y_data, "bar"),
        title="📊 产品销量对比",
        x_label="产品"
    )
    print(f"✅ {result}")
    return result

def demo_trend_chart():
    """演示趋势图表"""
    print("\n📈 生成趋势图表...")
    
    trend_data = {
        "x_data": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
            {
                "name": "收入",
                "data": [2800, 3200, 3800, 4200],
                "type": "line",
                "y_unit": "万元",
                "color": "#00ff9f"
            },
            {
                "name": "支出",
                "data": [2200, 2600, 2900, 3100],
                "type": "line",
                "y_unit": "万元",
                "color": "#ff6b6b"
            },
            {
                "name": "利润",
                "data": [600, 600, 900, 1100],
                "type": "bar",
                "y_unit": "万元",
                "color": "#4ecdc4"
            }
        ]
    }
    
    result = draw_html_chart(
        trend_data,
        title="📈 季度财务趋势",
        x_label="季度"
    )
    print(f"✅ {result}")
    return result

def demo_pie_chart():
    """演示饼图"""
    print("\n🥧 生成饼图...")
    
    pie_data = {
        "chart_type": "pie",
        "data": [
            {"name": "移动端", "value": 335},
            {"name": "PC端", "value": 310},
            {"name": "平板", "value": 234},
            {"name": "其他", "value": 135}
        ]
    }
    
    result = draw_html_chart(
        pie_data,
        title="🥧 用户设备分布"
    )
    print(f"✅ {result}")
    return result

def demo_rose_chart():
    """演示南丁格尔图"""
    print("\n🌹 生成南丁格尔图...")
    
    rose_data = {
        "chart_type": "rose",
        "data": [
            {"name": "研发", "value": 40},
            {"name": "市场", "value": 25},
            {"name": "销售", "value": 20},
            {"name": "运营", "value": 15}
        ]
    }
    
    result = draw_html_chart(
        rose_data,
        title="🌹 部门人员分布"
    )
    print(f"✅ {result}")
    return result

def demo_radar_chart():
    """演示雷达图"""
    print("\n🎯 生成雷达图...")
    
    radar_data = {
        "chart_type": "radar",
        "indicators": [
            {"name": "性能", "max": 100},
            {"name": "易用性", "max": 100},
            {"name": "稳定性", "max": 100},
            {"name": "功能", "max": 100},
            {"name": "成本", "max": 100}
        ],
        "series": [
            {
                "name": "产品A",
                "data": [85, 90, 88, 92, 70]
            },
            {
                "name": "产品B",
                "data": [78, 85, 95, 80, 85]
            }
        ]
    }
    
    result = draw_html_chart(
        radar_data,
        title="🎯 产品对比分析"
    )
    print(f"✅ {result}")
    return result

def demo_funnel_chart():
    """演示漏斗图"""
    print("\n📊 生成漏斗图...")
    
    funnel_data = {
        "chart_type": "funnel",
        "data": [
            {"name": "访问", "value": 1000},
            {"name": "注册", "value": 800},
            {"name": "激活", "value": 600},
            {"name": "付费", "value": 300},
            {"name": "续费", "value": 150}
        ]
    }
    
    result = draw_html_chart(
        funnel_data,
        title="📊 用户转化漏斗"
    )
    print(f"✅ {result}")
    return result

def demo_wordcloud_chart():
    """演示词云图"""
    print("\n☁️ 生成词云图...")
    
    wordcloud_data = {
        "chart_type": "wordcloud",
        "words": [
            {"name": "Python", "value": 1000},
            {"name": "JavaScript", "value": 800},
            {"name": "数据分析", "value": 700},
            {"name": "机器学习", "value": 600},
            {"name": "人工智能", "value": 500},
            {"name": "深度学习", "value": 400},
            {"name": "算法", "value": 350},
            {"name": "编程", "value": 300},
            {"name": "开发", "value": 250},
            {"name": "技术", "value": 200}
        ]
    }
    
    result = draw_html_chart(
        wordcloud_data,
        title="☁️ 技术关键词云"
    )
    print(f"✅ {result}")
    return result

def demo_heatmap_chart():
    """演示热力图"""
    print("\n🔥 生成热力图...")
    
    heatmap_data = {
        "chart_type": "heatmap",
        "x_data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "y_data": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "data": [
            [0, 0, 5], [0, 1, 1], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0],
            [1, 0, 1], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 6, 0],
            [2, 0, 2], [2, 1, 2], [2, 2, 5], [2, 3, 4], [2, 4, 2], [2, 5, 4], [2, 6, 2],
            [3, 0, 14], [3, 1, 13], [3, 2, 17], [3, 3, 23], [3, 4, 25], [3, 5, 25], [3, 6, 22],
            [4, 0, 7], [4, 1, 8], [4, 2, 12], [4, 3, 23], [4, 4, 30], [4, 5, 28], [4, 6, 26],
            [5, 0, 1], [5, 1, 1], [5, 2, 2], [5, 3, 4], [5, 4, 7], [5, 5, 16], [5, 6, 15]
        ],
        "max_value": 30
    }
    
    result = draw_html_chart(
        heatmap_data,
        title="🔥 用户活跃度热力图"
    )
    print(f"✅ {result}")
    return result

def demo_sankey_chart():
    """演示桑基图"""
    print("\n🌊 生成桑基图...")
    
    sankey_data = {
        "chart_type": "sankey",
        "nodes": [
            {"name": "访问用户"},
            {"name": "注册用户"},
            {"name": "活跃用户"},
            {"name": "付费用户"},
            {"name": "流失用户"},
            {"name": "新用户"},
            {"name": "老用户"}
        ],
        "links": [
            {"source": "访问用户", "target": "注册用户", "value": 300},
            {"source": "访问用户", "target": "流失用户", "value": 200},
            {"source": "注册用户", "target": "活跃用户", "value": 200},
            {"source": "注册用户", "target": "流失用户", "value": 100},
            {"source": "活跃用户", "target": "付费用户", "value": 80},
            {"source": "活跃用户", "target": "新用户", "value": 70},
            {"source": "活跃用户", "target": "老用户", "value": 50}
        ]
    }
    
    result = draw_html_chart(
        sankey_data,
        title="🌊 用户流向分析"
    )
    print(f"✅ {result}")
    return result

def demo_graph_chart():
    """演示关系图"""
    print("\n🕸️ 生成关系图...")
    
    graph_data = {
        "chart_type": "graph",
        "nodes": [
            {"id": "用户", "name": "用户", "symbolSize": 50, "category": 0},
            {"id": "产品", "name": "产品", "symbolSize": 40, "category": 1},
            {"id": "订单", "name": "订单", "symbolSize": 35, "category": 2},
            {"id": "支付", "name": "支付", "symbolSize": 30, "category": 2},
            {"id": "物流", "name": "物流", "symbolSize": 25, "category": 3},
            {"id": "评价", "name": "评价", "symbolSize": 20, "category": 0}
        ],
        "links": [
            {"source": "用户", "target": "产品", "value": 1},
            {"source": "用户", "target": "订单", "value": 2},
            {"source": "订单", "target": "支付", "value": 3},
            {"source": "订单", "target": "物流", "value": 2},
            {"source": "用户", "target": "评价", "value": 1},
            {"source": "产品", "target": "评价", "value": 1}
        ],
        "categories": [
            {"name": "用户相关"},
            {"name": "产品相关"},
            {"name": "交易相关"},
            {"name": "服务相关"}
        ]
    }
    
    result = draw_html_chart(
        graph_data,
        title="🕸️ 业务关系图"
    )
    print(f"✅ {result}")
    return result

def demo_map_chart():
    """演示地图"""
    print("\n🗺️ 生成地图...")
    
    map_data = {
        "chart_type": "map",
        "map_type": "china",
        "regions": [
            {"name": "北京", "value": 177},
            {"name": "天津", "value": 42},
            {"name": "河北", "value": 102},
            {"name": "山西", "value": 81},
            {"name": "内蒙古", "value": 47},
            {"name": "辽宁", "value": 67},
            {"name": "吉林", "value": 82},
            {"name": "黑龙江", "value": 123},
            {"name": "上海", "value": 24},
            {"name": "江苏", "value": 92},
            {"name": "浙江", "value": 114},
            {"name": "安徽", "value": 109},
            {"name": "福建", "value": 116},
            {"name": "江西", "value": 91},
            {"name": "山东", "value": 119},
            {"name": "河南", "value": 137},
            {"name": "湖北", "value": 116},
            {"name": "湖南", "value": 114},
            {"name": "重庆", "value": 91},
            {"name": "四川", "value": 125},
            {"name": "贵州", "value": 62},
            {"name": "云南", "value": 83},
            {"name": "西藏", "value": 9},
            {"name": "陕西", "value": 80},
            {"name": "甘肃", "value": 56},
            {"name": "青海", "value": 10},
            {"name": "宁夏", "value": 18},
            {"name": "新疆", "value": 67},
            {"name": "广东", "value": 123},
            {"name": "广西", "value": 59},
            {"name": "海南", "value": 14}
        ],
        "scatter_data": [
            {"name": "北京", "value": [116.46, 39.92, 95]},
            {"name": "上海", "value": [121.48, 31.22, 85]},
            {"name": "广州", "value": [113.23, 23.16, 78]},
            {"name": "深圳", "value": [114.07, 22.62, 75]},
            {"name": "西安", "value": [108.95, 34.27, 68]},
            {"name": "重庆", "value": [106.54, 29.59, 65]}
        ],
        "max_value": 200
    }
    
    result = draw_html_chart(
        map_data,
        title="🗺️ 全国数据分布地图"
    )
    print(f"✅ {result}")
    return result

def main():
    """主演示函数"""
    print("🚀 HTML动态图表演示")
    print("=" * 50)
    print("本演示将展示多种图表类型和功能:")
    print("- 混合图表（柱状图 + 折线图）")
    print("- 双Y轴支持")
    print("- 动态动画效果")
    print("- 交互式操作")
    print("- 主题切换")
    print("- 图片下载")
    print("=" * 50)
    
    demos = [
        ("销售数据分析", demo_sales_chart),
        ("系统性能监控", demo_performance_chart),
        ("用户行为分析", demo_user_analytics),
        ("产品销量对比", demo_simple_chart),
        ("季度财务趋势", demo_trend_chart),
        ("饼图演示", demo_pie_chart),
        ("南丁格尔图演示", demo_rose_chart),
        ("雷达图演示", demo_radar_chart),
        ("漏斗图演示", demo_funnel_chart),
        ("词云图演示", demo_wordcloud_chart),
        ("热力图演示", demo_heatmap_chart),
        ("桑基图演示", demo_sankey_chart),
        ("关系图演示", demo_graph_chart),
        ("地图演示", demo_map_chart)
    ]
    
    print("\n🎯 选择演示类型:")
    print("=== 基础图表 ===")
    for i in range(5):
        name, _ = demos[i]
        print(f"{i+1}. {name}")
    
    print("\n=== 高级图表 ===")
    for i in range(5, len(demos)):
        name, _ = demos[i]
        print(f"{i+1}. {name}")
    
    print(f"\n{len(demos)+1}. 运行所有演示")
    print("0. 退出")
    
    while True:
        choice = input(f"\n请选择 (0-{len(demos)+1}): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == str(len(demos)+1):
            print("\n🎬 运行所有演示...")
            for i, (name, demo_func) in enumerate(demos, 1):
                print(f"\n[{i}/{len(demos)}] {name}")
                try:
                    demo_func()
                    time.sleep(1)  # 给用户时间查看结果
                except Exception as e:
                    print(f"❌ 演示失败: {e}")
            print("\n🎉 所有演示完成！")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            idx = int(choice) - 1
            name, demo_func = demos[idx]
            print(f"\n🎬 运行演示: {name}")
            try:
                demo_func()
                print(f"\n✅ 演示 '{name}' 完成！")
            except Exception as e:
                print(f"❌ 演示失败: {e}")
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main() 