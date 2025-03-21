'''
Author: Mr.Car
Date: 2025-03-21 14:28:32
'''
import pytest
from fastmcp import FastMCP
from weather_server.server import get_weather, get_weather_forecast, CityNameConverter

@pytest.mark.asyncio
async def test_mcp_weather_call():
    """测试 MCP 天气服务调用"""
    # 测试实时天气工具调用
    result = await get_weather("suzhou")
    assert result is not None
    assert hasattr(result, 'description')
    assert hasattr(result, 'temperature')
    assert hasattr(result, 'humidity')
    assert hasattr(result, 'wind_speed')
    assert hasattr(result, 'city')
    
    # 测试天气预报工具调用
    forecast = await get_weather_forecast("suzhou", days=1)
    assert forecast is not None
    assert 'forecasts' in forecast
    assert len(forecast['forecasts']) > 0
    assert 'date' in forecast['forecasts'][0]
    assert 'description' in forecast['forecasts'][0]

@pytest.mark.asyncio
async def test_mcp_chinese_city_name():
    """测试中文城市名称处理"""
    # 测试中文城市名
    result = await get_weather("苏州")
    assert result is not None
    assert result.city == "苏州"
    
    # 测试天气预报中的中文城市名
    forecast = await get_weather_forecast("苏州", days=1)
    assert forecast is not None
    assert forecast['forecasts'][0]['city'] == "苏州" 