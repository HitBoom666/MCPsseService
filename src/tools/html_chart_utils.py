import logging
import json
import os
from datetime import datetime
from src.config.config_loader import ConfigLoader
import subprocess
import platform

logger = logging.getLogger(__name__)

# 获取配置
config = ConfigLoader()

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

def open_html_file(file_path):
    """
    在浏览器中打开HTML文件
    """
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        logger.warning(f"打开HTML文件失败: {str(e)}")

def process_json_data(json_data):
    """
    处理JSON格式的输入数据，与原有格式兼容
    """
    try:
        # 如果输入是字符串，解析为字典
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        # 检查图表类型，不同类型有不同的验证规则
        chart_type = data.get('chart_type', 'mixed')
        
        if chart_type == 'mixed':
            # 混合图表需要x_data和series
            if 'x_data' not in data or 'series' not in data:
                raise ValueError("混合图表数据必须包含'x_data'和'series'字段")
        elif chart_type in ['pie', 'rose', 'funnel']:
            # 饼图、南丁格尔图、漏斗图需要data字段
            if 'data' not in data:
                raise ValueError(f"{chart_type}图表数据必须包含'data'字段")
        elif chart_type == 'radar':
            # 雷达图需要indicators和series
            if 'indicators' not in data or 'series' not in data:
                raise ValueError("雷达图数据必须包含'indicators'和'series'字段")
        elif chart_type == 'wordcloud':
            # 词云图需要words字段
            if 'words' not in data:
                raise ValueError("词云图数据必须包含'words'字段")
        elif chart_type == 'heatmap':
            # 热力图需要特定字段
            if 'x_data' not in data or 'y_data' not in data or 'data' not in data:
                raise ValueError("热力图数据必须包含'x_data'、'y_data'和'data'字段")
        elif chart_type in ['sankey', 'graph']:
            # 桑基图和关系图需要nodes和links
            if 'nodes' not in data or 'links' not in data:
                raise ValueError(f"{chart_type}图表数据必须包含'nodes'和'links'字段")
        elif chart_type == 'map':
            # 地图需要至少一种数据类型
            if not any(key in data for key in ['regions', 'scatter_data', 'heatmap_data']):
                raise ValueError("地图数据必须包含'regions'、'scatter_data'或'heatmap_data'中的至少一种")
            
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise ValueError(f"数据处理错误: {str(e)}")

def generate_echarts_config(data, title="动态图表", x_label="X轴"):
    """
    生成ECharts配置对象，支持多种图表类型
    """
    # 检查是否为特殊图表类型
    chart_type = data.get('chart_type', 'mixed')
    
    if chart_type == 'pie':
        return generate_pie_config(data, title)
    elif chart_type == 'rose':
        return generate_rose_config(data, title)
    elif chart_type == 'radar':
        return generate_radar_config(data, title)
    elif chart_type == 'funnel':
        return generate_funnel_config(data, title)
    elif chart_type == 'wordcloud':
        return generate_wordcloud_config(data, title)
    elif chart_type == 'heatmap':
        return generate_heatmap_config(data, title)
    elif chart_type == 'sankey':
        return generate_sankey_config(data, title)
    elif chart_type == 'graph':
        return generate_graph_config(data, title)
    elif chart_type == 'map':
        return generate_map_config(data, title)
    else:
        # 默认混合图表逻辑
        return generate_mixed_config(data, title, x_label)

def generate_mixed_config(data, title, x_label):
    """生成混合图表配置"""
    x_data = data['x_data']
    series_data = data['series']
    
    # 处理y轴单位分组
    y_units = list(set([series.get('y_unit', '数值') for series in series_data]))
    has_dual_axis = len(y_units) > 1
    
    # 构建series配置
    echarts_series = []
    for i, series in enumerate(series_data):
        series_config = {
            'name': series.get('name', f'系列{i+1}'),
            'type': 'bar' if series.get('type', 'bar') == 'bar' else 'line',
            'data': series['data'],
            'yAxisIndex': 0 if series.get('y_unit', '数值') == y_units[0] else 1,
            'itemStyle': {
                'color': series.get('color', ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24'][i % 5])
            },
            'animationDelay': i * 100,
        }
        
        # 为折线图添加特殊配置
        if series.get('type') == 'line':
            series_config.update({
                'smooth': True,
                'symbol': series.get('marker', 'circle'),
                'symbolSize': 8,
                'lineStyle': {
                    'width': 3,
                    'shadowColor': series.get('color', '#00ff9f'),
                    'shadowBlur': 10
                }
            })
        else:
            # 为柱状图添加特殊配置
            series_config.update({
                'barMaxWidth': 60,
                'emphasis': {
                    'itemStyle': {
                        'shadowBlur': 10,
                        'shadowOffsetX': 0,
                        'shadowColor': 'rgba(0, 0, 0, 0.5)'
                    }
                }
            })
        
        echarts_series.append(series_config)
    
    # 构建y轴配置
    y_axis_config = [{
        'type': 'value',
        'name': y_units[0],
        'nameTextStyle': {'color': '#ffffff', 'fontSize': 12},
        'axisLine': {'lineStyle': {'color': '#ffffff'}},
        'axisLabel': {'color': '#ffffff'},
        'splitLine': {'lineStyle': {'color': '#333333'}}
    }]
    
    if has_dual_axis:
        y_axis_config.append({
            'type': 'value',
            'name': y_units[1],
            'nameTextStyle': {'color': '#ffffff', 'fontSize': 12},
            'axisLine': {'lineStyle': {'color': '#ffffff'}},
            'axisLabel': {'color': '#ffffff'},
            'splitLine': {'show': False}
        })
    
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross', 'animation': True, 'crossStyle': {'color': '#999'}},
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'data': [series.get('name', f'系列{i+1}') for i, series in enumerate(series_data)],
            'textStyle': {'color': '#ffffff'},
            'top': 60, 'left': 'center'
        },
        'grid': {
            'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True,
            'backgroundColor': 'rgba(0, 0, 0, 0.1)', 'borderColor': '#333'
        },
        'xAxis': {
            'type': 'category', 'data': x_data, 'name': x_label,
            'nameTextStyle': {'color': '#ffffff', 'fontSize': 12},
            'axisLine': {'lineStyle': {'color': '#ffffff'}},
            'axisLabel': {'color': '#ffffff', 'rotate': 0 if len(max(x_data, key=len)) < 8 else 45}
        },
        'yAxis': y_axis_config,
        'series': echarts_series,
        'animationEasing': 'cubicOut',
        'animationDuration': 1000,
        'backgroundColor': '#1a1a1a'
    }

