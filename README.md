# Kerykeion MCP 工具

基于 [Kerykeion](https://www.kerykeion.net/) 库的占星计算 MCP 服务器。

## 功能特性

- **创建占星主体**: 使用 Kerykeion 的内置 JSON 序列化功能，返回完整的占星数据
- **本命相位分析**: 获取个人星盘中的行星相位关系
- **合盘相位分析**: 分析两个人之间的星盘相位关系
- **组合盘创建**: 生成中点合成盘用于关系分析
- **当前时间**: 获取系统当前时间信息

## 安装

### 使用 uvx（推荐）

```bash
# 直接运行
uvx kerykeion-mcp

# 或者通过 Python 模块运行
uvx python -m kerykeion_mcp.server
```

### 从源码安装

```bash
# 安装依赖
pip install kerykeion pydantic

# 或者使用 uv 包管理器
uv add kerykeion pydantic

# 运行
python -m kerykeion_mcp.server
```

### 开发环境安装

```bash
# 安装开发依赖
uv add --dev pytest pytest-cov black isort flake8 mypy

# 运行测试
uv run pytest

# 格式化代码
uv run black src/kerykeion_mcp tests
uv run isort src/kerykeion_mcp tests

# 类型检查
uv run mypy src/kerykeion_mcp
```

## 配置

将 `kerykeion_mcp_config.json` 文件添加到您的 MCP 客户端配置中：

```json
{
  "mcpServers": {
    "kerykeion": {
      "command": "uvx",
      "args": ["kerykeion-mcp"]
    }
  }
}
```

## 支持的功能

### 1. 获取当前时间
返回详细的系统时间信息。

### 2. 创建占星主体
- 支持城市名称查询（内置中国城市数据库）
- 支持直接经纬度输入
- 支持多种黄道类型（热带/恒星）
- 支持恒星模式选择（如 LAHIRI）

### 3. 本命相位分析
分析个人星盘中行星间的相位关系。

### 4. 合盘相位分析
分析两个人星盘间的相位关系，用于兼容性分析。

### 5. 组合盘创建
创建中点合成盘，用于关系占星学分析。

## JSON 支持

本工具充分利用了 Kerykeion 的 [JSON 支持功能](https://www.kerykeion.net/pydocs/kerykeion.html#json-support)，直接返回 `AstrologicalSubject.json()` 序列化的完整数据，而不是手动提取属性。

## 使用示例

通过 MCP 客户端调用相应的工具函数，传入所需的参数即可获得占星数据。

## 打包发布

### 构建包

```bash
# 构建 wheel 和 sdist
uv build

# 或者使用 hatchling 直接构建
python -m build
```

### 发布到 PyPI

```bash
# 安装发布工具
uv add --dev twine

# 上传到 PyPI
uv run twine upload dist/*
```

### 安装已发布的包

```bash
# 安装发布后的包
pip install kerykeion-mcp

# 或者使用 uvx 运行
uvx kerykeion-mcp
```

## 注意事项

- 确保网络连接正常（用于城市名称查询）
- 推荐提供经纬度和时区以获得最准确的结果
- 支持的国家代码：US, GB, CN 等标准代码
- 内置了中国主要城市的坐标数据，无需网络查询

## 项目结构

```
kerykeion-mcp/
├── src/kerykeion_mcp/
│   ├── __init__.py          # 包初始化
│   ├── core.py              # 核心占星计算功能
│   ├── server.py            # MCP 服务器入口
│   └── china_cities.json    # 中国城市坐标数据
├── tests/                   # 测试文件
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
├── LICENSE                 # 许可证
└── MANIFEST.in            # 包包含文件清单
```

## 许可证

本工具基于 Kerykeion 库，请遵守相应的开源许可证。