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
     
     10. 地图 - 地理数据可视化（支持区域数据、散点、热力图）：
     
     a) 基础区域地图（省份数据可视化）：
     {
         "chart_type": "map",
         "map_type": "china",
         "regions": [
             {"name": "北京", "value": 177},
             {"name": "天津", "value": 42},
             {"name": "河北", "value": 102},
             {"name": "山西", "value": 81},
             {"name": "上海", "value": 24},
             {"name": "江苏", "value": 92},
             {"name": "浙江", "value": 114},
             {"name": "广东", "value": 123},
             {"name": "四川", "value": 125},
             {"name": "重庆", "value": 91}
         ],
         "max_value": 200
     }
     
     b) 城市散点地图（显示城市位置和数据）：
     {
         "chart_type": "map",
         "map_type": "china",
         "scatter_data": [
             {"name": "北京", "value": [116.46, 39.92, 95]},
             {"name": "上海", "value": [121.48, 31.22, 85]},
             {"name": "广州", "value": [113.23, 23.16, 78]},
             {"name": "深圳", "value": [114.07, 22.62, 75]},
             {"name": "西安", "value": [108.95, 34.27, 68]},
             {"name": "重庆", "value": [106.54, 29.59, 65]}
         ]
     }
     
     c) 复合地图（区域+散点）：
     {
         "chart_type": "map",
         "map_type": "china",
         "regions": [
             {"name": "北京", "value": 177},
             {"name": "上海", "value": 124},
             {"name": "广东", "value": 223},
             {"name": "四川", "value": 125},
             {"name": "江苏", "value": 92}
         ],
         "scatter_data": [
             {"name": "北京", "value": [116.46, 39.92, 95]},
             {"name": "上海", "value": [121.48, 31.22, 85]},
             {"name": "广州", "value": [113.23, 23.16, 78]},
             {"name": "深圳", "value": [114.07, 22.62, 75]}
         ],
         "max_value": 300
     }
     
     地图参数说明：
     - map_type: 地图类型，目前支持 "china"（中国地图）
     - regions: 省份/区域数据，显示为有颜色填充的区域
       - name: 省份名称（如"北京"、"上海"、"广东"等）
       - value: 数值，用于颜色映射
     - scatter_data: 散点数据，显示为地图上的标记点
       - name: 城市名称
       - value: [经度, 纬度, 数值]，经纬度用于定位，数值用于大小
     - max_value: 最大值，用于颜色映射范围
     
     地图使用场景：
     - 省份数据对比（GDP、人口、销售额等）
     - 城市分布展示（分公司、用户分布等）
     - 地理位置分析（物流、覆盖范围等）
     - 区域业绩可视化（销售区域、市场份额等）
    
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
    - 地理数据可视化 → 地图
      * 省份数据对比 → 区域地图（regions）
      * 城市位置展示 → 散点地图（scatter_data）
      * 综合地理分析 → 复合地图（regions + scatter_data）
      * 全国业务分布 → 地图 + 数据标注
    
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