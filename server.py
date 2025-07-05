"""
独立的 MCP 服务器
支持 SSE 模式，可独立部署
"""
import logging
import asyncio
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from external_message import send_external_message
from src.database.db_reader import DatabaseReader
from src.tools.chart_utils import draw_chart
from src.tools.web_control import open_website
from src.tools.html_chart_utils import draw_html_chart
from fastmcp import FastMCP
from src.config.config_loader import ConfigLoader

# 获取配置
config = ConfigLoader()

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 配置更详细的日志
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_level = getattr(logging, config.logging_config.get('level', 'INFO'))

# 创建文件处理器 - 详细日志
file_handler = logging.FileHandler(config.logging_config.get('file', 'logs/mcp_server.log'), encoding='utf-8')
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format))

# 创建控制台处理器 - 简化显示
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 创建专门的MCP调用日志文件
mcp_calls_handler = logging.FileHandler('logs/mcp_calls.log', encoding='utf-8')
mcp_calls_handler.setLevel(logging.INFO)
mcp_calls_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

# 配置根日志记录器
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger('mcp_server')

# 创建专门的MCP调用日志记录器
mcp_calls_logger = logging.getLogger('mcp_calls')
mcp_calls_logger.addHandler(mcp_calls_handler)
mcp_calls_logger.setLevel(logging.INFO)
mcp_calls_logger.propagate = False  # 防止重复记录

# 创建 MCP 实例
mcp = FastMCP("AIKnowledgeStorage MCP Server")

