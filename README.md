# 🌤️ 天气 Agent

> 基于 LangChain 的智能天气预报助手，支持自然语言查询，说话喜欢用双关语


## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🗣️ **自然语言交互** | 直接说"长沙今天怎么样啊"即可查询 |
| 🌍 **城市自动识别** | 从对话中自动提取城市名，无需手动指定 |
| 💬 **多轮对话** | 支持上下文理解，可连续查询多个城市 |
| 😄 **双关语风格** | AI 回复幽默风趣，带天气双关语 |
| 🧠 **智能记忆** | 自动保存对话历史，上下文不丢失 |
| 📋 **结构化输出** | 支持格式化响应，便于程序处理 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install langchain langchain-core langgraph
2. 运行代码
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from pydantic.dataclasses import dataclass

# 定义天气查询工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气."""
    return f"在这个 {city} 总是阳光明媚!"

# 定义城市提取工具
@tool
def get_user_location(**kwargs) -> str:
    """从用户输入中提取城市名。"""
    config = kwargs.get('config', {})
    messages = config.get('configurable', {}).get('messages', [])
    
    if messages:
        content = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        cities = ["长沙", "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "重庆"]
        for city in cities:
            if city in content:
                return city
    return "北京"

# 创建 Agent
checkpointer = InMemorySaver()
agent = create_agent(
    model=llm,
    system_prompt="你是一位天气预报专家，说话喜欢用双关语",
    tools=[get_user_location, get_weather_for_location],
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
在这个 长沙 总是阳光明媚!
示例 2：多轮对话
# 第一轮
response = agent.invoke(
    {"messages": [{"role": "user", "content": "长沙今天怎么样啊？"}]},
    config=config,
    context=Context(user_id="1")
)

# 第二轮（保持同一个 thread_id）
response = agent.invoke(
    {"messages": [{"role": "user", "content": "谢谢!"}]},
    config=config,
    context=Context(user_id="1")
)
输出：

不客气！在长沙，阳光总是"湘"伴您左右～
如果天气有变，记得带伞哦！☂️
示例 3：查询不同城市
输入：

用户：北京天气如何？
用户：那上海呢？
用户：广州明天会下雨吗？
输出：

AI: 在北京，阳光总是"京"彩不断！☀️...
AI: 在上海，阳光总是"沪"你周全！☀️...
AI: 在广州，阳光总是"广"阔无云！☀️...
🏗️ 项目结构
langchain 练习/
├── 02agent 天气.py          # 主程序
├── init_llm.py              # LLM 初始化配置
└── README.md                # 项目文档
⚙️ 核心组件详解
1. 系统提示词
SYSTEM_PROMPT = """
你是一位天气预报专家，说话总是喜欢用双关语。 
您可以访问两个工具： 
- get_weather_for_location：使用它来获取给定城市的天气 
- get_user_location：使用它来获取用户的城市地址 
如果用户向你询问天气，确保你知道它的位置。
"""
2. 天气查询工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气."""
    return f"在这个 {city} 总是阳光明媚!"
说明：

@tool 装饰器将函数转换为 LangChain 工具
文档字符串告诉 Agent 这个工具的用途
当前返回模拟数据，可替换为真实 API 调用
3. 城市提取工具
@tool
def get_user_location(**kwargs) -> str:
    """从用户输入中提取城市名。从对话历史中查找用户提到的城市。"""
    config = kwargs.get('config', {})
    messages = config.get('configurable', {}).get('messages', [])
    
    if messages:
        last_message = messages[-1]
        content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        cities = ["长沙", "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "重庆"]
        for city in cities:
            if city in content:
                return city
    
    return "北京"
说明：

使用 **kwargs 接收运行时配置
从对话历史中提取用户消息
遍历城市列表，匹配提到的城市名
4. 上下文管理
@dataclass
class Context:
    """自定义运行时上下文模式."""
    user_id: str
说明：

用于传递用户 ID 等运行时信息
支持多用户会话隔离
5. 结构化输出
@dataclass
class ResponseFormat:
    """agent 的响应模式."""
    punny_response: str              # 双关语回复
    weather_conditions: str | None = None  # 天气详情（可选）
说明：

强制 Agent 输出结构化数据
便于程序解析和处理
6. 对话记忆
checkpointer = InMemorySaver()

agent = create_agent(
    ...
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}
说明：

InMemorySaver 保存对话状态
thread_id 唯一标识一个会话
相同 thread_id 的调用共享对话历史
🧪 完整测试代码
# 测试用例
test_cases = [
    "长沙今天怎么样啊？",
    "北京天气如何？",
    "今天天气怎么样？",  # 未指定城市
    "那上海呢？",        # 多轮对话
]

for user_input in test_cases:
    print(f"\n用户：{user_input}")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        context=Context(user_id="1")
    )
    
    if 'messages' in response:
        last_message = response['messages'][-1]
        print(f"AI: {last_message.content}")
📊 响应结构
{
    'messages': [
        HumanMessage(content='长沙今天怎么样啊？'),
        AIMessage(content='', tool_calls=[{'name': 'get_user_location', 'args': {...}}]),
        ToolMessage(content='长沙', name='get_user_location'),
        AIMessage(content='', tool_calls=[{'name': 'get_weather_for_location', 'args': {'city': '长沙'}}]),
        ToolMessage(content='在这个 长沙 总是阳光明媚!', name='get_weather_for_location'),
        AIMessage(content='在长沙，阳光总是"湘"伴您左右！☀️...'),
    ],
    'structured_response': {
        'punny_response': '在长沙，阳光总是"湘"伴您左右！☀️',
        'weather_conditions': '在这个 长沙 总是阳光明媚!'
    }
}
