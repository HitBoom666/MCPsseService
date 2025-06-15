# AIKnowledgeStorage MCP Server (独立版本)

这是从主项目中分离出来的独立 MCP 服务器，支持 SSE (Server-Sent Events) 模式。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python server.py
```
或者使用启动脚本：
```bash
start_server.bat  # Windows
```

### 3. 验证服务器
服务器启动后，访问：http://localhost:8000/sse

## 📁 目录结构

```
MCP-Server-Standalone/
├── server.py              # MCP 服务器主程序
├── requirements.txt       # 依赖文件
├── start_server.bat      # Windows 启动脚本
├── README.md             # 说明文档
├── src/                  # 源代码
│   ├── tools/           # 工具模块
│   └── database/        # 数据库模块
├── config/              # 配置文件
│   └── server_config.json
└── logs/                # 日志文件
    └── mcp_server.log
```

## 🔧 配置

### 环境变量
- `MCP_HOST`: 服务器主机地址 (默认: 0.0.0.0)
- `MCP_PORT`: 服务器端口 (默认: 8000)
- `MCP_PATH`: SSE 路径 (默认: /sse)

### 示例
```bash
set MCP_HOST=127.0.0.1
set MCP_PORT=8001
python server.py
```

## 🛠️ 工具列表

1. **openWebsite**: 打开指定网页
2. **getDataFromDatabase**: 查询数据库数据
3. **drawChart**: 生成图表

## 🔗 连接到主项目

在主项目的 `config.py` 中配置：
```python
MCP_CONFIGS = {
    "mode": "sse",
    "sse": {
        "primary": {
            "url": "http://127.0.0.1:8000/sse"
        }
    }
}
```

## 📋 部署说明

### 复制到外部项目
1. 复制整个 `MCP-Server-Standalone` 目录
2. 确保数据库文件路径正确
3. 安装依赖并启动服务器

### Docker 部署
可以基于此目录创建 Docker 镜像进行容器化部署。

## 🚨 故障排除

### 常见问题
1. **端口被占用**: 修改 `MCP_PORT` 环境变量
2. **数据库路径错误**: 检查 `config/server_config.json` 中的路径
3. **依赖缺失**: 运行 `pip install -r requirements.txt`

### 日志查看
```bash
tail -f logs/mcp_server.log  # Linux/Mac
type logs\mcp_server.log     # Windows
```

## 📞 支持

如有问题，请检查：
1. 日志文件 `logs/mcp_server.log`
2. 配置文件 `config/server_config.json`
3. 网络连接和端口状态 