# -*- coding: utf-8 -*-
"""
数据处理模块 - 负责数据加载和预处理
包含负荷数据生成和气象数据获取功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from .config import get_config, get_load_profile_pattern
from .performance import monitor_data_loading

@st.cache_data
@monitor_data_loading
def load_mine_load_profile(profile_name, annual_consumption_gwh):
    """
    根据用户选择的负荷曲线类型和年总用电量，生成一年8760个小时的用电负荷序列
    
    参数:
    - profile_name: str, 负荷类型 ('24小时连续生产型' 或 '白班为主型')
    - annual_consumption_gwh: float, 年总用电量 (GWh)
    
    返回:
    - pandas.Series: 包含8760个小时负荷值的时间序列 (kW)
    """
    try:
        # 从配置文件获取负荷模式
        try:
            daily_pattern = np.array(get_load_profile_pattern(profile_name))
        except KeyError:
            raise ValueError(f"不支持的负荷类型: {profile_name}")
        
        # 生成一年的负荷模式 (365天 × 24小时 = 8760小时)
        annual_pattern = np.tile(daily_pattern, 365)
        
        # 确保精确为8760小时 (处理闰年情况)
        annual_pattern = annual_pattern[:8760]
        
        # 计算缩放因子，使总用电量匹配用户输入
        # 单位转换: GWh -> kWh (1 GWh = 1,000,000 kWh)
        target_total_kwh = annual_consumption_gwh * 1_000_000
        current_total = np.sum(annual_pattern)
        scaling_factor = target_total_kwh / current_total
        
        # 应用缩放因子得到实际负荷值 (kW)
        actual_loads = annual_pattern * scaling_factor
        
        # 创建时间索引 (2023年1月1日0时开始的小时频率)
        start_date = datetime(2023, 1, 1)
        time_index = pd.date_range(
            start=start_date, 
            periods=8760, 
            freq='h'
        )
        
        # 创建并返回Pandas Series
        load_series = pd.Series(
            data=actual_loads,
            index=time_index,
            name=f'负荷_{profile_name}'
        )
        
        return load_series
        
    except Exception as e:
        st.error(f"负荷数据生成失败: {str(e)}")
        return None


@st.cache_data
@monitor_data_loading
def get_weather_data(latitude, longitude, year=None):
    """
    使用Open-Meteo API获取指定经纬度的历史气象数据

    参数:
    - latitude: float, 纬度
    - longitude: float, 经度
    - year: int, 分析年份，默认为最近的完整年份

    返回:
    - pandas.DataFrame: 包含小时级气象数据的DataFrame
    """
    try:
        # 确定分析年份
        if year is None:
            from datetime import datetime
            current_year = datetime.now().year
            # 如果当前年份还未结束，使用上一年
            if datetime.now().month < 12:
                year = current_year - 1
            else:
                year = current_year

        # 构造Open-Meteo API URL
        base_url = "https://archive-api.open-meteo.com/v1/archive"

        # API参数
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': f'{year}-01-01',
            'end_date': f'{year}-12-31',
            'hourly': [
                'temperature_2m',           # 2米高度温度 (°C)
                'windspeed_10m',           # 10米高度风速 (m/s)
                'shortwave_radiation',     # 全球水平辐射 GHI (W/m²)
                'direct_normal_irradiance', # 直接法向辐射 DNI (W/m²)
                'diffuse_radiation'        # 散射辐射 DHI (W/m²)
            ],
            'timezone': 'UTC'
        }
        
        # 发送API请求
        response = requests.get(base_url, params=params, timeout=30)
        
        # 检查请求是否成功
        if response.status_code != 200:
            raise Exception(f"API请求失败，状态码: {response.status_code}")
        
        # 解析JSON数据
        data = response.json()
        
        # 检查API返回是否包含错误
        if 'error' in data:
            raise Exception(f"API返回错误: {data['error']}")
        
        # 提取小时数据
        hourly_data = data['hourly']
        
        # 创建DataFrame
        weather_df = pd.DataFrame({
            'time': hourly_data['time'],
            'temperature_2m': hourly_data['temperature_2m'],
            'windspeed_10m': hourly_data['windspeed_10m'],
            'ghi': hourly_data['shortwave_radiation'],  # Global Horizontal Irradiance
            'dni': hourly_data['direct_normal_irradiance'],  # Direct Normal Irradiance
            'dhi': hourly_data['diffuse_radiation']  # Diffuse Horizontal Irradiance
        })
        
        # 转换时间列为DatetimeIndex
        weather_df['time'] = pd.to_datetime(weather_df['time'])
        weather_df.set_index('time', inplace=True)
        
        # 数据质量检查
        if len(weather_df) != 8760:
            st.warning(f"气象数据长度异常: {len(weather_df)} 小时 (期望: 8760小时)")
        
        # 检查缺失值
        missing_data = weather_df.isnull().sum()
        if missing_data.any():
            st.warning(f"气象数据存在缺失值，已自动填充")
            # 使用前向填充处理缺失值
            weather_df.fillna(method='ffill', inplace=True)
        
        return weather_df
        
    except requests.exceptions.Timeout:
        st.error("API请求超时，请检查网络连接或稍后重试")
        return None
    except requests.exceptions.ConnectionError:
        st.error("网络连接错误，请检查网络连接")
        return None
    except Exception as e:
        st.error(f"气象数据获取失败: {str(e)}")
        return None

def validate_data_quality(data, data_type="数据"):
    """
    验证数据质量
    
    参数:
    - data: pandas.DataFrame 或 pandas.Series, 要验证的数据
    - data_type: str, 数据类型描述
    
    返回:
    - bool: 数据质量是否合格
    """
    if data is None or data.empty:
        st.error(f"{data_type}为空或无效")
        return False
    
    # 检查数据长度
    if len(data) != 8760:
        st.warning(f"{data_type}长度异常: {len(data)} (期望: 8760)")
    
    # 检查缺失值
    if hasattr(data, 'isnull'):
        missing_count = data.isnull().sum()
        if isinstance(missing_count, pd.Series):
            total_missing = missing_count.sum()
        else:
            total_missing = missing_count
            
        if total_missing > 0:
            st.warning(f"{data_type}存在 {total_missing} 个缺失值")
    
    return True

def preprocess_data(data, fill_method='ffill'):
    """
    数据预处理
    
    参数:
    - data: pandas.DataFrame 或 pandas.Series, 要处理的数据
    - fill_method: str, 缺失值填充方法
    
    返回:
    - 处理后的数据
    """
    if data is None:
        return None
    
    # 填充缺失值
    if hasattr(data, 'fillna'):
        data = data.fillna(method=fill_method)
    
    # 确保数据为数值类型
    if hasattr(data, 'select_dtypes'):
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    return data
