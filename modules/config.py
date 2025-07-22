# -*- coding: utf-8 -*-
"""
配置管理模块 - 集中管理所有配置参数
包含默认参数、风机数据库、系统配置等
"""

import pandas as pd
import numpy as np

# ==================== 系统默认配置 ====================

DEFAULT_CONFIG = {
    # 地理位置默认值
    "geography": {
        "default_latitude": 39.90,
        "default_longitude": 116.40,
        "timezone": "UTC"
    },
    
    # 负荷模式配置
    "load_profiles": {
        "24小时连续生产型": {
            "pattern": [0.85, 0.82, 0.80, 0.78, 0.76, 0.78,  # 0-5时
                       0.85, 0.92, 0.98, 1.00, 1.00, 1.00,  # 6-11时
                       0.98, 0.95, 0.98, 1.00, 1.00, 0.98,  # 12-17时
                       0.95, 0.92, 0.90, 0.88, 0.87, 0.86], # 18-23时
            "description": "连续生产型：全天相对稳定，夜间略低"
        },
        "白班为主型": {
            "pattern": [0.45, 0.40, 0.35, 0.32, 0.30, 0.35,  # 0-5时
                       0.50, 0.70, 0.85, 0.95, 1.00, 1.00,  # 6-11时
                       0.98, 0.95, 0.98, 1.00, 0.95, 0.85,  # 12-17时
                       0.70, 0.60, 0.55, 0.52, 0.48, 0.46], # 18-23时
            "description": "白班为主型：明显的昼夜差异"
        }
    },
    
    # 经济参数默认值
    "economics": {
        "default_purchase_price": 0.15,  # $/kWh
        "default_sell_price": 0.05,     # $/kWh
        "carbon_emission_factor": 0.58,  # kg CO2/kWh
        "discount_rate": 0.08,           # 8%
        "project_lifetime": 25           # 年
    },
    
    # 电池系统配置
    "battery": {
        "round_trip_efficiency": 0.85,  # 往返效率
        "depth_of_discharge": 0.9,      # 放电深度
        "calendar_life": 15,            # 日历寿命(年)
        "cycle_life": 6000,             # 循环寿命
        "initial_soc": 0.5              # 初始SOC
    },
    
    # 光伏系统配置
    "solar": {
        "preferred_module_keywords": ["Canadian_Solar", "300"],  # 优先选择的组件关键词
        "preferred_inverter_keywords": ["ABB"],                  # 优先选择的逆变器关键词
        "surface_tilt": 30,             # 倾斜角度
        "surface_azimuth": 180,         # 朝南
        "modules_per_string": 20,       # 每串组件数
        "system_losses": 0.14,          # 系统损失14%
        "default_module_power": 300,    # 默认组件功率 (W)
        "fallback_module_params": {     # 备用组件参数
            "A_c": 1.94,
            "N_s": 60,
            "I_sc_ref": 9.5,
            "V_oc_ref": 37.8,
            "I_mp_ref": 8.9,
            "V_mp_ref": 30.5,
            "alpha_sc": 0.0048,
            "beta_oc": -0.35,
            "gamma_r": -0.45,
            "STC": 300
        },
        "fallback_inverter_params": {   # 备用逆变器参数
            "Paco": 250000,
            "Pdco": 259589,
            "Vdco": 310,
            "Pso": 17.92,
            "C0": -0.000002,
            "C1": -0.000047,
            "C2": -0.001861,
            "C3": 0.000721,
            "Pnt": 0.07
        }
    },
    
    # API配置
    "api": {
        "weather_api_timeout": 30,      # 秒
        "weather_api_retries": 3,       # 重试次数
        "cache_ttl": 3600              # 缓存时间(秒)
    },
    
    # 验证阈值
    "validation": {
        "max_annual_consumption": 1000,  # GWh
        "min_annual_consumption": 1,     # GWh
        "max_pv_capacity": 500,         # MW
        "max_wind_turbines": 100,       # 台
        "max_battery_capacity": 1000,   # MWh
        "max_battery_power": 500,       # MW
        "max_purchase_price": 1.0,      # $/kWh
        "max_sell_price": 0.5,          # $/kWh
        "min_purchase_price": 0.01,     # $/kWh
        "min_sell_price": 0.001,        # $/kWh
        "max_c_rate": 2.0,              # C倍率上限
        "min_c_rate": 0.1               # C倍率下限
    }
}

# ==================== 风机数据库 ====================

