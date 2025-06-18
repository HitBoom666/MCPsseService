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
import json
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
    处理输入的字符串数据（保留用于向后兼容）
    
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

def process_json_data(json_data):
    """
    处理JSON格式的输入数据
    
    参数:
    json_data: JSON字符串或字典，格式为:
    {
        "x_data": ["类别1", "类别2", "类别3"],
        "series": [
            {
                "name": "系列1",
                "data": [10, 20, 30],
                "type": "bar",
                "y_unit": "数量",
                "color": "#00ff9f"
            },
            {
                "name": "系列2", 
                "data": [15, 25, 35],
                "type": "line",
                "y_unit": "百分比",
                "color": "#ff6b6b",
                "marker": "o"
            }
        ]
    }
    """
    try:
        # 如果输入是字符串，解析为字典
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        # 验证必需字段
        if 'x_data' not in data or 'series' not in data:
            raise ValueError("JSON数据必须包含'x_data'和'series'字段")
            
        x_values = data['x_data']
        series_list = data['series']
        
        # 验证数据长度一致性
        for series in series_list:
            if len(series['data']) != len(x_values):
                raise ValueError(f"系列'{series['name']}'的数据长度与x轴数据长度不匹配")
                
        return x_values, series_list
        
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise ValueError(f"数据处理错误: {str(e)}")

def get_y_axis_groups(series_list):
    """
    根据y轴单位对数据系列进行分组
    
    返回: (left_axis_series, right_axis_series, left_unit, right_unit)
    """
    y_units = list(set([series.get('y_unit', '数值') for series in series_list]))
    
    if len(y_units) > 2:
        raise ValueError("最多只支持两个不同的y轴单位")
    
    left_unit = y_units[0]
    right_unit = y_units[1] if len(y_units) > 1 else None
    
    left_axis_series = [s for s in series_list if s.get('y_unit', '数值') == left_unit]
    right_axis_series = [s for s in series_list if s.get('y_unit', '数值') == right_unit] if right_unit else []
    
    return left_axis_series, right_axis_series, left_unit, right_unit

def draw_series_on_axis(ax, x_values, series_list, colors_palette, bar_positions=None):
    """
    在指定的坐标轴上绘制数据系列
    
    参数:
    ax: matplotlib坐标轴对象
    x_values: x轴数据
    series_list: 数据系列列表
    colors_palette: 颜色调色板
    bar_positions: 柱状图位置偏移（用于多个柱状图并排显示）
    
    返回: 图例句柄列表
    """
    legend_handles = []
    bar_width = 0.35  # 柱状图宽度
    
    # 计算柱状图的位置偏移
    if bar_positions is None:
        bar_count = sum(1 for s in series_list if s.get('type', 'bar') == 'bar')
        bar_positions = np.arange(len(x_values))
        if bar_count > 1:
            bar_offset = bar_width / bar_count
        else:
            bar_offset = 0
    else:
        bar_offset = bar_width / 2
    
    bar_index = 0
    
    for i, series in enumerate(series_list):
        series_type = series.get('type', 'bar')
        series_name = series.get('name', f'系列{i+1}')
        series_data = series['data']
        series_color = series.get('color', colors_palette[i % len(colors_palette)])
        
        if series_type == 'bar':
            # 绘制柱状图
            x_pos = bar_positions + (bar_index - (sum(1 for s in series_list if s.get('type', 'bar') == 'bar') - 1) / 2) * bar_offset
            bars = ax.bar(x_pos, series_data, bar_width * 0.8, 
                         label=series_name, color=series_color, alpha=0.8)
            
            # 添加柱状图边框效果
            for bar in bars:
                bar.set_edgecolor('white')
                bar.set_linewidth(0.5)
            
            # 在柱子上方显示数值
            for j, (bar, value) in enumerate(zip(bars, series_data)):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(series_data) * 0.01,
                       f'{value}', ha='center', va='bottom', fontsize=9, color='white')
            
            legend_handles.append(bars[0])
            bar_index += 1
            
        elif series_type == 'line':
            # 绘制折线图
            marker = series.get('marker', 'o')
            line_width = series.get('line_width', 2)
            
            line = ax.plot(bar_positions, series_data, color=series_color, 
                          marker=marker, linestyle='-', linewidth=line_width, 
                          label=series_name, markersize=6)[0]
            
            # 添加发光效果
            line.set_path_effects([patheffects.withStroke(linewidth=line_width+2, 
                                                         foreground=series_color, alpha=0.3)])
            
            # 在数据点上方显示数值
            for j, (x, y) in enumerate(zip(bar_positions, series_data)):
                ax.text(x, y + max(series_data) * 0.02, f'{y}', 
                       ha='center', va='bottom', fontsize=9, color='white')
            
            legend_handles.append(line)
    
    return legend_handles

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

