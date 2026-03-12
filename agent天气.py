from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from pydantic.dataclasses import dataclass

from langchain练习.init_llm import llm

SYSTEM_PROMPT = """
你是一位天气预报专家，说话总是喜欢用双关语。 
您可以访问两个工具： 
- get_weather_for_location：使用它来获取给定城市的天气 
- get_user_location：使用它来获取用户的城市地址 
如果用户向你询问天气，确保你知道它的位置。如果您可以从问题中知道它们的意思，那么可以使用 get_user_location 工具找到它们的位置。
"""


@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气."""
    return f"在这个 {city} 总是阳光明媚!"


@dataclass
class Context:
    """自定义运行时上下文模式."""
    user_id: str


@tool
def get_user_location(**kwargs) -> str:
    """根据用户输入提取城市名。从对话历史中查找用户提到的城市。"""
    # 从 kwargs 中获取配置信息
    config = kwargs.get('config', {})

    # 获取对话历史中的用户输入
    messages = config.get('configurable', {}).get('messages', [])

    # 从最后一条用户消息中提取城市名
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            content = last_message.content
        else:
            content = str(last_message)

        cities = ["长沙", "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "重庆"]
        for city in cities:
            if city in content:
                return city

    # 默认返回
    return "北京"


model = llm


@dataclass
class ResponseFormat:
    """agent 的响应模式."""
    punny_response: str
    weather_conditions: str | None = None


checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "长沙今天怎么样啊？"}]},
    config=config,
    context=Context(user_id="1")
)

print("完整响应结构:")
print(response)
print("\n" + "=" * 50 + "\n")

if 'messages' in response:
    last_message = response['messages'][-1]
    if hasattr(last_message, 'content'):
        print("AI 回复内容:")
        print(last_message.content)

if 'structured_response' in response:
    print("\n结构化响应:")
    print(response['structured_response'])

response = agent.invoke(
    {"messages": [{"role": "user", "content": "谢谢!"}]},
    config=config,
    context=Context(user_id="1")
)

print("\n" + "=" * 50 + "\n")
print("第二轮会话回复:")

if 'messages' in response:
    last_message = response['messages'][-1]
    if hasattr(last_message, 'content'):
        print(last_message.content)