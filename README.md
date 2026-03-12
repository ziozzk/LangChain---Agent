# 🌤️ 天气 Agent
> 基于 LangChain 的智能天气预报助手，支持自然语言查询，说话喜欢用双关语

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🗣️ **自然语言交互** | 直接说"长沙今天怎么样啊"即可查询 |
| 🌍 **城市自动识别** | 从对话中自动提取城市名，无需手动指定 |
| 🌡️ **真实天气数据** | 接入和风天气 API，返回实时温度、湿度、风力等 |
| 💬 **多轮对话** | 支持上下文理解，可连续查询多个城市 |
| 😄 **双关语风格** | AI 回复幽默风趣，带天气双关语 |
| 🧠 **智能记忆** | 自动保存对话历史，上下文不丢失 |
| 📋 **结构化输出** | 支持格式化响应，便于程序处理 |

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install langchain langchain-core langgraph requests
```

### 2. 配置 API Key
在代码中设置和风天气 API 凭据：
```python
# 和风天气 API 配置
API_KEY = "你的 API Key"  # 从和风天气控制台获取
API_HOST = "你的服务器地址"  # 如 n76hexkpa5.re.qweatherapi.com
```

### 3. 运行示例
```python
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
# 需自行实现 llm 初始化（例如从 init_llm.py 导入）
from init_llm import llm  

# 定义天气查询工具
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气"""
    import requests
    
    API_KEY = "你的 API Key"
    API_HOST = "你的服务器地址"
    
    # 1. 获取城市 ID
    geo_response = requests.get(
        f"https://{API_HOST}/geo/v2/city/lookup",
        params={"location": city, "key": API_KEY}
    )
    city_id = geo_response.json()["location"][0]["id"]
    
    # 2. 查询天气
    weather_response = requests.get(
        f"https://{API_HOST}/v7/weather/now",
        params={"location": city_id, "key": API_KEY}
    )
    now = weather_response.json()["now"]
    
    return f"{city} 今天{now['text']}，气温{now['temp']}°C"

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
```

---

## 📋 使用示例

### 示例 1：查询单个城市
**输入**：
```
长沙今天怎么样啊？
```
**输出**：
```
在长沙，阳光总是"湘"伴您左右！☀️
长沙 今天多云，气温 28°C，体感 30°C，东南风 3 级，湿度 65%，气压 1013hPa，能见度 16km～
```

### 示例 2：多轮对话
```python
# 第一轮
config = {"configurable": {"thread_id": "1"}}
response = agent.invoke(
    {"messages": [{"role": "user", "content": "长沙今天怎么样啊？"}]},
    config=config
)

# 第二轮（保持同一个 thread_id）
response = agent.invoke(
    {"messages": [{"role": "user", "content": "谢谢!"}]},
    config=config
)
```
**输出**：
```
第一轮：在长沙，阳光总是"湘"伴您左右！☀️...
第二轮：不客气！在长沙，阳光总是"湘"伴您左右～如果天气有变，记得带伞哦！☂️
```

### 示例 3：查询不同城市
**输入**：
```
用户：北京天气如何？
用户：那上海呢？
用户：广州明天会下雨吗？
```
**输出**：
```
AI: 在北京，阳光总是"京"彩不断！☀️ 北京 今天晴，气温 22°C...
AI: 在上海，阳光总是"沪"你周全！☀️ 上海 今天多云，气温 25°C...
AI: 在广州，阳光总是"广"阔无云！☀️ 广州 今天小雨，气温 27°C...
```

---

## 🏗️ 项目结构
```
langchain 练习/
├── 02agent 天气.py          # 主程序
├── init_llm.py              # LLM 初始化配置
└── README.md                # 项目文档
```

---

## ⚙️ 核心组件详解

### 1. 系统提示词
```python
SYSTEM_PROMPT = """
你是一位天气预报专家，说话总是喜欢用双关语。 
您可以访问两个工具： 
- get_weather_for_location：使用它来获取给定城市的天气 
- get_user_location：使用它来获取用户的城市地址 
如果用户向你询问天气，确保你知道它的位置。
"""
```

### 2. 天气查询工具（接入和风天气 API）
```python
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气."""
    import requests
    
    API_KEY = ""  # 替换为你的 API Key
    API_HOST = ""  # 替换为你的服务器地址
    
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
```

### 3. 城市提取工具
```python
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
```

### 4. 上下文管理
```python
from dataclasses import dataclass