def draw_chart(data_input, title="多系列图表", x_label="X轴"):
    print(f"[DEBUG] draw_chart被调用，参数: data_input={data_input}, title={title}, x_label={x_label}")
    try:
        # 检查输入格式并处理数据
        if isinstance(data_input, (str, dict)):
            # JSON格式
            x_values, series_list = process_json_data(data_input)
        elif isinstance(data_input, tuple) and len(data_input) >= 2:
            # 向后兼容：旧的字符串格式
            x_str, y_str = data_input[0], data_input[1]
            chart_type = data_input[2] if len(data_input) > 2 else 'bar'
            
            x_values, y_values = process_input_data(x_str, y_str)
            series_list = [{
                'name': '数据系列',
                'data': y_values,
                'type': chart_type,
                'y_unit': '数值',
            }]
        else:
            raise ValueError("不支持的数据输入格式")
        
        # 按y轴单位分组数据系列
        left_axis_series, right_axis_series, left_unit, right_unit = get_y_axis_groups(series_list)
        
        # 从配置获取图表参数
        figsize = config.charts_config.get('figsize', [14, 8])
        background_color = config.charts_config.get('background_color', '#1a1a1a')
        
        # 创建图形和坐标轴
        fig, ax1 = plt.subplots(figsize=figsize, facecolor=background_color)
        ax1.set_facecolor(background_color)
        
        # 创建颜色调色板
        colors_palette = ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', 
                         '#eb4d4b', '#6c5ce7', '#a29bfe', '#fd79a8']
        
        # 设置x轴位置
        x_positions = np.arange(len(x_values))
        
        # 绘制左y轴数据
        legend_handles = []
        if left_axis_series:
            handles = draw_series_on_axis(ax1, x_values, left_axis_series, colors_palette)
            legend_handles.extend(handles)
            
            # 设置左y轴
            ax1.set_ylabel(left_unit, fontsize=12, labelpad=10, color='white')
            ax1.tick_params(axis='y', labelcolor='white')
        
        # 绘制右y轴数据（如果存在）
        ax2 = None
        if right_axis_series:
            ax2 = ax1.twinx()
            ax2.set_facecolor(background_color)
            
            # 为右y轴数据使用不同的颜色起始位置
            right_colors = colors_palette[len(left_axis_series):]
            handles = draw_series_on_axis(ax2, x_values, right_axis_series, right_colors, x_positions)
            legend_handles.extend(handles)
            
            # 设置右y轴
            ax2.set_ylabel(right_unit, fontsize=12, labelpad=10, color='white')
            ax2.tick_params(axis='y', labelcolor='white')
            
            # 设置右y轴边框颜色
            for spine in ax2.spines.values():
                spine.set_color('#333333')
                spine.set_linewidth(1.5)
        
        # 设置x轴
        ax1.set_xticks(x_positions)
        ax1.set_xticklabels(x_values)
        ax1.set_xlabel(x_label, fontsize=12, labelpad=10, color='white')
        
        # 设置标题
        ax1.set_title(title, fontsize=16, pad=20, color='white', fontweight='bold')
        
        # 设置刻度标签颜色
        ax1.tick_params(colors='white')
        
        # 添加网格线
        ax1.grid(True, linestyle='--', alpha=0.2, color='white')
        ax1.set_axisbelow(True)
        
        # 设置边框
        for spine in ax1.spines.values():
            spine.set_color('#333333')
            spine.set_linewidth(1.5)
        
        # 添加图例
        if legend_handles:
            legend = ax1.legend(handles=legend_handles, loc='upper left', 
                              fancybox=True, shadow=True, framealpha=0.9,
                              facecolor='#2a2a2a', edgecolor='white')
            legend.get_frame().set_facecolor('#2a2a2a')
            for text in legend.get_texts():
                text.set_color('white')
        
        # 自动调整X轴标签
        adjust_x_labels(ax1, x_values)
        
        # 自动调整布局
        plt.tight_layout()
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ensure_output_dir()
        filename = f"mixed_chart_{timestamp}.png"
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

# 为了向后兼容，保留旧的函数签名
def draw_chart_legacy(x_str, y_str, chart_type='bar', title="图表", x_label="X轴", y_label="Y轴", color='#00ff9f', bar_width=0.5, marker='o'):
    """
    旧版本的draw_chart方法（向后兼容）
    """
    # 将旧参数转换为新的JSON格式
    json_data = {
        "x_data": [x.strip() for x in x_str.split(',')],
        "series": [{
            "name": "数据系列",
            "data": [float(y.strip()) for y in y_str.split(',')],
            "type": chart_type,
            "y_unit": y_label,
            "color": color,
            "marker": marker
        }]
    }
    return draw_chart(json_data, title=title, x_label=x_label)

# 使用示例
if __name__ == "__main__":
    # 示例1：多系列混合图表
    json_data = {
        "x_data": ["1月", "2月", "3月", "4月", "5月"],
        "series": [
            {
                "name": "销售额",
                "data": [120, 150, 180, 200, 160],
                "type": "bar",
                "y_unit": "万元",
                "color": "#00ff9f"
            },
            {
                "name": "增长率",
                "data": [15, 25, 20, 35, 30],
                "type": "line",
                "y_unit": "百分比",
                "color": "#ff6b6b",
                "marker": "o"
            },
            {
                "name": "成本",
                "data": [80, 90, 110, 120, 100],
                "type": "bar",
                "y_unit": "万元",
                "color": "#4ecdc4"
            }
        ]
    }
    
    result = draw_chart(
        json_data,
        title="销售数据综合分析",
        x_label="月份"
    )
    print(result)
    
    # 示例2：向后兼容的用法
    x_str = "2024年第一季度,2024年第二季度,2024年第三季度,2024年第四季度"
    y_str = "10,20,15,25"
    
    result = draw_chart(
        (x_str, y_str, 'line'),
        title="季度数据趋势",
        x_label="时间"
    )
    print(result)