"""
独立的 MCP 服务器
支持 SSE 模式，可独立部署
"""
import logging
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.db_reader import DatabaseReader
from src.tools.chart_utils import draw_chart
from src.tools.web_control import open_website
from fastmcp import FastMCP
from src.config.config_loader import ConfigLoader

# 获取配置
config = ConfigLoader()

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.logging_config.get('level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging_config.get('file', 'logs/mcp_server.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mcp_server')

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
def drawChart(data_input, title="多系列图表", x_label="X轴") -> dict:
    """
    绘制支持多组数据和混合图表类型的图表
    important!!! 如果想要在一张图表中绘制多组数据，或绘制折线图柱状图混合图表，请在series中添加多组数据。
    在传入json的时候，如果你能获取到相应数据，各个字段请确保有确切清晰的值，比如x_data的值是具体的项目名称而不是项目A。
    参数:
    data_input: 数据输入，支持两种格式：
        JSON格式字符串或字典（推荐）:
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

    title: 图表标题
    x_label: X轴标签
    """
    try:
        result = draw_chart(data_input, title, x_label)
        logger.info(f"成功创建图表: {title}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"图表创建失败: {str(e)}")
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