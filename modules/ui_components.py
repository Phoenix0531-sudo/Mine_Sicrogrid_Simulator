# -*- coding: utf-8 -*-
"""
UI组件模块 - 负责创建用户界面组件
包含侧边栏创建和用户输入收集功能
"""

import streamlit as st
from .config import get_config, WIND_TURBINE_DATABASE
from .performance import create_performance_dashboard

def create_sidebar():
    """
    创建整个侧边栏界面，包含所有用户输入控件
    
    返回:
    - dict: 包含所有用户输入值的字典
    """
    # 侧边栏配置
    st.sidebar.title("📊 规划参数输入")
    st.sidebar.markdown("---")

    # 组1: 地理与负荷
    st.sidebar.subheader("🌍 1. 地理与负荷")

    # 地理位置
    # 从配置获取默认值
    geo_config = get_config("geography")

    longitude = st.sidebar.number_input(
        "矿区中心经度",
        min_value=-180.0,
        max_value=180.0,
        value=geo_config["default_longitude"],
        step=0.01,
        format="%.2f",
        help="请输入矿区中心位置的经度坐标"
    )

    latitude = st.sidebar.number_input(
        "矿区中心纬度",
        min_value=-90.0,
        max_value=90.0,
        value=geo_config["default_latitude"],
        step=0.01,
        format="%.2f",
        help="请输入矿区中心位置的纬度坐标"
    )

    # 矿区用电
    load_type = st.sidebar.selectbox(
        "选择矿区用电模式",
        options=['24小时连续生产型', '白班为主型'],
        index=0,
        help="选择矿区的主要用电模式，影响负荷曲线特征"
    )

    annual_consumption = st.sidebar.number_input(
        "年总用电量 (GWh)",
        min_value=1.0,
        max_value=1000.0,
        value=100.0,
        step=1.0,
        format="%.1f",
        help="矿区年度总用电量"
    )

    # 添加年份选择
    from datetime import datetime
    current_year = datetime.now().year
    available_years = list(range(current_year-3, current_year))  # 最近3年的完整数据

    analysis_year = st.sidebar.selectbox(
        "选择气象数据年份",
        options=available_years,
        index=len(available_years)-1,  # 默认选择最近年份
        help="选择用于分析的气象数据年份"
    )

    st.sidebar.markdown("---")

    # 组2: 发电设备配置
    st.sidebar.subheader("🔆 2. 发电设备配置")

    # 光伏系统
    pv_capacity = st.sidebar.slider(
        "光伏装机容量 (MWp)",
        min_value=0,
        max_value=200,
        value=50,
        step=5,
        help="光伏发电系统的装机容量"
    )

    # 风电系统
    # 从配置获取风机选项
    wind_turbine_options = list(WIND_TURBINE_DATABASE.keys())
    wind_turbine_model = st.sidebar.selectbox(
        "选择风机型号",
        options=wind_turbine_options,
        index=0,
        help="选择适合当地风况的风机型号",
        format_func=lambda x: f"{x} ({WIND_TURBINE_DATABASE[x]['rated_power']}kW)"
    )

    wind_turbine_count = st.sidebar.slider(
        "风机安装数量",
        min_value=0,
        max_value=50,
        value=10,
        step=1,
        help="计划安装的风机台数"
    )

    st.sidebar.markdown("---")

    # 组3: 储能系统配置
    st.sidebar.subheader("🔋 3. 储能系统配置")

    # 电池储能
    battery_capacity = st.sidebar.slider(
        "电池储能容量 (MWh)",
        min_value=0,
        max_value=200,
        value=50,
        step=5,
        help="电池储能系统的总容量"
    )

    battery_power = st.sidebar.slider(
        "电池最大充/放电功率 (MW)",
        min_value=0,
        max_value=100,
        value=25,
        step=5,
        help="电池系统的最大充电和放电功率"
    )

    st.sidebar.markdown("---")

    # 组4: 经济性参数
    st.sidebar.subheader("💰 4. 经济性参数")

    # 电价
    # 从配置获取经济参数默认值
    econ_config = get_config("economics")

    grid_purchase_price = st.sidebar.number_input(
        "电网购电电价 ($/kWh)",
        min_value=0.01,
        max_value=1.0,
        value=econ_config["default_purchase_price"],
        step=0.01,
        format="%.3f",
        help="从电网购买电力的价格"
    )

    grid_sell_price = st.sidebar.number_input(
        "上网卖电电价 ($/kWh)",
        min_value=0.01,
        max_value=1.0,
        value=econ_config["default_sell_price"],
        step=0.01,
        format="%.3f",
        help="向电网出售电力的价格"
    )

    st.sidebar.markdown("---")

    # 添加性能监控仪表板
    create_performance_dashboard()

    # 收集所有用户输入到字典中
    user_inputs = {
        'longitude': longitude,
        'latitude': latitude,
        'annual_consumption': annual_consumption,
        'analysis_year': analysis_year,
        'pv_capacity': pv_capacity,
        'wind_turbine_count': wind_turbine_count,
        'battery_capacity': battery_capacity,
        'battery_power': battery_power,
        'grid_purchase_price': grid_purchase_price,
        'grid_sell_price': grid_sell_price,
        'load_type': load_type,
        'wind_turbine_model': wind_turbine_model
    }

    return user_inputs

def create_main_header():
    """
    创建主页面标题和介绍
    """
    st.title("⚡ 矿区可再生能源与微电网规划模拟器")
    st.markdown("""
    ---
    **欢迎使用矿区可再生能源与微电网规划模拟器！**

    本工具专为矿区设计，帮助您优化可再生能源配置，实现经济高效的微电网规划。
    通过输入地理位置、负荷特性、设备参数和经济指标，系统将为您提供最佳的能源配置方案，
    包括光伏、风电和储能系统的容量配置建议，以及详细的经济性分析。

    请在左侧侧边栏中输入相关参数，然后点击'运行模拟分析'开始计算。
    """)

def create_default_info():
    """
    创建默认显示信息（当用户未点击分析按钮时）
    """
    st.info("👈 请在左侧侧边栏中输入规划参数，然后点击'运行模拟分析'按钮开始计算。")
    
    # 显示功能特色
    st.subheader("🎯 系统功能特色")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌞 光伏发电模拟**
        - 基于地理位置的太阳辐射计算
        - 考虑天气变化的发电量预测
        - 光伏组件效率分析
        """)
    
    with col2:
        st.markdown("""
        **💨 风电发电模拟**
        - 多种主流风机型号支持
        - 风速-功率曲线建模
        - 风资源评估分析
        """)
    
    with col3:
        st.markdown("""
        **⚡ 储能优化配置**
        - 电池充放电策略优化
        - 峰谷电价套利分析
        - 系统稳定性保障
        """)

def create_footer():
    """
    创建页脚信息
    """
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666666;'>"
        "矿区可再生能源与微电网规划模拟器 | "
        "Powered by Streamlit | "
        "© 2024 版权所有"
        "</div>",
        unsafe_allow_html=True
    )
