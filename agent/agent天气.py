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
    import requests

    # 和风天气 API 配置（来自正常运行的项目）
    API_KEY = "5b35994e5da24b1d9d8c0a72f036d7f1"
    API_HOST = "n76hexkpa5.re.qweatherapi.com"

    try:
        # 步骤 1: 根据城市名获取城市 ID
        geo_response = requests.get(
            f"https://{API_HOST}/geo/v2/city/lookup",
            params={"location": city, "key": API_KEY},
            timeout=5
        )
        geo_data = geo_response.json()

        if geo_data.get("code") != "200" or not geo_data.get("location"):
            return f"抱歉，找不到 {city} 这个城市～"

        city_id = geo_data["location"][0]["id"]
        city_name = geo_data["location"][0]["name"]

        # 步骤 2: 根据城市 ID 获取实时天气
        weather_response = requests.get(
            f"https://{API_HOST}/v7/weather/now",
            params={"location": city_id, "key": API_KEY},
            timeout=5
        )
        weather_data = weather_response.json()

        if weather_data.get("code") != "200":
            return f"抱歉，无法获取 {city_name} 的天气～"

        # 提取天气数据
        now = weather_data["now"]
        temp = now.get("temp", "?")
        feels_like = now.get("feelsLike", "?")
        text = now.get("text", "?")
        wind_dir = now.get("windDir", "?")
        wind_scale = now.get("windScale", "?")
        humidity = now.get("humidity", "?")
        pressure = now.get("pressure", "?")
        vis = now.get("vis", "?")

        return (f"{city_name} 今天{text}，气温{temp}°C，体感{feels_like}°C，"
                f"{wind_dir}{wind_scale}级，湿度{humidity}%，"
                f"气压{pressure}hPa，能见度{vis}km～")

    except requests.Timeout:
        return f"抱歉，天气查询超时了～"
    except Exception:
        return f"抱歉，天气查询出错了～"


@dataclass
class Context:
    """自定义运行时上下文模式."""
    user_id: str


@tool
def get_user_location(**kwargs) -> str:
    """根据用户输入提取城市名。从对话历史中查找用户提到的城市。"""
    config = kwargs.get('config', {})
    messages = config.get('configurable', {}).get('messages', [])

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