def generate_pie_config(data, title):
    """生成饼图配置"""
    pie_data = [{'name': item['name'], 'value': item['value']} for item in data['data']]
    
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'formatter': '{a} <br/>{b}: {c} ({d}%)',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'textStyle': {'color': '#ffffff'},
            'data': [item['name'] for item in pie_data]
        },
        'series': [{
            'name': title,
            'type': 'pie',
            'radius': '50%',
            'center': ['50%', '60%'],
            'data': pie_data,
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            },
            'animationType': 'scale',
            'animationEasing': 'elasticOut',
            'animationDelay': 200
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_rose_config(data, title):
    """生成南丁格尔图配置"""
    rose_data = [{'name': item['name'], 'value': item['value']} for item in data['data']]
    
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'formatter': '{a} <br/>{b}: {c} ({d}%)',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'textStyle': {'color': '#ffffff'},
            'data': [item['name'] for item in rose_data]
        },
        'series': [{
            'name': title,
            'type': 'pie',
            'radius': [30, 110],
            'center': ['50%', '60%'],
            'roseType': 'area',
            'data': rose_data,
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            },
            'animationType': 'scale',
            'animationEasing': 'elasticOut'
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_radar_config(data, title):
    """生成雷达图配置"""
    indicators = [{'name': item['name'], 'max': item.get('max', 100)} for item in data['indicators']]
    
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'data': [series['name'] for series in data['series']],
            'textStyle': {'color': '#ffffff'},
            'top': 60, 'left': 'center'
        },
        'radar': {
            'indicator': indicators,
            'name': {'textStyle': {'color': '#ffffff'}},
            'splitLine': {'lineStyle': {'color': '#333333'}},
            'splitArea': {'show': False},
            'axisLine': {'lineStyle': {'color': '#333333'}}
        },
        'series': [{
            'type': 'radar',
            'data': [
                {
                    'value': series['data'],
                    'name': series['name'],
                    'areaStyle': {'opacity': 0.3}
                } for series in data['series']
            ],
            'animationDuration': 1000
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_funnel_config(data, title):
    """生成漏斗图配置"""
    funnel_data = [{'name': item['name'], 'value': item['value']} for item in data['data']]
    
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'formatter': '{a} <br/>{b}: {c} ({d}%)',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'data': [item['name'] for item in funnel_data],
            'textStyle': {'color': '#ffffff'},
            'top': 60, 'left': 'center'
        },
        'series': [{
            'name': title,
            'type': 'funnel',
            'left': '10%',
            'top': 60,
            'width': '80%',
            'height': '80%',
            'minSize': '0%',
            'maxSize': '100%',
            'sort': 'descending',
            'gap': 2,
            'label': {
                'show': True,
                'position': 'inside',
                'color': '#ffffff'
            },
            'labelLine': {
                'length': 10,
                'lineStyle': {'width': 1, 'type': 'solid'}
            },
            'itemStyle': {
                'borderColor': '#fff',
                'borderWidth': 1
            },
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            },
            'data': funnel_data
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_wordcloud_config(data, title):
    """生成词云图配置"""
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'show': True,
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'series': [{
            'type': 'wordCloud',
            'shape': 'circle',
            'left': 'center',
            'top': 'center',
            'width': '70%',
            'height': '80%',
            'right': None,
            'bottom': None,
            'sizeRange': [12, 60],
            'rotationRange': [-90, 90],
            'rotationStep': 45,
            'gridSize': 8,
            'drawOutOfBound': False,
            'textStyle': {
                'fontFamily': 'sans-serif',
                'fontWeight': 'bold',
                'color': '#ffffff'
            },
            'emphasis': {
                'textStyle': {
                    'shadowBlur': 10,
                    'shadowColor': '#333'
                }
            },
            'data': data['words']
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_heatmap_config(data, title):
    """生成热力图配置"""
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'position': 'top',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'grid': {
            'height': '50%',
            'top': '10%'
        },
        'xAxis': {
            'type': 'category',
            'data': data['x_data'],
            'splitArea': {'show': True},
            'axisLabel': {'color': '#ffffff'}
        },
        'yAxis': {
            'type': 'category',
            'data': data['y_data'],
            'splitArea': {'show': True},
            'axisLabel': {'color': '#ffffff'}
        },
        'visualMap': {
            'min': 0,
            'max': data.get('max_value', 100),
            'calculable': True,
            'orient': 'horizontal',
            'left': 'center',
            'bottom': '15%',
            'textStyle': {'color': '#ffffff'}
        },
        'series': [{
            'name': title,
            'type': 'heatmap',
            'data': data['data'],
            'label': {
                'show': True,
                'color': '#ffffff'
            },
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            }
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_sankey_config(data, title):
    """生成桑基图配置"""
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'triggerOn': 'mousemove',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'series': [{
            'type': 'sankey',
            'layout': 'none',
            'top': 60,
            'right': '10%',
            'bottom': '10%',
            'left': '10%',
            'nodeWidth': 20,
            'nodeGap': 8,
            'draggable': True,
            'focusNodeAdjacency': True,
            'data': data['nodes'],
            'links': data['links'],
            'lineStyle': {
                'color': 'source',
                'curveness': 0.5
            },
            'label': {
                'color': '#ffffff',
                'fontFamily': 'Arial'
            },
            'emphasis': {
                'focus': 'adjacency'
            }
        }],
        'backgroundColor': '#1a1a1a'
    }

def generate_graph_config(data, title):
    """生成关系图配置"""
    return {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'}
        },
        'legend': {
            'data': data.get('categories', []),
            'textStyle': {'color': '#ffffff'},
            'top': 60, 'left': 'center'
        },
        'series': [{
            'name': title,
            'type': 'graph',
            'layout': 'force',
            'data': data['nodes'],
            'links': data['links'],
            'categories': data.get('categories', []),
            'roam': True,
            'focusNodeAdjacency': True,
            'itemStyle': {
                'borderColor': '#fff',
                'borderWidth': 1,
                'shadowBlur': 10,
                'shadowColor': 'rgba(0, 0, 0, 0.3)'
            },
            'label': {
                'show': True,
                'position': 'right',
                'formatter': '{b}',
                'color': '#ffffff'
            },
            'lineStyle': {
                'color': 'source',
                'curveness': 0.3
            },
            'emphasis': {
                'focus': 'adjacency',
                'lineStyle': {
                    'width': 10
                }
            },
            'force': {
                'repulsion': 100,
                'gravity': 0.1,
                'edgeLength': 30,
                'layoutAnimation': True
            }
        }],
        'backgroundColor': '#1a1a1a'
    }

def detect_map_type(region_names):
    """
    根据地名列表智能检测地图类型
    """
    # 省份/直辖市映射
    province_map_types = {
        '山东': 'shandong',
        '北京': 'beijing', 
        '上海': 'shanghai',
        '广东': 'guangdong',
        '四川': 'sichuan',
        '江苏': 'jiangsu',
        '浙江': 'zhejiang',
        '河北': 'hebei',
        '河南': 'henan',
        '湖北': 'hubei',
        '湖南': 'hunan',
        '安徽': 'anhui',
        '福建': 'fujian',
        '江西': 'jiangxi',
        '辽宁': 'liaoning',
        '吉林': 'jilin',
        '黑龙江': 'heilongjiang',
        '内蒙古': 'neimenggu',
        '山西': 'shanxi',
        '陕西': 'shaanxi',
        '甘肃': 'gansu',
        '青海': 'qinghai',
        '宁夏': 'ningxia',
        '新疆': 'xinjiang',
        '西藏': 'xizang',
        '云南': 'yunnan',
        '贵州': 'guizhou',
        '重庆': 'chongqing',
        '天津': 'tianjin',
        '广西': 'guangxi',
        '海南': 'hainan'
    }
    
    # 山东省城市映射
    shandong_cities = {
        '济南': 'jinan',
        '青岛': 'qingdao', 
        '烟台': 'yantai',
        '潍坊': 'weifang',
        '临沂': 'linyi',
        '淄博': 'zibo',
        '济宁': 'jining',
        '泰安': 'taian',
        '聊城': 'liaocheng',
        '威海': 'weihai',
        '枣庄': 'zaozhuang',
        '德州': 'dezhou',
        '东营': 'dongying',
        '菏泽': 'heze',
        '日照': 'rizhao',
        '滨州': 'binzhou'
    }
    
    # 其他省份主要城市映射
    city_to_province = {
        # 广东省城市
        '广州': 'guangdong', '深圳': 'guangdong', '珠海': 'guangdong', '佛山': 'guangdong',
        '韶关': 'guangdong', '湛江': 'guangdong', '肇庆': 'guangdong', '江门': 'guangdong',
        '茂名': 'guangdong', '惠州': 'guangdong', '梅州': 'guangdong', '汕尾': 'guangdong',
        '河源': 'guangdong', '阳江': 'guangdong', '清远': 'guangdong', '东莞': 'guangdong',
        '中山': 'guangdong', '潮州': 'guangdong', '揭阳': 'guangdong', '云浮': 'guangdong',
        '汕头': 'guangdong',
        
        # 江苏省城市
        '南京': 'jiangsu', '苏州': 'jiangsu', '无锡': 'jiangsu', '常州': 'jiangsu',
        '镇江': 'jiangsu', '南通': 'jiangsu', '泰州': 'jiangsu', '扬州': 'jiangsu',
        '盐城': 'jiangsu', '连云港': 'jiangsu', '徐州': 'jiangsu', '淮安': 'jiangsu',
        '宿迁': 'jiangsu',
        
        # 浙江省城市
        '杭州': 'zhejiang', '宁波': 'zhejiang', '温州': 'zhejiang', '嘉兴': 'zhejiang',
        '湖州': 'zhejiang', '绍兴': 'zhejiang', '金华': 'zhejiang', '衢州': 'zhejiang',
        '舟山': 'zhejiang', '台州': 'zhejiang', '丽水': 'zhejiang',
        
        # 河北省城市
        '石家庄': 'hebei', '唐山': 'hebei', '秦皇岛': 'hebei', '邯郸': 'hebei',
        '邢台': 'hebei', '保定': 'hebei', '张家口': 'hebei', '承德': 'hebei',
        '沧州': 'hebei', '廊坊': 'hebei', '衡水': 'hebei',
        
        # 河南省城市
        '郑州': 'henan', '开封': 'henan', '洛阳': 'henan', '平顶山': 'henan',
        '安阳': 'henan', '鹤壁': 'henan', '新乡': 'henan', '焦作': 'henan',
        '濮阳': 'henan', '许昌': 'henan', '漯河': 'henan', '三门峡': 'henan',
        '南阳': 'henan', '商丘': 'henan', '信阳': 'henan', '周口': 'henan',
        '驻马店': 'henan',
        
        # 四川省城市
        '成都': 'sichuan', '自贡': 'sichuan', '攀枝花': 'sichuan', '泸州': 'sichuan',
        '德阳': 'sichuan', '绵阳': 'sichuan', '广元': 'sichuan', '遂宁': 'sichuan',
        '内江': 'sichuan', '乐山': 'sichuan', '南充': 'sichuan', '眉山': 'sichuan',
        '宜宾': 'sichuan', '广安': 'sichuan', '达州': 'sichuan', '雅安': 'sichuan',
        '巴中': 'sichuan', '资阳': 'sichuan',
        
        # 湖北省城市
        '武汉': 'hubei', '黄石': 'hubei', '十堰': 'hubei', '宜昌': 'hubei',
        '襄阳': 'hubei', '鄂州': 'hubei', '荆门': 'hubei', '孝感': 'hubei',
        '荆州': 'hubei', '黄冈': 'hubei', '咸宁': 'hubei', '随州': 'hubei',
        
        # 湖南省城市
        '长沙': 'hunan', '株洲': 'hunan', '湘潭': 'hunan', '衡阳': 'hunan',
        '邵阳': 'hunan', '岳阳': 'hunan', '常德': 'hunan', '张家界': 'hunan',
        '益阳': 'hunan', '郴州': 'hunan', '永州': 'hunan', '怀化': 'hunan',
        '娄底': 'hunan',
        
        # 安徽省城市
        '合肥': 'anhui', '芜湖': 'anhui', '蚌埠': 'anhui', '淮南': 'anhui',
        '马鞍山': 'anhui', '淮北': 'anhui', '铜陵': 'anhui', '安庆': 'anhui',
        '黄山': 'anhui', '滁州': 'anhui', '阜阳': 'anhui', '宿州': 'anhui',
        '六安': 'anhui', '亳州': 'anhui', '池州': 'anhui', '宣城': 'anhui',
        
        # 福建省城市
        '福州': 'fujian', '厦门': 'fujian', '莆田': 'fujian', '三明': 'fujian',
        '泉州': 'fujian', '漳州': 'fujian', '南平': 'fujian', '龙岩': 'fujian',
        '宁德': 'fujian',
        
        # 江西省城市
        '南昌': 'jiangxi', '景德镇': 'jiangxi', '萍乡': 'jiangxi', '九江': 'jiangxi',
        '新余': 'jiangxi', '鹰潭': 'jiangxi', '赣州': 'jiangxi', '吉安': 'jiangxi',
        '宜春': 'jiangxi', '抚州': 'jiangxi', '上饶': 'jiangxi',
        
        # 辽宁省城市
        '沈阳': 'liaoning', '大连': 'liaoning', '鞍山': 'liaoning', '抚顺': 'liaoning',
        '本溪': 'liaoning', '丹东': 'liaoning', '锦州': 'liaoning', '营口': 'liaoning',
        '阜新': 'liaoning', '辽阳': 'liaoning', '盘锦': 'liaoning', '铁岭': 'liaoning',
        '朝阳': 'liaoning', '葫芦岛': 'liaoning',
        
        # 吉林省城市
        '长春': 'jilin', '吉林': 'jilin', '四平': 'jilin', '辽源': 'jilin',
        '通化': 'jilin', '白山': 'jilin', '松原': 'jilin', '白城': 'jilin',
        
        # 黑龙江省城市
        '哈尔滨': 'heilongjiang', '齐齐哈尔': 'heilongjiang', '鸡西': 'heilongjiang',
        '鹤岗': 'heilongjiang', '双鸭山': 'heilongjiang', '大庆': 'heilongjiang',
        '伊春': 'heilongjiang', '佳木斯': 'heilongjiang', '七台河': 'heilongjiang',
        '牡丹江': 'heilongjiang', '黑河': 'heilongjiang', '绥化': 'heilongjiang',
        
        # 山西省城市
        '太原': 'shanxi', '大同': 'shanxi', '阳泉': 'shanxi', '长治': 'shanxi',
        '晋城': 'shanxi', '朔州': 'shanxi', '晋中': 'shanxi', '运城': 'shanxi',
        '忻州': 'shanxi', '临汾': 'shanxi', '吕梁': 'shanxi',
        
        # 陕西省城市
        '西安': 'shaanxi', '铜川': 'shaanxi', '宝鸡': 'shaanxi', '咸阳': 'shaanxi',
        '渭南': 'shaanxi', '延安': 'shaanxi', '汉中': 'shaanxi', '榆林': 'shaanxi',
        '安康': 'shaanxi', '商洛': 'shaanxi',
        
        # 甘肃省城市
        '兰州': 'gansu', '嘉峪关': 'gansu', '金昌': 'gansu', '白银': 'gansu',
        '天水': 'gansu', '武威': 'gansu', '张掖': 'gansu', '平凉': 'gansu',
        '酒泉': 'gansu', '庆阳': 'gansu', '定西': 'gansu', '陇南': 'gansu',
        
        # 青海省城市
        '西宁': 'qinghai', '海东': 'qinghai',
        
        # 宁夏城市
        '银川': 'ningxia', '石嘴山': 'ningxia', '吴忠': 'ningxia', '固原': 'ningxia',
        '中卫': 'ningxia',
        
        # 新疆城市
        '乌鲁木齐': 'xinjiang', '克拉玛依': 'xinjiang', '吐鲁番': 'xinjiang',
        '哈密': 'xinjiang',
        
        # 西藏城市
        '拉萨': 'xizang', '日喀则': 'xizang', '昌都': 'xizang', '林芝': 'xizang',
        '山南': 'xizang', '那曲': 'xizang',
        
        # 云南省城市
        '昆明': 'yunnan', '曲靖': 'yunnan', '玉溪': 'yunnan', '保山': 'yunnan',
        '昭通': 'yunnan', '丽江': 'yunnan', '普洱': 'yunnan', '临沧': 'yunnan',
        
        # 贵州省城市
        '贵阳': 'guizhou', '六盘水': 'guizhou', '遵义': 'guizhou', '安顺': 'guizhou',
        '毕节': 'guizhou', '铜仁': 'guizhou',
        
        # 广西城市
        '南宁': 'guangxi', '柳州': 'guangxi', '桂林': 'guangxi', '梧州': 'guangxi',
        '北海': 'guangxi', '防城港': 'guangxi', '钦州': 'guangxi', '贵港': 'guangxi',
        '玉林': 'guangxi', '百色': 'guangxi', '贺州': 'guangxi', '河池': 'guangxi',
        '来宾': 'guangxi', '崇左': 'guangxi',
        
        # 海南省城市
        '海口': 'hainan', '三亚': 'hainan', '三沙': 'hainan', '儋州': 'hainan',
        
        # 内蒙古城市
        '呼和浩特': 'neimenggu', '包头': 'neimenggu', '乌海': 'neimenggu',
        '赤峰': 'neimenggu', '通辽': 'neimenggu', '鄂尔多斯': 'neimenggu',
        '呼伦贝尔': 'neimenggu', '巴彦淖尔': 'neimenggu', '乌兰察布': 'neimenggu'
    }
    
    # 1. 检查是否为单一省份
    if len(region_names) == 1:
        region_name = region_names[0]
        if region_name in province_map_types:
            return province_map_types[region_name]
    
    # 2. 检查是否为山东省城市
    if all(name in shandong_cities for name in region_names):
        if len(region_names) == 1:
            # 单个山东城市，返回该城市的地图
            return shandong_cities[region_names[0]]
        else:
            # 多个山东城市，返回山东省地图
            return 'shandong'
    
    # 3. 检查是否为其他省份的城市
    provinces_found = set()
    for name in region_names:
        if name in city_to_province:
            provinces_found.add(city_to_province[name])
    
    if len(provinces_found) == 1:
        # 所有城市都属于同一个省份
        return provinces_found.pop()
    
    # 4. 检查是否为多个省份
    provinces_in_data = set()
    for name in region_names:
        if name in province_map_types:
            provinces_in_data.add(name)
    
    if len(provinces_in_data) >= 2:
        # 多个省份，使用中国地图
        return 'china'
    
    # 5. 默认返回中国地图
    return 'china'

def get_map_center(map_type):
    """获取地图中心点坐标"""
    centers = {
        'china': [104.114129, 37.550339],  # 中国
        # 省份中心点
        'shandong': [117.000923, 36.675807],  # 山东
        'beijing': [116.383331, 39.916668],  # 北京
        'shanghai': [121.472644, 31.231706],  # 上海
        'guangdong': [113.280637, 23.125178],  # 广东
        'sichuan': [104.065735, 30.659462],  # 四川
        'jiangsu': [118.767413, 32.041544],  # 江苏
        'zhejiang': [120.153576, 30.287459],  # 浙江
        'hebei': [114.502461, 38.045474],  # 河北
        'henan': [113.665412, 34.757975],  # 河南
        'hubei': [114.298572, 30.584355],  # 湖北
        'hunan': [112.982279, 28.19409],   # 湖南
        'anhui': [117.283042, 31.86119],   # 安徽
        'fujian': [119.306239, 26.075302], # 福建
        'jiangxi': [115.892151, 28.676493], # 江西
        'liaoning': [123.429096, 41.796767], # 辽宁
        'jilin': [125.3245, 43.886841],    # 吉林
        'heilongjiang': [126.642464, 45.756967], # 黑龙江
        'neimenggu': [111.670801, 40.818311], # 内蒙古
        'shanxi': [112.549248, 37.857014],  # 山西
        'shaanxi': [108.948024, 34.263161], # 陕西
        'gansu': [103.823557, 36.058039],  # 甘肃
        'qinghai': [101.778916, 36.623178], # 青海
        'ningxia': [106.278179, 38.46637],  # 宁夏
        'xinjiang': [87.617733, 43.792818], # 新疆
        'xizang': [91.132212, 29.660361],   # 西藏
        'yunnan': [102.712251, 25.040609],  # 云南
        'guizhou': [106.713478, 26.578343], # 贵州
        'chongqing': [106.504962, 29.533155], # 重庆
        'tianjin': [117.190182, 39.125596], # 天津
        'guangxi': [108.320004, 22.82402],  # 广西
        'hainan': [110.33119, 20.031971],   # 海南
        # 山东省城市中心点
        'jinan': [117.000923, 36.675807],   # 济南
        'qingdao': [120.355173, 36.082982], # 青岛
        'yantai': [121.391382, 37.539297],  # 烟台
        'weifang': [119.107078, 36.70925],  # 潍坊
        'linyi': [118.326443, 35.065282],   # 临沂
        'zibo': [118.047648, 36.814939],    # 淄博
        'jining': [116.587245, 35.415393],  # 济宁
        'taian': [117.129063, 36.194968],   # 泰安
        'liaocheng': [115.980367, 36.456013], # 聊城
        'weihai': [122.116394, 37.513068],  # 威海
        'zaozhuang': [117.557964, 34.856424], # 枣庄
        'dezhou': [116.307428, 37.453968],  # 德州
        'dongying': [118.49642, 37.461266], # 东营
        'heze': [115.469381, 35.246531],    # 菏泽
        'rizhao': [119.461208, 35.428588],  # 日照
        'binzhou': [118.016974, 37.383542]  # 滨州
    }
    return centers.get(map_type, centers['china'])

def get_map_zoom(map_type):
    """获取地图缩放级别"""
    zooms = {
        'china': 1.2,      # 中国
        # 省份缩放级别
        'shandong': 1.8,   # 山东
        'beijing': 2.5,    # 北京
        'shanghai': 2.5,   # 上海
        'guangdong': 1.8,  # 广东
        'sichuan': 1.5,    # 四川
        'jiangsu': 1.8,    # 江苏
        'zhejiang': 1.8,   # 浙江
        'hebei': 1.6,      # 河北
        'henan': 1.6,      # 河南
        'hubei': 1.8,      # 湖北
        'hunan': 1.8,      # 湖南
        'anhui': 1.8,      # 安徽
        'fujian': 2.0,     # 福建
        'jiangxi': 1.8,    # 江西
        'liaoning': 1.8,   # 辽宁
        'jilin': 1.8,      # 吉林
        'heilongjiang': 1.5, # 黑龙江
        'neimenggu': 1.2,  # 内蒙古
        'shanxi': 1.8,     # 山西
        'shaanxi': 1.6,    # 陕西
        'gansu': 1.3,      # 甘肃
        'qinghai': 1.3,    # 青海
        'ningxia': 2.2,    # 宁夏
        'xinjiang': 1.0,   # 新疆
        'xizang': 1.0,     # 西藏
        'yunnan': 1.5,     # 云南
        'guizhou': 1.8,    # 贵州
        'chongqing': 2.2,  # 重庆
        'tianjin': 2.5,    # 天津
        'guangxi': 1.6,    # 广西
        'hainan': 2.2,     # 海南
        # 山东省城市缩放级别
        'jinan': 2.5,      # 济南
        'qingdao': 2.5,    # 青岛
        'yantai': 2.5,     # 烟台
        'weifang': 2.5,    # 潍坊
        'linyi': 2.5,      # 临沂
        'zibo': 2.5,       # 淄博
        'jining': 2.5,     # 济宁
        'taian': 2.5,      # 泰安
        'liaocheng': 2.5,  # 聊城
        'weihai': 2.5,     # 威海
        'zaozhuang': 2.5,  # 枣庄
        'dezhou': 2.5,     # 德州
        'dongying': 2.5,   # 东营
        'heze': 2.5,       # 菏泽
        'rizhao': 2.5,     # 日照
        'binzhou': 2.5     # 滨州
    }
    return zooms.get(map_type, zooms['china'])

def generate_map_config(data, title):
    """生成地图配置"""
    map_type = data.get('map_type', 'china')  # 默认中国地图
    
    # 智能检测地图类型
    if 'regions' in data and len(data['regions']) >= 1:
        # 分析数据中的地名，智能选择合适的地图类型
        region_names = [region['name'] for region in data['regions']]
        detected_map_type = detect_map_type(region_names)
        
        if detected_map_type != 'china':
            map_type = detected_map_type
            logger.info(f"智能检测地图类型: {region_names} -> {map_type}")
        else:
            logger.info(f"使用默认中国地图显示: {region_names}")
    
    # 基础地图配置
    map_config = {
        'title': {
            'text': title,
            'textStyle': {'color': '#ffffff', 'fontSize': 20, 'fontWeight': 'bold'},
            'left': 'center', 'top': 20
        },
        'tooltip': {
            'trigger': 'item',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',
            'borderColor': '#333',
            'textStyle': {'color': '#fff'},
            'formatter': '{b}<br/>{c}'
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'textStyle': {'color': '#ffffff'},
            'data': []
        },
        'visualMap': {
            'min': 0,
            'max': data.get('max_value', 1000),
            'left': 'left',
            'top': 'bottom',
            'text': ['高', '低'],
            'calculable': True,
            'textStyle': {'color': '#ffffff'},
            'inRange': {
                'color': ['#50a3ba', '#eac736', '#d94e5d']
            }
        },
        'series': [],
        'backgroundColor': '#1a1a1a'
    }
    
    # 如果只有区域数据，使用简单的地图模式
    if 'regions' in data and 'scatter_data' not in data:
        # 区域数据图
        map_config['series'].append({
            'name': '数据',
            'type': 'map',
            'map': map_type,
            'roam': True,
            'zoom': get_map_zoom(map_type),
            'center': get_map_center(map_type),
            'data': data['regions'],
            'emphasis': {
                'itemStyle': {
                    'areaColor': '#f4e925'
                },
                'label': {
                    'show': True,
                    'color': '#000'
                }
            },
            'itemStyle': {
                'areaColor': '#323c48',
                'borderColor': '#389BB7',
                'borderWidth': 1
            },
            'label': {
                'show': True,
                'color': '#ffffff',
                'fontSize': 8
            }
        })
        
        # 添加图例数据
        map_config['legend']['data'].append('数据')
    
    # 如果有散点数据，使用geo坐标系
    elif 'scatter_data' in data:
        # 添加地理坐标系统
        map_config['geo'] = {
            'map': map_type,
            'roam': True,
            'zoom': get_map_zoom(map_type),
            'center': get_map_center(map_type),
            'itemStyle': {
                'areaColor': '#323c48',
                'borderColor': '#404a59',
                'borderWidth': 1
            },
            'emphasis': {
                'itemStyle': {
                    'areaColor': '#2a333d'
                }
            },
            'label': {
                'show': True,
                'color': '#ffffff',
                'fontSize': 8
            }
        }
        
        # 如果同时有区域数据，添加到geo上
        if 'regions' in data:
            # 将区域数据转换为geo的regions配置
            map_config['geo']['regions'] = []
            for region in data['regions']:
                map_config['geo']['regions'].append({
                    'name': region['name'],
                    'itemStyle': {
                        'areaColor': '#323c48',
                        'borderColor': '#389BB7'
                    },
                    'emphasis': {
                        'itemStyle': {
                            'areaColor': '#f4e925'
                        }
                    }
                })
        
        # 转换散点数据格式
        scatter_data = []
        for item in data['scatter_data']:
            if isinstance(item, dict) and 'name' in item and 'value' in item:
                scatter_data.append({
                    'name': item['name'],
                    'value': item['value']
                })
            elif isinstance(item, list) and len(item) >= 3:
                scatter_data.append({
                    'name': item[3] if len(item) > 3 else f'点{len(scatter_data)+1}',
                    'value': item[:3]
                })
        
        scatter_series = {
            'name': '散点数据',
            'type': 'scatter',
            'coordinateSystem': 'geo',
            'data': scatter_data,
            'symbolSize': 15,
            'label': {
                'show': True,
                'position': 'right',
                'formatter': '{b}',
                'color': '#ffffff',
                'fontSize': 10
            },
            'itemStyle': {
                'color': '#00ff9f',
                'shadowBlur': 10,
                'shadowColor': '#333'
            },
            'emphasis': {
                'itemStyle': {
                    'color': '#ff6b6b'
                }
            }
        }
        
        map_config['series'].append(scatter_series)
        map_config['legend']['data'].append('散点数据')
    
    # 添加热力图数据
    if 'heatmap_data' in data:
        # 如果没有geo，先创建
        if 'geo' not in map_config:
            map_config['geo'] = {
                'map': map_type,
                'roam': True,
                'zoom': get_map_zoom(map_type),
                'center': get_map_center(map_type),
                'itemStyle': {
                    'areaColor': '#323c48',
                    'borderColor': '#404a59'
                },
                'emphasis': {
                    'itemStyle': {
                        'areaColor': '#2a333d'
                    }
                }
            }
        
        heatmap_series = {
            'name': '热力分布',
            'type': 'heatmap',
            'coordinateSystem': 'geo',
            'data': data['heatmap_data'],
            'pointSize': 5,
            'blurSize': 6
        }
        
        map_config['series'].append(heatmap_series)
        map_config['legend']['data'].append('热力分布')
    
    return map_config

def create_html_template(echarts_config, title="动态图表", map_type="china"):
    """
    创建HTML模板
    """
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.0.0/dist/echarts-wordcloud.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        #chart {{
            width: 100%;
            height: 600px;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.2);
        }}
        
        .info {{
            text-align: center;
            color: #ffffff;
            margin-bottom: 20px;
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #00ff9f, #00cc7f);
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 159, 0.3);
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 159, 0.4);
        }}
        
        .btn:active {{
            transform: translateY(0);
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .container {{
            animation: fadeIn 0.8s ease-out;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="info">
            <h2 style="color: #00ff9f; margin: 0;">{title}</h2>
            <p>动态交互式图表 - 鼠标悬停查看详细数据</p>
        </div>
        
        <div id="chart"></div>
        
        <div class="controls">
            <button class="btn" onclick="refreshChart()">刷新动画</button>
            <button class="btn" onclick="downloadChart()">下载图片</button>
            <button class="btn" onclick="toggleTheme()">切换主题</button>
        </div>
    </div>

    <script>
        // 错误处理函数
        function handleError(error, context) {{
            console.error('图表错误 (' + context + '):', error);
            const chartDom = document.getElementById('chart');
            chartDom.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #ff6b6b; text-align: center; flex-direction: column;">' +
                '<h3>图表加载失败</h3>' +
                '<p>错误信息: ' + (error.message || error) + '</p>' +
                '<p>上下文: ' + context + '</p>' +
                '<p>请检查网络连接或刷新页面重试</p>' +
                '</div>';
        }}
        
        // 等待资源加载完成
        function initChart() {{
            try {{
                // 检查ECharts是否加载
                if (typeof echarts === 'undefined') {{
                    throw new Error('ECharts未加载');
                }}
                
                // 初始化图表
                const chartDom = document.getElementById('chart');
                const myChart = echarts.init(chartDom);
                
                // 图表配置
                const option = {json.dumps(echarts_config, ensure_ascii=False, indent=2)};
                
                // 地图加载状态
                let mapLoaded = false;
                
                // 检查是否为地图类型
                const isMapChart = option.series && option.series.some(s => s.type === 'map') || 
                                  option.geo !== undefined;
                
                if (isMapChart) {{
                    // 等待地图数据加载
                    setTimeout(() => {{
                        try {{
                                                        // 根据地图类型选择数据源
                            const mapType = '{map_type}';
                            let mapUrls = [];
                            
                            // 地图数据源配置
                            const mapDataSources = {{
                                'china': ['https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'],
                                // 省份地图
                                'shandong': ['https://geo.datav.aliyun.com/areas_v3/bound/370000_full.json'],
                                'beijing': ['https://geo.datav.aliyun.com/areas_v3/bound/110000_full.json'],
                                'shanghai': ['https://geo.datav.aliyun.com/areas_v3/bound/310000_full.json'],
                                'guangdong': ['https://geo.datav.aliyun.com/areas_v3/bound/440000_full.json'],
                                'sichuan': ['https://geo.datav.aliyun.com/areas_v3/bound/510000_full.json'],
                                'jiangsu': ['https://geo.datav.aliyun.com/areas_v3/bound/320000_full.json'],
                                'zhejiang': ['https://geo.datav.aliyun.com/areas_v3/bound/330000_full.json'],
                                'hebei': ['https://geo.datav.aliyun.com/areas_v3/bound/130000_full.json'],
                                'henan': ['https://geo.datav.aliyun.com/areas_v3/bound/410000_full.json'],
                                'hubei': ['https://geo.datav.aliyun.com/areas_v3/bound/420000_full.json'],
                                'hunan': ['https://geo.datav.aliyun.com/areas_v3/bound/430000_full.json'],
                                'anhui': ['https://geo.datav.aliyun.com/areas_v3/bound/340000_full.json'],
                                'fujian': ['https://geo.datav.aliyun.com/areas_v3/bound/350000_full.json'],
                                'jiangxi': ['https://geo.datav.aliyun.com/areas_v3/bound/360000_full.json'],
                                'liaoning': ['https://geo.datav.aliyun.com/areas_v3/bound/210000_full.json'],
                                'jilin': ['https://geo.datav.aliyun.com/areas_v3/bound/220000_full.json'],
                                'heilongjiang': ['https://geo.datav.aliyun.com/areas_v3/bound/230000_full.json'],
                                'neimenggu': ['https://geo.datav.aliyun.com/areas_v3/bound/150000_full.json'],
                                'shanxi': ['https://geo.datav.aliyun.com/areas_v3/bound/140000_full.json'],
                                'shaanxi': ['https://geo.datav.aliyun.com/areas_v3/bound/610000_full.json'],
                                'gansu': ['https://geo.datav.aliyun.com/areas_v3/bound/620000_full.json'],
                                'qinghai': ['https://geo.datav.aliyun.com/areas_v3/bound/630000_full.json'],
                                'ningxia': ['https://geo.datav.aliyun.com/areas_v3/bound/640000_full.json'],
                                'xinjiang': ['https://geo.datav.aliyun.com/areas_v3/bound/650000_full.json'],
                                'xizang': ['https://geo.datav.aliyun.com/areas_v3/bound/540000_full.json'],
                                'yunnan': ['https://geo.datav.aliyun.com/areas_v3/bound/530000_full.json'],
                                'guizhou': ['https://geo.datav.aliyun.com/areas_v3/bound/520000_full.json'],
                                'chongqing': ['https://geo.datav.aliyun.com/areas_v3/bound/500000_full.json'],
                                'tianjin': ['https://geo.datav.aliyun.com/areas_v3/bound/120000_full.json'],
                                'guangxi': ['https://geo.datav.aliyun.com/areas_v3/bound/450000_full.json'],
                                'hainan': ['https://geo.datav.aliyun.com/areas_v3/bound/460000_full.json'],
                                // 山东省城市地图
                                'jinan': ['https://geo.datav.aliyun.com/areas_v3/bound/370100_full.json'],
                                'qingdao': ['https://geo.datav.aliyun.com/areas_v3/bound/370200_full.json'],
                                'yantai': ['https://geo.datav.aliyun.com/areas_v3/bound/370600_full.json'],
                                'weifang': ['https://geo.datav.aliyun.com/areas_v3/bound/370700_full.json'],
                                'linyi': ['https://geo.datav.aliyun.com/areas_v3/bound/371300_full.json'],
                                'zibo': ['https://geo.datav.aliyun.com/areas_v3/bound/370300_full.json'],
                                'jining': ['https://geo.datav.aliyun.com/areas_v3/bound/370800_full.json'],
                                'taian': ['https://geo.datav.aliyun.com/areas_v3/bound/370900_full.json'],
                                'liaocheng': ['https://geo.datav.aliyun.com/areas_v3/bound/371500_full.json'],
                                'weihai': ['https://geo.datav.aliyun.com/areas_v3/bound/371000_full.json'],
                                'zaozhuang': ['https://geo.datav.aliyun.com/areas_v3/bound/370400_full.json'],
                                'dezhou': ['https://geo.datav.aliyun.com/areas_v3/bound/371400_full.json'],
                                'dongying': ['https://geo.datav.aliyun.com/areas_v3/bound/370500_full.json'],
                                'heze': ['https://geo.datav.aliyun.com/areas_v3/bound/371700_full.json'],
                                'rizhao': ['https://geo.datav.aliyun.com/areas_v3/bound/371100_full.json'],
                                'binzhou': ['https://geo.datav.aliyun.com/areas_v3/bound/371600_full.json']
                            }};
                            
                            mapUrls = mapDataSources[mapType] || mapDataSources['china'];
                            
                            let loadSuccess = false;
                            
                            function tryLoadMapData(urls, index = 0) {{
                                if (index >= urls.length) {{
                                    console.warn('所有在线地图数据源加载失败，使用简化显示');
                                    // 如果所有在线数据源都失败，直接渲染现有配置
                                    myChart.setOption(option);
                                    console.log('使用默认配置渲染地图');
                                    return;
                                }}
                                
                                console.log('尝试加载地图数据:', urls[index]);
                                
                                fetch(urls[index])
                                    .then(response => {{
                                        if (!response.ok) {{
                                            throw new Error('HTTP ' + response.status);
                                        }}
                                        return response.json();
                                    }})
                                    .then(geoData => {{
                                        // 处理不同格式的地理数据
                                        let chinaData = geoData;
                                        
                                        // 如果是阿里云数据源，直接使用
                                        if (urls[index].includes('datav.aliyun.com')) {{
                                            echarts.registerMap(mapType, chinaData);
                                            myChart.setOption(option);
                                            console.log('阿里云地图数据加载成功:', mapType);
                                            loadSuccess = true;
                                            return;
                                        }}
                                        
                                        // 如果是其他数据源，处理不同的数据格式
                                        if (geoData.features) {{
                                            let targetFeatures = [];
                                            
                                            if (mapType === 'china') {{
                                                // 中国地图：过滤中国数据
                                                targetFeatures = geoData.features.filter(feature => 
                                                    feature.properties && 
                                                    (feature.properties.NAME_ZH === '中国' || 
                                                     feature.properties.name === '中国' ||
                                                     feature.properties.NAME === 'China' ||
                                                     feature.properties.name === 'China')
                                                );
                                            }} else {{
                                                // 省级地图：直接使用所有特征
                                                targetFeatures = geoData.features;
                                            }}
                                            
                                            if (targetFeatures.length > 0) {{
                                                chinaData = {{
                                                    type: 'FeatureCollection',
                                                    features: targetFeatures
                                                }};
                                                echarts.registerMap(mapType, chinaData);
                                                myChart.setOption(option);
                                                console.log('地图数据过滤并加载成功:', mapType);
                                                loadSuccess = true;
                                                return;
                                            }}
                                        }}
                                        
                                        // 如果无法识别格式，尝试下一个数据源
                                        throw new Error('无法识别地图数据格式');
                                    }})
                                    .catch(error => {{
                                        console.warn('地图数据加载失败:', urls[index], error.message);
                                        tryLoadMapData(urls, index + 1);
                                    }});
                            }}
                            
                            // 开始尝试加载地图数据
                            tryLoadMapData(mapUrls);
                        }} catch (mapError) {{
                            handleError(mapError, '地图数据加载');
                        }}
                    }}, 1000);
                }} else {{
                    // 非地图图表直接渲染
                    myChart.setOption(option);
                    console.log('图表初始化成功');
                }}
                
                // 监听图表错误
                myChart.on('error', function(params) {{
                    handleError(params, '图表渲染');
                }});
                
                // 存储图表实例供其他函数使用
                window.myChart = myChart;
                
            }} catch (error) {{
                handleError(error, '图表初始化');
            }}
        }}
        
        // 页面加载完成后初始化
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initChart);
        }} else {{
            initChart();
        }}
        
        // 响应式
        window.addEventListener('resize', function() {{
            if (window.myChart) {{
                window.myChart.resize();
            }}
        }});
        
        // 刷新动画
        function refreshChart() {{
            if (window.myChart) {{
                window.myChart.clear();
                window.myChart.setOption({json.dumps(echarts_config, ensure_ascii=False)});
            }}
        }}
        
        // 下载图片
        function downloadChart() {{
            if (window.myChart) {{
                const url = window.myChart.getDataURL({{
                    type: 'png',
                    pixelRatio: 2,
                    backgroundColor: '#1a1a1a'
                }});
                const link = document.createElement('a');
                link.download = '{title}_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.png';
                link.href = url;
                link.click();
            }}
        }}
        
        // 切换主题
        let isDarkTheme = true;
        function toggleTheme() {{
            if (window.myChart) {{
                isDarkTheme = !isDarkTheme;
                const newOption = JSON.parse(JSON.stringify({json.dumps(echarts_config, ensure_ascii=False)}));
                
                if (isDarkTheme) {{
                    newOption.backgroundColor = '#1a1a1a';
                    document.body.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)';
                }} else {{
                    newOption.backgroundColor = '#ffffff';
                    if (newOption.title) newOption.title.textStyle.color = '#333333';
                    if (newOption.legend) newOption.legend.textStyle.color = '#333333';
                    if (newOption.xAxis) {{
                        newOption.xAxis.nameTextStyle.color = '#333333';
                        newOption.xAxis.axisLine.lineStyle.color = '#333333';
                        newOption.xAxis.axisLabel.color = '#333333';
                    }}
                    if (newOption.yAxis && Array.isArray(newOption.yAxis)) {{
                        newOption.yAxis.forEach(axis => {{
                            axis.nameTextStyle.color = '#333333';
                            axis.axisLine.lineStyle.color = '#333333';
                            axis.axisLabel.color = '#333333';
                        }});
                    }}
                    document.body.style.background = 'linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%)';
                }}
                
                window.myChart.setOption(newOption);
            }}
        }}
        
        // 添加事件监听器
        function addEventListeners() {{
            if (window.myChart) {{
                // 添加点击事件
                window.myChart.on('click', function(params) {{
                    console.log('点击了:', params);
                    // 可以在这里添加更多交互逻辑
                }});
                
                // 添加数据缩放功能
                window.myChart.on('datazoom', function(params) {{
                    console.log('数据缩放:', params);
                }});
            }}
        }}
        
        // 延迟添加事件监听器
        setTimeout(addEventListeners, 1500);
    </script>
