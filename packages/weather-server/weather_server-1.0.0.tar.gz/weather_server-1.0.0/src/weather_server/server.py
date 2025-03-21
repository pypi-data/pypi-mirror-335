'''
Author: Mr.Car
Date: 2025-03-20 20:18:33
'''
from fastmcp import FastMCP
import httpx
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import pinyin

load_dotenv()

# 定义天气数据类
@dataclass
class WeatherData:
    description: str
    temperature: float
    humidity: int
    wind_speed: float
    city: str

    def format_message(self) -> str:
        return f"当前{self.city}的天气：{self.description}，温度{self.temperature}°C，湿度{self.humidity}%，风速{self.wind_speed}米/秒"

# 添加天气预报数据类
@dataclass
class ForecastData:
    date: str
    description: str
    temp_min: float
    temp_max: float
    humidity: int
    wind_speed: float
    city: str

    def format_message(self) -> str:
        return f"{self.date} {self.city}的天气预报：{self.description}，温度{self.temp_min}°C至{self.temp_max}°C，湿度{self.humidity}%，风速{self.wind_speed}米/秒"

# 初始化 FastMCP 服务器
server = FastMCP()

class CityNameConverter:
    def __init__(self):
        # 基础城市映射
        self._city_map = {
            "苏州": "suzhou",
            "北京": "beijing",
            "上海": "shanghai",
            "广州": "guangzhou",
            "深圳": "shenzhen",
        }
    
    def to_english(self, city: str) -> str:
        """
        将城市名转换为英文，使用多种策略：
        1. 直接映射
        2. 拼音转换（去声调）
        3. 如果已经是英文则保持不变
        """
        # 如果已经在映射表中，直接返回
        if city in self._city_map:
            return self._city_map[city]
            
        # 如果输入是英文，直接返回
        if all(ord(c) < 128 for c in city):
            return city.lower()
            
        # 尝试转换为拼音（去掉声调和空格）
        try:
            # 移除特殊字符
            city = ''.join(c for c in city if c.isalnum() or c.isspace())
            py = pinyin.get(city, format="strip")
            return py.lower().replace(" ", "")
        except:
            # 如果转换失败，返回原始输入
            return city

# 创建转换器实例
city_converter = CityNameConverter()

@server.tool()
async def get_weather(
    city: str,
    units: str = "metric",
    lang: str = "zh_cn"
) -> WeatherData:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称（支持中文或英文，如：苏州、suzhou）
        units: 温度单位 (metric: 摄氏度, imperial: 华氏度)
        lang: 返回语言 (zh_cn: 中文, en: 英文)
    
    Returns:
        WeatherData: 包含天气信息的对象
    """
    # 转换城市名称
    english_city = city_converter.to_english(city)
    
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise ValueError("缺少 OPENWEATHERMAP_API_KEY 环境变量")

    params = {
        "q": english_city,
        "appid": api_key,
        "units": units,
        "lang": lang
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            return WeatherData(
                description=data["weather"][0]["description"],
                temperature=data["main"]["temp"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                city=city  # 保留原始输入的城市名
            )
            
    except httpx.TimeoutException:
        raise Exception("请求超时，请稍后重试")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise Exception(f"未找到城市 '{city}' ({english_city}) 的天气信息")
        raise Exception(f"HTTP错误: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise Exception(f"数据解析错误：缺少必要字段 {str(e)}")
    except Exception as e:
        raise Exception(f"获取天气信息时发生错误：{str(e)}")

@server.tool()
async def get_weather_forecast(
    city: str,
    days: int = 5,
    units: str = "metric",
    lang: str = "zh_cn"
) -> dict:
    """
    获取指定城市的天气预报信息
    
    Args:
        city: 城市名称（支持中文或英文，如：苏州、suzhou）
        days: 预报天数（最多5天）
        units: 温度单位 (metric: 摄氏度, imperial: 华氏度)
        lang: 返回语言 (zh_cn: 中文, en: 英文)
    
    Returns:
        dict: 包含天气预报信息的字典
    """
    # 转换城市名称
    english_city = city_converter.to_english(city)
    
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise ValueError("缺少 OPENWEATHERMAP_API_KEY 环境变量")

    params = {
        "q": english_city,
        "appid": api_key,
        "units": units,
        "lang": lang,
        "cnt": min(days * 8, 40)
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.openweathermap.org/data/2.5/forecast",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # 处理预报数据，按天聚合
            forecasts = {}
            for item in data["list"]:
                date = item["dt_txt"].split()[0]
                if date not in forecasts:
                    forecasts[date] = {
                        "temp_min": float("inf"),
                        "temp_max": float("-inf"),
                        "descriptions": set(),
                        "humidity": [],
                        "wind_speed": []
                    }
                
                daily = forecasts[date]
                daily["temp_min"] = min(daily["temp_min"], item["main"]["temp"])
                daily["temp_max"] = max(daily["temp_max"], item["main"]["temp"])
                daily["descriptions"].add(item["weather"][0]["description"])
                daily["humidity"].append(item["main"]["humidity"])
                daily["wind_speed"].append(item["wind"]["speed"])

            # 转换为ForecastData对象列表
            result = []
            for date, daily in list(forecasts.items())[:days]:
                result.append(ForecastData(
                    date=date,
                    description="/".join(daily["descriptions"]),
                    temp_min=round(daily["temp_min"], 2),
                    temp_max=round(daily["temp_max"], 2),
                    humidity=round(sum(daily["humidity"]) / len(daily["humidity"])),
                    wind_speed=round(sum(daily["wind_speed"]) / len(daily["wind_speed"]), 2),
                    city=city
                ))
            
            # 修改返回格式为字典
            return {
                "forecasts": [
                    {
                        "date": forecast.date,
                        "description": forecast.description,
                        "temp_min": forecast.temp_min,
                        "temp_max": forecast.temp_max,
                        "humidity": forecast.humidity,
                        "wind_speed": forecast.wind_speed,
                        "city": forecast.city
                    } for forecast in result
                ]
            }
            
    except httpx.TimeoutException:
        raise Exception("请求超时，请稍后重试")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise Exception(f"未找到城市 '{city}' 的天气信息")
        raise Exception(f"HTTP错误: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise Exception(f"数据解析错误：缺少必要字段 {str(e)}")
    except Exception as e:
        raise Exception(f"获取天气预报信息时发生错误：{str(e)}")

# 运行服务器
if __name__ == "__main__":
    server.run()