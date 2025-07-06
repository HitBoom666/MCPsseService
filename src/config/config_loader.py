import json
import os
from pathlib import Path

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'server_config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 设置默认配置
            #self._config = self._get_default_config()

    # def _get_default_config(self):
    #     """获取默认配置"""
    #     return {
    #         "server": {
    #             "host": "0.0.0.0",
    #             "port": 8000,
    #             "path": "/sse"
    #         },
    #         "logging": {
    #             "level": "INFO",
    #             "file": "logs/mcp_server.log"
    #         },
    #         "database": {
    #             "path": "src/database/Data/project_storage.db",
    #             "name": "project_storage.db"
    #         },
    #         "charts": {
    #             "output_dir": "WebSite\\static\\charts",
    #             "figsize": [12, 7],
    #             "dpi": 300,
    #             "background_color": "#1a1a1a",
    #             "font_family": "SimHei"
    #         },
    #         "mcp_pipe": {
    #             "process_timeout": 5,
    #             "initial_backoff": 1,
    #             "max_backoff": 600
    #         }
    #     }

    @property
    def server_config(self):
        """获取服务器配置"""
        return self._config.get('server', {})

    @property
    def logging_config(self):
        """获取日志配置"""
        return self._config.get('logging', {})

    @property
    def database_config(self):
        """获取数据库配置"""
        return self._config.get('database', {})

    @property
    def charts_config(self):
        """获取图表配置"""
        return self._config.get('charts', {})

    @property
    def mcp_pipe_config(self):
        """获取MCP管道配置"""
        return self._config.get('mcp_pipe', {})

    def get_config(self, key, default=None):
        """获取配置值"""
        return self._config.get(key, default) 