WIND_TURBINE_DATABASE = {
    'Vestas V112 3300': {
        'turbine_type': 'V112/3300',
        'hub_height': 119,
        'rated_power': 3300,  # kW
        'cut_in_speed': 3,    # m/s
        'rated_speed': 12,    # m/s
        'cut_out_speed': 25,  # m/s
        'rotor_diameter': 112, # m
        'manufacturer': 'Vestas',
        'description': '3.3MW海上风机，适合中高风速地区'
    },
    'Enercon E126 7500': {
        'turbine_type': 'E126/7500',
        'hub_height': 135,
        'rated_power': 7500,  # kW
        'cut_in_speed': 2.5,  # m/s
        'rated_speed': 13,    # m/s
        'cut_out_speed': 28,  # m/s
        'rotor_diameter': 126, # m
        'manufacturer': 'Enercon',
        'description': '7.5MW大型风机，适合低风速地区'
    },
    'Goldwind GW121 2500': {
        'turbine_type': 'GW121/2500',
        'hub_height': 120,
        'rated_power': 2500,  # kW
        'cut_in_speed': 3,    # m/s
        'rated_speed': 10.5,  # m/s
        'cut_out_speed': 25,  # m/s
        'rotor_diameter': 121, # m
        'manufacturer': 'Goldwind',
        'description': '2.5MW陆上风机，性价比高'
    },
    'Siemens SWT 3000': {
        'turbine_type': 'SWT-3.0-113',
        'hub_height': 120,
        'rated_power': 3000,  # kW
        'cut_in_speed': 3,    # m/s
        'rated_speed': 12,    # m/s
        'cut_out_speed': 25,  # m/s
        'rotor_diameter': 113, # m
        'manufacturer': 'Siemens',
        'description': '3.0MW通用型风机，技术成熟'
    }
}

# ==================== 颜色主题配置 ====================

COLOR_THEMES = {
    "default": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e", 
        "success": "#2ca02c",
        "warning": "#d62728",
        "info": "#17becf",
        "light": "#bcbd22",
        "dark": "#8c564b"
    },
    "energy": {
        "solar": "#FFA500",      # 橙色 - 太阳能
        "wind": "#87CEEB",       # 天蓝色 - 风能
        "grid": "#FF6B6B",       # 红色 - 电网
        "load": "#4ECDC4",       # 青色 - 负荷
        "battery": "#45B7D1",    # 蓝色 - 电池
        "sell": "#96CEB4",       # 绿色 - 售电
        "discharge": "#9B59B6"   # 紫色 - 放电
    }
}

# ==================== 单位转换配置 ====================

UNIT_CONVERSIONS = {
    # 功率单位
    "power": {
        ("kW", "MW"): 0.001,
        ("MW", "kW"): 1000,
        ("kW", "W"): 1000,
        ("W", "kW"): 0.001,
        ("MW", "GW"): 0.001,
        ("GW", "MW"): 1000
    },
    # 能量单位
    "energy": {
        ("kWh", "MWh"): 0.001,
        ("MWh", "kWh"): 1000,
        ("MWh", "GWh"): 0.001,
        ("GWh", "MWh"): 1000,
        ("kWh", "GWh"): 0.000001,
        ("GWh", "kWh"): 1000000
    }
}

# ==================== 配置访问函数 ====================

def get_config(section=None, key=None):
    """
    获取配置参数
    
    参数:
    - section: str, 配置节名称
    - key: str, 配置键名称
    
    返回:
    - 配置值或整个配置字典
    """
    if section is None:
        return DEFAULT_CONFIG
    
    if section not in DEFAULT_CONFIG:
        raise KeyError(f"配置节 '{section}' 不存在")
    
    if key is None:
        return DEFAULT_CONFIG[section]
    
    if key not in DEFAULT_CONFIG[section]:
        raise KeyError(f"配置键 '{key}' 在节 '{section}' 中不存在")
    
    return DEFAULT_CONFIG[section][key]

def get_wind_turbine_info(turbine_model):
    """
    获取风机信息
    
    参数:
    - turbine_model: str, 风机型号
    
    返回:
    - dict: 风机参数字典
    """
    if turbine_model not in WIND_TURBINE_DATABASE:
        raise KeyError(f"风机型号 '{turbine_model}' 不存在")
    
    return WIND_TURBINE_DATABASE[turbine_model]

def get_color_theme(theme_name="energy"):
    """
    获取颜色主题
    
    参数:
    - theme_name: str, 主题名称
    
    返回:
    - dict: 颜色配置字典
    """
    if theme_name not in COLOR_THEMES:
        theme_name = "default"
    
    return COLOR_THEMES[theme_name]

def get_load_profile_pattern(profile_name):
    """
    获取负荷模式
    
    参数:
    - profile_name: str, 负荷模式名称
    
    返回:
    - list: 24小时负荷模式数组
    """
    load_profiles = get_config("load_profiles")
    
    if profile_name not in load_profiles:
        raise KeyError(f"负荷模式 '{profile_name}' 不存在")
    
    return load_profiles[profile_name]["pattern"]

def validate_config():
    """
    验证配置文件的完整性
    
    返回:
    - bool: 验证是否通过
    """
    required_sections = [
        "geography", "load_profiles", "economics", 
        "battery", "solar", "api", "validation"
    ]
    
    for section in required_sections:
        if section not in DEFAULT_CONFIG:
            print(f"缺少配置节: {section}")
            return False
    
    # 验证负荷模式
    for profile_name, profile_data in DEFAULT_CONFIG["load_profiles"].items():
        if len(profile_data["pattern"]) != 24:
            print(f"负荷模式 '{profile_name}' 的模式数组长度不是24")
            return False
    
    # 验证风机数据库
    for turbine_name, turbine_data in WIND_TURBINE_DATABASE.items():
        required_keys = ['turbine_type', 'hub_height', 'rated_power']
        for key in required_keys:
            if key not in turbine_data:
                print(f"风机 '{turbine_name}' 缺少参数: {key}")
                return False
    
    return True
