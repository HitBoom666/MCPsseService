import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import matplotlib as mpl
from matplotlib import patheffects
import os
from datetime import datetime
import subprocess
import platform
from src.config.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

# 获取配置
config = ConfigLoader()

# 设置中文字体
plt.rcParams['font.sans-serif'] = [config.charts_config.get('font_family', 'SimHei')]  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置全局样式
plt.style.use('dark_background')  # 使用深色主题

def process_input_data(x_str, y_str):
    """
    处理输入的字符串数据
    
    参数:
    x_str: 横坐标字符串，以逗号分隔
    y_str: 纵坐标字符串，以逗号分隔
    """
    try:
        # 分割字符串并转换为列表
        x_values = [x.strip() for x in x_str.split(',')]
        y_values = [float(y.strip()) for y in y_str.split(',')]
        
        # 检查数据长度是否匹配
        if len(x_values) != len(y_values):
            raise ValueError("横坐标和纵坐标的数据长度不匹配")
            
        return x_values, y_values
    except Exception as e:
        raise ValueError(f"数据格式错误: {str(e)}")

def adjust_x_labels(ax, x_values):
    """
    自动调整X轴标签
    """
    try:
        # 如果标签过多，进行旋转
        if len(x_values) > 10:
            plt.xticks(rotation=45)
        else:
            plt.xticks(rotation=0)
    except Exception as e:
        logger.warning(f"调整X轴标签失败: {str(e)}")

def ensure_output_dir():
    """
    确保输出目录存在
    """
    output_dir = config.charts_config.get('output_dir', 'charts')
    
    # 如果是相对路径，从项目根目录开始
    if not os.path.isabs(output_dir):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        output_dir = os.path.join(project_root, output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def open_image(image_path):
    """
    打开图片文件
    """
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(image_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", image_path])
        else:  # Linux
            subprocess.run(["xdg-open", image_path])
    except Exception as e:
        logger.warning(f"打开图片失败: {str(e)}")

def draw_chart(x_str, y_str, chart_type='bar', title="图表", x_label="X轴", y_label="Y轴", color='#00ff9f', bar_width=0.5, marker='o'):
    """
    绘制图表并保存为PNG
    
    参数:
    x_str: 横坐标字符串，以逗号分隔
    y_str: 纵坐标字符串，以逗号分隔
    chart_type: 图表类型，'bar'为柱状图，'line'为折线图
    title: 图表标题
    x_label: X轴标签
    y_label: Y轴标签
    color: 图表颜色
    bar_width: 柱子宽度（仅柱状图有效）
    marker: 数据点标记样式（仅折线图有效）
    """
    try:
        # 处理输入数据
        x_values, y_values = process_input_data(x_str, y_str)
        
        # 从配置获取图表参数
        figsize = config.charts_config.get('figsize', [12, 7])
        background_color = config.charts_config.get('background_color', '#1a1a1a')
        
        # 创建图形和坐标轴
        fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)
        
        # 设置背景色
        ax.set_facecolor(background_color)
        
        # 创建渐变色
        colors = plt.cm.viridis(np.linspace(0, 1, len(x_values)))
        
        # 根据图表类型绘制
        if chart_type == 'bar':
            # 绘制柱状图
            bars = ax.bar(x_values, y_values, width=bar_width, color=colors, alpha=0.8)
            # 添加发光效果
            for bar in bars:
                bar.set_edgecolor('white')
                bar.set_linewidth(0.5)
            # 在柱子上方显示数值
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height}',
                       ha='center', va='bottom', fontsize=10, color='white')
        else:  # line
            # 绘制折线图
            line = ax.plot(x_values, y_values, color=color, marker=marker, linestyle='-', linewidth=2)[0]
            # 添加发光效果
            line.set_path_effects([patheffects.withStroke(linewidth=5, foreground='#00ff9f', alpha=0.3)])
            # 在数据点上方显示数值
            for i, v in enumerate(y_values):
                ax.text(i, v, f'{v}', ha='center', va='bottom', fontsize=10, color='white')
            
        # 设置标题和轴标签
        ax.set_title(title, fontsize=16, pad=20, color='white', fontweight='bold')
        ax.set_xlabel(x_label, fontsize=12, labelpad=10, color='white')
        ax.set_ylabel(y_label, fontsize=12, labelpad=10, color='white')
        
        # 设置刻度标签颜色
        ax.tick_params(colors='white')
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.2, color='white')
        
        # 设置边框
        for spine in ax.spines.values():
            spine.set_color('#333333')
            spine.set_linewidth(1.5)
        
        # 添加科技感装饰
        # 在图表背景添加网格线
        ax.set_axisbelow(True)
        
        # 自动调整X轴标签
        adjust_x_labels(ax, x_values)
        
        # 自动调整布局
        plt.tight_layout()
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ensure_output_dir()
        filename = f"{chart_type}_chart_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # 保存图表
        dpi = config.charts_config.get('dpi', 300)
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        
        # 打开保存的图片
        open_image(filepath)
        
        # 只获取文件名
        filename = "/static/charts/"+os.path.basename(filepath)
        return f"图片保存至: {filename}，请将整个地址输出以展示图片"
    except Exception as e:
        logger.error(f"绘制图表失败: {str(e)}")
        return f"绘制图表失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    # 示例数据 - 使用较长的标签测试
    x_str = "2024年第一季度,2024年第二季度,2024年第三季度,2024年第四季度,2025年第一季度"
    y_str = "10,20,15,25,30"
    
    # 绘制柱状图
    result = draw_chart(
        x_str=x_str,
        y_str=y_str,
        chart_type='bar',
        title="季度数据统计图表",
        x_label="时间",
        y_label="数值",
        color='#00ff9f'  # 使用霓虹绿色
    )
    print(result)
    
    # 绘制折线图
    result = draw_chart(
        x_str=x_str,
        y_str=y_str,
        chart_type='line',
        title="季度数据趋势图表",
        x_label="时间",
        y_label="数值",
        color='#00ff9f'  # 使用霓虹绿色
    )
    print(result)