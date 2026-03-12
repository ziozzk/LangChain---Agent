# 🌤️ 天气 Agent

> 基于 LangChain 的智能天气预报助手，支持自然语言查询，说话喜欢用双关语

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/langchain-1.0+-green.svg)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/langgraph-latest-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🗣️ **自然语言交互** | 直接说"长沙今天怎么样啊"即可查询 |
| 🌍 **城市自动识别** | 从对话中自动提取城市名 |
| 📊 **真实天气数据** | 接入和风天气 API，返回实时天气 |
| 💬 **多轮对话** | 支持上下文理解，可连续查询多个城市 |
| 😄 **双关语风格** | AI 回复幽默风趣，带天气双关语 |
| 🧠 **智能记忆** | 自动保存对话历史，上下文不丢失 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install langchain langchain-core langgraph requests
2. 配置 API Key
在代码中设置和风天气 API Key：

API_KEY = "你的和风天气 API Key"  # 替换为你的 Key
3. 运行示例
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# 定义工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气"""
    import requests
    API_KEY = "b5bf68e9f400eccb808c33e993045d7"
    # ... 天气查询逻辑
    return f"{city} 今天晴，气温 25°C"

# 创建 Agent
checkpointer = InMemorySaver()
agent = create_agent(
    model=llm,
    system_prompt="你是一位天气预报专家，说话喜欢用双关语",
    tools=[get_weather_for_location],
    checkpointer=checkpointer
)

# 调用
response = agent.invoke(
    {"messages": [{"role": "user", "content": "长沙今天怎么样啊？"}]},
    config={"configurable": {"thread_id": "1"}}
)
📋 使用示例
示例 1：查询单个城市
输入：

长沙今天怎么样啊？
输出：

在长沙，阳光总是"湘"伴您左右！☀️
长沙 今天多云，气温 28°C，体感 30°C，东南风 3 级，湿度 65%～
示例 2：多轮对话
输入：

用户：北京天气如何？
AI: 在北京，阳光总是"京"彩不断！☀️...

用户：那上海呢？
AI: 在上海，阳光总是"沪"你周全！☀️...
示例 3：未指定城市
输入：

今天天气怎么样？
输出：

亲，您想知道哪个城市的天气呢？🌤️
请告诉我城市名，我马上帮您查询！
🏗️ 项目结构
langchain 练习/
├── 02agent 天气.py          # 主程序
├── init_llm.py              # LLM 初始化配置
├── requirements.txt         # 依赖列表
└── README.md               # 项目文档
⚙️ 配置说明
和风天气 API
获取 API Key

访问 https://dev.qweather.com/
注册账号并创建项目
获取 API Key（免费版每天 1000 次调用）
API 端点

城市搜索：https://devapi.qweather.com/v2/city/lookup
实时天气：https://devapi.qweather.com/v7/weather/now
替换 Key

API_KEY = "你的 API Key"  # 在 get_weather_for_location 函数中
模型配置
在 init_llm.py 中配置 LLM：

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    temperature=0.7,
    api_key="你的 API Key",
    base_url="https://your-api-endpoint.com"
)
🛠️ 核心组件
1. 天气查询工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气"""
    # 1. 根据城市名获取城市 ID
    # 2. 根据城市 ID 查询实时天气
    # 3. 返回格式化的天气信息
2. 城市提取工具
@tool
def get_user_location(**kwargs) -> str:
    """从用户输入中提取城市名"""
    # 从对话历史中查找提到的城市
    # 支持：长沙、北京、上海、广州等 10+ 城市
3. 对话记忆
checkpointer = InMemorySaver()  # 保存对话状态
config = {"configurable": {"thread_id": "1"}}  # 会话 ID
📊 API 响应示例
成功响应
{
  "code": "200",
  "now": {
    "obsTime": "2026-03-12T18:30+08:00",
    "temp": "25",
    "feelsLike": "27",
    "text": "多云",
    "windDir": "东南风",
    "windScale": "3",
    "humidity": "65"
  }
}
格式化输出
长沙 今天多云，气温 25°C，体感 27°C，东南风 3 级，湿度 65%～
🧪 测试用例
测试场景	输入	预期行为
正常查询	"长沙今天怎么样啊？"	返回长沙天气
多轮对话	"那上海呢？"	结合上下文返回上海天气
无城市	"今天天气怎么样？"	追问用户哪个城市
无效城市	"XXX 市天气"	提示找不到城市
网络超时	-	返回友好错误提示
⚠️ 注意事项
问题	解决方案
API Key 无效	检查和风天气控制台，确认 Key 有效
调用超限	免费版每天 1000 次，升级或等待次日
网络超时	添加 timeout 参数和重试机制
城市名不匹配	扩展城市列表或使用模糊匹配
🚀 扩展功能
1. 添加更多城市
cities = ["长沙", "北京", "上海", ... , "你的城市"]
2. 接入真实天气 API
# 已在代码中实现，替换 API Key 即可
3. 添加天气预报
# 使用 /v7/weather/3d 接口获取 3 天预报
4. 添加空气质量
# 使用 /v7/air/now 接口获取 AQI 数据
📚 相关资源
LangChain 官方文档
LangGraph 文档
和风天气 API 文档
OpenAI API 文档
🤝 贡献指南
欢迎提交 Issue 和 Pull Request！

Fork 本项目
创建功能分支 (git checkout -b feature/AmazingFeature)
提交更改 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
提交 Pull Request
📝 许可证
本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情。

🙏 致谢
LangChain - AI 应用开发框架
和风天气 - 提供天气数据 API
