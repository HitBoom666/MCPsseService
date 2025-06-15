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

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp_server.log'),
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
def drawChart(x_str: str, y_str: str, chart_type: str = 'bar', 
              title: str = "图表", x_label: str = "X轴", y_label: str = "Y轴", 
              color: str = '#00ff9f', bar_width: float = 0.5, marker: str = 'o') -> dict:
    """绘制图表
    
    Args:
        x_str: X轴数据，逗号分隔
        y_str: Y轴数据，逗号分隔
        chart_type: 图表类型 ('bar' 或 'line')
        title: 图表标题
        x_label: X轴标签
        y_label: Y轴标签
        color: 图表颜色
        bar_width: 柱状图宽度
        marker: 折线图标记
        
    Returns:
        dict: 图表生成结果
    """
    try:
        result = draw_chart(x_str, y_str, chart_type, title, x_label, y_label, color, bar_width, marker)
        logger.info(f"成功创建图表: {title}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"图表创建失败: {str(e)}")
        return {"success": False, "error": str(e)}

async def main():
    """启动 MCP 服务器"""
    # 从环境变量或配置文件读取设置
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    path = os.getenv("MCP_PATH", "/sse")
    
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