</body>
</html>"""
    
    return html_template

def draw_html_chart(data_input, title="动态图表", x_label="X轴"):
    """
    绘制HTML动态图表
    """
    try:
        # 处理输入数据
        if isinstance(data_input, (str, dict)):
            # JSON格式
            data = process_json_data(data_input)
        elif isinstance(data_input, tuple) and len(data_input) >= 2:
            # 向后兼容：旧的字符串格式
            x_str, y_str = data_input[0], data_input[1]
            chart_type = data_input[2] if len(data_input) > 2 else 'bar'
            
            x_values = [x.strip() for x in x_str.split(',')]
            y_values = [float(y.strip()) for y in y_str.split(',')]
            
            data = {
                "x_data": x_values,
                "series": [{
                    'name': '数据系列',
                    'data': y_values,
                    'type': chart_type,
                    'y_unit': '数值',
                    'color': '#00ff9f'
                }]
            }
        else:
            raise ValueError("不支持的数据输入格式")
        
        # 生成ECharts配置
        echarts_config = generate_echarts_config(data, title, x_label)
        
        # 获取地图类型（如果是地图图表的话）
        map_type = "china"  # 默认值
        if data.get('chart_type') == 'map':
            # 使用智能检测函数
            if 'regions' in data and len(data['regions']) >= 1:
                region_names = [region['name'] for region in data['regions']]
                map_type = detect_map_type(region_names)
            else:
                map_type = data.get('map_type', 'china')
        
        # 创建HTML内容
        html_content = create_html_template(echarts_config, title, map_type)
        
        # 生成文件名和路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ensure_output_dir()
        filename = f"dynamic_chart_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # 保存HTML文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 在浏览器中打开
        open_html_file(filepath)
        
        # 返回相对路径用于web显示
        relative_path = f"/static/charts/{os.path.basename(filepath)}"
        message = f"动态图表 '{title}' 已生成！\n文件路径: {relative_path}\n特性: 动画效果、交互缩放、主题切换、图片下载"
        
        return message
        
    except Exception as e:
        logger.error(f"生成HTML图表失败: {str(e)}")
        return f"生成HTML图表失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    # 示例：多系列混合图表
    json_data = {
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
        json_data,
        title="销售数据动态分析",
        x_label="月份"
    )
    print(result) 