@mcp.tool()
def openWebsite(url: str) -> dict:
    """打开网页工具
    
    Args:
        url: 要打开的网页 URL
        
    Returns:
        dict: 操作结果
    """
    try:
        result = open_website(url)
        logger.info(f"成功打开网页: {url}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"打开网页失败: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def getDataFromDatabase(table_name: str) -> dict:
    """For get url from database, always use this tool to get url data, table_name: sponge_city_urls.
    For get project information from database, always use this tool to get data, table_name: 项目统计."""
    try:
        db = DatabaseReader()
        result = db.read_data_by_table(table_name)
        logger.info(f"成功查询数据表: {table_name}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"数据库查询失败: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def drawChart(data_input, title="多系列图表", x_label="X轴", userName = "Unknown") -> dict:
    """
    绘制各种类型的动态交互式图表，支持11种图表类型
    
    重要提示：
    1. 如果想要在一张图表中绘制多组数据，或绘制折线图柱状图混合图表，请在series中添加多组数据
    2. 在传入json的时候，如果你能获取到相应数据，各个字段请确保有确切清晰的值，比如x_data的值是具体的项目名称而不是项目A
    
    参数:
    data_input: 数据输入，支持多种图表类型的JSON格式：
    
    === 基础图表 ===
    
    1. 混合图表（柱状图+折线图，支持双Y轴）- 默认类型：
    {
        "x_data": ["1月", "2月", "3月", "4月"],
        "series": [
            {
                "name": "销售额",
                "data": [120, 150, 180, 200],
                "type": "bar",
                "y_unit": "万元",
                "color": "#00ff9f"
            },
            {
                "name": "增长率",
                "data": [15, 25, 20, 35],
                "type": "line",
                "y_unit": "百分比",
                "color": "#ff6b6b"
            }
        ]
    }
    
    === 高级图表 ===
    
    2. 饼图 - 显示数据占比：
    {
        "chart_type": "pie",
        "data": [
            {"name": "移动端", "value": 335},
            {"name": "PC端", "value": 310},
            {"name": "平板", "value": 234},
            {"name": "其他", "value": 135}
        ]
    }
    
    3. 南丁格尔图（玫瑰图）- 美化的饼图，面积表示数值：
    {
        "chart_type": "rose",
        "data": [
            {"name": "研发", "value": 40},
            {"name": "市场", "value": 25},
            {"name": "销售", "value": 20},
            {"name": "运营", "value": 15}
        ]
    }
    
    4. 雷达图 - 多维度对比分析：
    {
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
    
    5. 漏斗图 - 转化流程分析：
    {
        "chart_type": "funnel",
        "data": [
            {"name": "访问", "value": 1000},
            {"name": "注册", "value": 800},
            {"name": "激活", "value": 600},
            {"name": "付费", "value": 300},
            {"name": "续费", "value": 150}
        ]
    }
    
    6. 词云图 - 文本数据可视化：
    {
        "chart_type": "wordcloud",
        "words": [
            {"name": "Python", "value": 1000},
            {"name": "JavaScript", "value": 800},
            {"name": "数据分析", "value": 700},
            {"name": "机器学习", "value": 600},
            {"name": "人工智能", "value": 500}
        ]
    }
    
    7. 热力图 - 数据密度分布：
    {
        "chart_type": "heatmap",
        "x_data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "y_data": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "data": [
            [0, 0, 5], [0, 1, 1], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0],
            [1, 0, 1], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 6, 0],
            [2, 0, 2], [2, 1, 2], [2, 2, 5], [2, 3, 4], [2, 4, 2], [2, 5, 4], [2, 6, 2]
        ],
        "max_value": 30
    }
    
    8. 桑基图 - 流向关系分析：
    {
        "chart_type": "sankey",
        "nodes": [
            {"name": "访问用户"},
            {"name": "注册用户"},
            {"name": "活跃用户"},
            {"name": "付费用户"},
            {"name": "流失用户"}
        ],
        "links": [
            {"source": "访问用户", "target": "注册用户", "value": 300},
            {"source": "访问用户", "target": "流失用户", "value": 200},
            {"source": "注册用户", "target": "活跃用户", "value": 200},
            {"source": "注册用户", "target": "流失用户", "value": 100},
            {"source": "活跃用户", "target": "付费用户", "value": 80}
        ]
    }
    
         9. 关系图 - 网络关系可视化：
     {
         "chart_type": "graph",
         "nodes": [
             {"id": "用户", "name": "用户", "symbolSize": 50, "category": 0},
             {"id": "产品", "name": "产品", "symbolSize": 40, "category": 1},
             {"id": "订单", "name": "订单", "symbolSize": 35, "category": 2},
             {"id": "支付", "name": "支付", "symbolSize": 30, "category": 2}
         ],
         "links": [
             {"source": "用户", "target": "产品", "value": 1},
             {"source": "用户", "target": "订单", "value": 2},
             {"source": "订单", "target": "支付", "value": 3}
         ],
         "categories": [
             {"name": "用户相关"},
             {"name": "产品相关"},
             {"name": "交易相关"}
         ]
     }
     
     10. 地图 - 智能地理数据可视化（支持自动地图层级检测和区域填充）：
     
     🎯 智能地图类型检测：系统会根据数据自动选择最适合的地图层级
     !重要,传入name的时候,不要加'省'或者'市',比如'山东'不要写成'山东省','济南'不要写成'济南市'
     
     a) 全国多省份地图（自动显示中国地图）：
     {
         "chart_type": "map",
         "regions": [
             {"name": "青海", "value": 2000},
             {"name": "福建", "value": 3000},
             {"name": "山东", "value": 2500},
             {"name": "广东", "value": 3500}
         ],
         "max_value": 4000
     }
     → 自动识别为多省份数据，显示中国地图，各省份区域用不同颜色填充
     
     b) 单省份地图（自动显示省级地图）：
     {
         "chart_type": "map",
         "regions": [
             {"name": "青海", "value": 2000}
         ],
         "max_value": 3000
     }
     → 自动识别为单省份数据，显示青海省地图，省内区域用颜色填充
     
     c) 省内多城市地图（自动显示省级地图）：
     {
         "chart_type": "map",
         "regions": [
             {"name": "济南", "value": 800},
             {"name": "青岛", "value": 900},
             {"name": "烟台", "value": 600},
             {"name": "日照", "value": 400}
         ],
         "max_value": 1000
     }
     → 自动识别为山东省城市数据，显示山东省地图，各城市区域用不同颜色填充
     
     d) 单城市地图（自动显示市级地图）：
     {
         "chart_type": "map",
         "regions": [
             {"name": "日照", "value": 500}
         ],
         "max_value": 1000
     }
     → 自动识别为单城市数据，显示日照市地图，市内区域用颜色填充
     
     🗺️ 支持的地图层级：
     - 国家级：中国地图（多省份数据时自动选择）
     - 省级：34个省/直辖市/自治区（山东、青海、北京、上海、广东、四川、江苏、浙江、河北、河南、湖北、湖南、安徽、福建、江西、辽宁、吉林、黑龙江、内蒙古、山西、陕西、甘肃、青海、宁夏、新疆、西藏、云南、贵州、重庆、天津、广西、海南等）
     - 市级：山东省16个市（济南、青岛、烟台、潍坊、临沂、淄博、济宁、泰安、聊城、威海、枣庄、德州、东营、菏泽、日照、滨州）
     
     📊 地图数据显示方式：
     - 区域填充：根据数值大小用渐变色填充对应区域（蓝色→黄色→红色）
     - 悬停提示：鼠标悬停显示区域名称和具体数值
     - 交互缩放：支持鼠标滚轮缩放和拖拽移动
     - 智能定位：自动设置最佳中心点和缩放级别
     
     🎨 地图参数说明：
     - chart_type: 固定为 "map"
     - regions: 区域数据数组，每个区域包含：
       - name: 区域名称（省份名、城市名或区县名）
       - value: 数值，用于颜色深浅映射
     - max_value: 可选，最大值用于颜色映射范围
     - map_type: 可选，通常不需要指定，系统会智能检测
     
     💡 地图使用场景：
     - 全国业务分布：多省份销售数据对比
     - 省内城市分析：省内各市业绩对比
     - 区域重点展示：单个省份或城市的详细数据
     - 地理数据可视化：人口、GDP、销售额等按地区展示
     
     📝 使用建议：
     - 多省份数据 → 自动显示中国地图
     - 单省份数据 → 自动显示该省地图  
     - 同省多城市 → 自动显示省级地图
     - 单城市数据 → 自动显示市级地图
     - 数据会以区域填充的方式显示，颜色深浅表示数值大小
    
    === 图表选择建议 ===
    - 数据对比 → 柱状图/混合图表
    - 趋势分析 → 折线图/混合图表
    - 占比分析 → 饼图/南丁格尔图
    - 多维对比 → 雷达图
    - 转化分析 → 漏斗图
    - 关键词分析 → 词云图
    - 时间/密度分布 → 热力图
    - 流程流向 → 桑基图
    - 关系网络 → 关系图
    - 地理数据可视化 → 智能地图（自动检测层级）
      * 全国多省份对比 → 自动显示中国地图 + 省份区域填充
      * 单省份展示 → 自动显示省级地图 + 区域填充
      * 省内多城市对比 → 自动显示省级地图 + 城市区域填充  
      * 单城市详情 → 自动显示市级地图 + 区域填充
      * 支持34个省份和山东省16个市的智能识别
    
    title: 图表标题（建议使用描述性标题）
    x_label: X轴标签（仅适用于有X轴的图表）
    userName: 调用时请传入你的名字，用于记录工具的调用者
    
    返回: 包含图表文件路径和特性说明的结果
    """
    # 记录详细的调用参数到控制台和普通日志
    logger.info("=" * 80)
    logger.info(f"🎨 MCP工具调用: drawChart")
    logger.info(f"📊 调用用户: {userName}")
    logger.info(f"📋 图表标题: {title}")
    logger.info(f"📐 X轴标签: {x_label}")
    logger.info(f"📊 数据类型: {type(data_input).__name__}")
    logger.info(f"📊 完整数据: {json.dumps(data_input, ensure_ascii=False, indent=2) if isinstance(data_input, dict) else str(data_input)}")
    
    # 同时记录到专门的MCP调用日志文件
    mcp_calls_logger.info("=" * 100)
    mcp_calls_logger.info(f"🎨 MCP工具调用: drawChart")
    mcp_calls_logger.info(f"📊 调用用户: {userName}")
    mcp_calls_logger.info(f"📋 图表标题: {title}")
    mcp_calls_logger.info(f"📐 X轴标签: {x_label}")
    mcp_calls_logger.info(f"📊 数据类型: {type(data_input).__name__}")
    mcp_calls_logger.info(f"📊 完整数据: {json.dumps(data_input, ensure_ascii=False, indent=2) if isinstance(data_input, dict) else str(data_input)}")
    
    # 根据数据类型记录详细信息
    if isinstance(data_input, dict):
        chart_type = data_input.get('chart_type', 'mixed')
        logger.info(f"📈 图表类型: {chart_type}")
        mcp_calls_logger.info(f"📈 图表类型: {chart_type}")
        
        if 'x_data' in data_input:
            logger.info(f"📊 X轴数据: {data_input['x_data']}")
            mcp_calls_logger.info(f"📊 X轴数据: {data_input['x_data']}")
            
        if 'series' in data_input:
            logger.info(f"📊 数据系列数量: {len(data_input['series'])}")
            mcp_calls_logger.info(f"📊 数据系列数量: {len(data_input['series'])}")
            for i, series in enumerate(data_input['series']):
                series_info = f"   系列{i+1}: {series.get('name', '未命名')} ({series.get('type', 'bar')})"
                logger.info(series_info)
                mcp_calls_logger.info(series_info)
                
        if 'data' in data_input:
            logger.info(f"📊 数据项数量: {len(data_input['data'])}")
            mcp_calls_logger.info(f"📊 数据项数量: {len(data_input['data'])}")
            
    elif isinstance(data_input, tuple):
        logger.info(f"📊 旧格式数据: {len(data_input)} 个参数")
        logger.info(f"   X轴数据: {data_input[0] if len(data_input) > 0 else 'None'}")
        logger.info(f"   Y轴数据: {data_input[1] if len(data_input) > 1 else 'None'}")
        logger.info(f"   图表类型: {data_input[2] if len(data_input) > 2 else 'bar'}")
        
        mcp_calls_logger.info(f"📊 旧格式数据: {len(data_input)} 个参数")
        mcp_calls_logger.info(f"   X轴数据: {data_input[0] if len(data_input) > 0 else 'None'}")
        mcp_calls_logger.info(f"   Y轴数据: {data_input[1] if len(data_input) > 1 else 'None'}")
        mcp_calls_logger.info(f"   图表类型: {data_input[2] if len(data_input) > 2 else 'bar'}")
    else:
        logger.info(f"📊 原始数据: {str(data_input)[:200]}...")
        mcp_calls_logger.info(f"📊 原始数据: {str(data_input)}")
    
    logger.info("-" * 80)
    mcp_calls_logger.info("-" * 100)
    
    try:
        result = draw_html_chart(data_input, title, x_label)
        send_external_message(result, userName, "success")
        logger.info(f"✅ 图表创建成功: {title}")
        logger.info(f"📁 文件路径: {result}")
        logger.info("=" * 80)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"❌ 图表创建失败: {str(e)}")
        logger.error(f"📊 失败数据: {str(data_input)[:500]}...")
        logger.error("=" * 80)
        return {"success": False, "error": str(e)}

async def main():
    """启动 MCP 服务器"""
    # 从配置文件读取设置，环境变量优先
    host = os.getenv("MCP_HOST", config.server_config.get('host', "0.0.0.0"))
    port = int(os.getenv("MCP_PORT", str(config.server_config.get('port', 8000))))
    path = os.getenv("MCP_PATH", config.server_config.get('path', "/sse"))
    
    logger.info(f"启动 MCP 服务器...")
    logger.info(f"地址: http://{host}:{port}{path}")
    
    # 记录已注册的工具
    logger.info(f"已注册工具: openWebsite, getDataFromDatabase, drawChart")
    
    try:
        await mcp.run_sse_async(host=host, port=port, path=path)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main()) 