@dataclass
class Context:
    """自定义运行时上下文模式."""
    user_id: str
```

### 5. 结构化输出
```python
from dataclasses import dataclass

@dataclass
class ResponseFormat:
    """agent 的响应模式."""
    punny_response: str              # 双关语回复
    weather_conditions: str | None = None  # 天气详情（可选）
```

### 6. 对话记忆
```python
checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}

# 相同 thread_id 的调用共享对话历史
response = agent.invoke(..., config=config)
```

---

## 📊 API 响应示例

### 城市搜索响应
```json
{
  "code": "200",
  "location": [
    {
      "id": "101250101",
      "name": "长沙",
      "lat": "28.20",
      "lon": "112.97"
    }
  ]
}
```

### 天气查询响应
```json
{
  "code": "200",
  "updateTime": "2026-03-12T19:00+08:00",
  "now": {
    "obsTime": "2026-03-12T19:00+08:00",
    "temp": "28",
    "feelsLike": "30",
    "icon": "101",
    "text": "多云",
    "wind360": "135",
    "windDir": "东南风",
    "windScale": "3",
    "windSpeed": "15",
    "humidity": "65",
    "precip": "0.0",
    "pressure": "1013",
    "vis": "16",
    "cloud": "50",
    "dew": "21"
  }
}
```

### 格式化输出
```
长沙 今天多云，气温 28°C，体感 30°C，东南风 3 级，湿度 65%，气压 1013hPa，能见度 16km～
```

---

## 🧪 测试用例

| 测试场景 | 输入 | 预期行为 |
|----------|------|----------|
| 正常查询 | "长沙今天怎么样啊？" | 返回长沙真实天气 |
| 多轮对话 | "那上海呢？" | 结合上下文返回上海天气 |
| 无城市 | "今天天气怎么样？" | 追问用户哪个城市 |
| 无效城市 | "XXX 市天气" | 提示找不到城市 |
| 网络超时 | - | 返回友好错误提示 |

---

## ⚠️ 注意事项

| 问题 | 解决方案 |
|------|----------|
| API Key 无效 | 检查和风天气控制台，确认 Key 有效 |
| 调用超限 | 免费版每天 1000 次，升级或等待次日 |
| 网络超时 | 添加 timeout 参数和重试机制 |
| 城市名不匹配 | 扩展城市列表或使用模糊匹配 |
| API_HOST 错误 | 使用控制台中分配的服务器地址 |

---

## 🚀 扩展建议

### 1. 添加更多城市
```python
cities = [
    "长沙", "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "重庆",
    "天津", "西安", "苏州", "青岛", "郑州", "沈阳", "大连", "厦门", "昆明", "哈尔滨"
]
```

### 2. 添加天气预报
```python
# 使用 /v7/weather/3d 接口获取 3 天预报
weather_response = requests.get(
    f"https://{API_HOST}/v7/weather/3d",
    params={"location": city_id, "key": API_KEY}
)
```

### 3. 添加空气质量
```python
# 使用 /v7/air/now 接口获取 AQI 数据
air_response = requests.get(
    f"https://{API_HOST}/v7/air/now",
    params={"location": city_id, "key": API_KEY}
)
```

### 4. 添加生活指数
```python
# 使用 /v7/indices/1d 接口获取生活指数
indices_response = requests.get(
    f"https://{API_HOST}/v7/indices/1d",
    params={"location": city_id, "key": API_KEY, "type": "1,2,3,5,8"}
)
```
