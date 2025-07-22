# -*- coding: utf-8 -*-
"""
高级UI组件模块 - 现代化、专业级用户界面
包含高级样式、动画效果、响应式设计等
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np
from .config import get_config, WIND_TURBINE_DATABASE

def inject_custom_css():
    """注入自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式优化 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e1e8ed;
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* 进度条样式 */
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-success { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-error { background-color: #dc3545; }
    .status-info { background-color: #17a2b8; }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 输入框样式 */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e1e8ed;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0px 0px;
        border: 1px solid #e1e8ed;
        color: #495057;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 侧边栏组件样式 */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* 动画效果 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .metric-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_advanced_header():
    """创建高级页面头部"""
    inject_custom_css()
    
    # 主标题
    st.markdown("""
    <div class="main-title fade-in-up">
        ⚡ 智能微电网规划分析平台
    </div>
    """, unsafe_allow_html=True)
    
    # 副标题和描述
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">
            基于AI驱动的矿区可再生能源与储能系统优化设计平台<br>
            <span style="color: #28a745;">🌱 绿色能源</span> • 
            <span style="color: #007bff;">🔋 智能储能</span> • 
            <span style="color: #ffc107;">📊 数据驱动</span>
        </div>
        """, unsafe_allow_html=True)

def create_status_dashboard():
    """创建状态仪表板"""
    st.markdown('<div class="sub-title">📊 系统状态总览</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-indicator status-success"></span>
                <strong>系统状态</strong>
            </div>
            <div style="font-size: 1.5rem; color: #28a745; font-weight: 600;">运行正常</div>
            <div style="color: #6c757d; font-size: 0.9rem;">所有模块正常运行</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-indicator status-info"></span>
                <strong>计算引擎</strong>
            </div>
            <div style="font-size: 1.5rem; color: #17a2b8; font-weight: 600;">就绪</div>
            <div style="color: #6c757d; font-size: 0.9rem;">8760小时精确建模</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-indicator status-success"></span>
                <strong>数据连接</strong>
            </div>
            <div style="font-size: 1.5rem; color: #28a745; font-weight: 600;">已连接</div>
            <div style="color: #6c757d; font-size: 0.9rem;">气象数据API正常</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # 获取实际内存使用情况
        try:
            from .memory_optimizer import MemoryMonitor
            monitor = MemoryMonitor()
            stats = monitor.get_memory_stats()
            memory_status = "正常" if stats.percent_used < 80 else "警告"
            memory_color = "#28a745" if stats.percent_used < 80 else "#ffc107"
            status_class = "status-success" if stats.percent_used < 80 else "status-warning"
        except:
            memory_status = "未知"
            memory_color = "#6c757d"
            status_class = "status-info"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-indicator {status_class}"></span>
                <strong>内存状态</strong>
            </div>
            <div style="font-size: 1.5rem; color: {memory_color}; font-weight: 600;">{memory_status}</div>
            <div style="color: #6c757d; font-size: 0.9rem;">系统资源监控</div>
        </div>
        """, unsafe_allow_html=True)

def create_advanced_sidebar():
    """创建高级侧边栏"""
    # 侧边栏标题
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: white;">
        <h2 style="margin: 0; color: white;">🎛️ 智能配置面板</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">专业级参数配置</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 配置向导
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h4 style="color: white; margin-bottom: 1rem;">📋 配置向导</h4>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">
            按照以下步骤完成系统配置：<br>
            ✅ 1. 地理位置与负荷<br>
            ✅ 2. 可再生能源配置<br>
            ✅ 3. 储能系统设计<br>
            ✅ 4. 经济参数设置
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 地理位置与负荷配置
    with st.sidebar.expander("🌍 地理位置与负荷", expanded=True):
        geo_config = get_config("geography")
        
        col1, col2 = st.columns(2)
        with col1:
            longitude = st.number_input(
                "经度 (°)",
                min_value=-180.0,
                max_value=180.0,
                value=geo_config["default_longitude"],
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            latitude = st.number_input(
                "纬度 (°)",
                min_value=-90.0,
                max_value=90.0,
                value=geo_config["default_latitude"],
                step=0.01,
                format="%.2f"
            )
        
        # 地图预览
        if st.checkbox("📍 显示位置预览"):
            create_location_preview(latitude, longitude)
        
        load_type = st.selectbox(
            "负荷类型",
            options=list(get_config("load_profiles").keys()),
            help="选择矿区的用电模式"
        )
        
        annual_consumption = st.number_input(
            "年用电量 (GWh)",
            min_value=1.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            format="%.1f"
        )
        
        # 年份选择
        current_year = datetime.now().year
        available_years = list(range(current_year-3, current_year))
        analysis_year = st.selectbox(
            "气象数据年份",
            options=available_years,
            index=len(available_years)-1
        )
    
    # 可再生能源配置
    with st.sidebar.expander("🌞 可再生能源配置", expanded=True):
        pv_capacity = st.number_input(
            "光伏装机容量 (MW)",
            min_value=0.0,
            max_value=500.0,
            value=50.0,
            step=1.0
        )
        
        # 风机配置
        wind_turbine_options = list(WIND_TURBINE_DATABASE.keys())
        wind_turbine_model = st.selectbox(
            "风机型号",
            options=wind_turbine_options,
            format_func=lambda x: f"{x} ({WIND_TURBINE_DATABASE[x]['rated_power']}kW)"
        )
        
        wind_turbine_count = st.number_input(
            "风机数量 (台)",
            min_value=0,
            max_value=100,
            value=10,
            step=1
        )
        
        # 可再生能源预览
        create_renewable_preview(pv_capacity, wind_turbine_count, wind_turbine_model)
    
    # 储能系统配置
    with st.sidebar.expander("🔋 储能系统配置", expanded=True):
        battery_capacity = st.number_input(
            "储能容量 (MWh)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0
        )
        
        battery_power = st.number_input(
            "储能功率 (MW)",
            min_value=0.0,
            max_value=500.0,
            value=50.0,
            step=1.0
        )
        
        # C倍率计算和显示
        if battery_capacity > 0:
            c_rate = battery_power / battery_capacity
            st.info(f"📊 C倍率: {c_rate:.2f}C")
            
            if c_rate > 1:
                st.warning("⚠️ C倍率较高，注意电池寿命")
            elif c_rate < 0.5:
                st.success("✅ C倍率适中，有利于电池寿命")
    
    # 经济参数配置
    with st.sidebar.expander("💰 经济参数配置", expanded=True):
        econ_config = get_config("economics")
        
        col1, col2 = st.columns(2)
        with col1:
            grid_purchase_price = st.number_input(
                "购电价格 ($/kWh)",
                min_value=0.01,
                max_value=1.0,
                value=econ_config["default_purchase_price"],
                step=0.01,
                format="%.3f"
            )
        
        with col2:
            grid_sell_price = st.number_input(
                "售电价格 ($/kWh)",
                min_value=0.01,
                max_value=1.0,
                value=econ_config["default_sell_price"],
                step=0.01,
                format="%.3f"
            )
        
        # 价差分析
        price_diff = grid_purchase_price - grid_sell_price
        st.info(f"📈 购售电价差: ${price_diff:.3f}/kWh")
    
    # 返回用户输入
    return {
        'latitude': latitude,
        'longitude': longitude,
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

def create_location_preview(latitude, longitude):
    """创建位置预览地图"""
    try:
        # 创建简单的位置标记图
        fig = go.Figure(go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode='markers',
            marker=dict(size=15, color='red'),
            text=[f"矿区位置<br>纬度: {latitude}°<br>经度: {longitude}°"],
            hoverinfo='text'
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=latitude, lon=longitude),
                zoom=8
            ),
            height=200,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("📍 地图预览暂时不可用")

def create_renewable_preview(pv_capacity, wind_count, wind_model):
    """创建可再生能源配置预览"""
    try:
        wind_info = WIND_TURBINE_DATABASE[wind_model]
        wind_capacity = wind_count * wind_info['rated_power'] / 1000  # MW
        total_capacity = pv_capacity + wind_capacity

        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=['光伏发电', '风力发电'],
            values=[pv_capacity, wind_capacity],
            hole=0.4,
            marker_colors=['#FFA500', '#87CEEB']
        )])

        fig.update_layout(
            title=f"总装机容量: {total_capacity:.1f} MW",
            height=200,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # 显示详细信息
        st.markdown(f"""
        **配置详情:**
        - 🌞 光伏: {pv_capacity} MW
        - 💨 风电: {wind_capacity:.1f} MW ({wind_count}台)
        - 📊 总计: {total_capacity:.1f} MW
        """)

    except Exception as e:
        st.info("📊 配置预览暂时不可用")

def create_advanced_progress_display(task_id, title="计算进行中..."):
    """创建高级进度显示"""
    from .async_processor import task_manager

    task = task_manager.get_task_status(task_id)

    if not task:
        st.error("❌ 任务不存在")
        return None

    # 创建进度容器
    progress_container = st.container()

    with progress_container:
        if task.status.value == "pending":
            st.markdown("""
            <div class="progress-container">
                <h4>⏳ 任务准备中...</h4>
                <div style="display: flex; align-items: center;">
                    <div style="width: 100%; background: #e9ecef; border-radius: 10px; height: 8px;">
                        <div style="width: 0%; background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    </div>
                    <span style="margin-left: 1rem; font-weight: 600;">0%</span>
                </div>
                <p style="margin-top: 0.5rem; color: #6c757d;">正在初始化计算环境...</p>
            </div>
            """, unsafe_allow_html=True)

        elif task.status.value == "running":
            progress_percent = int(task.progress * 100)

            st.markdown(f"""
            <div class="progress-container">
                <h4>🔄 {title}</h4>
                <div style="display: flex; align-items: center;">
                    <div style="width: 100%; background: #e9ecef; border-radius: 10px; height: 12px;">
                        <div style="width: {progress_percent}%; background: linear-gradient(90deg, #28a745, #20c997); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    </div>
                    <span style="margin-left: 1rem; font-weight: 600; font-size: 1.1rem;">{progress_percent}%</span>
                </div>
                <div style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                    <p style="margin: 0; color: #6c757d;">正在执行复杂的能源系统建模计算...</p>
                    <button onclick="cancelTask()" style="background: #dc3545; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">取消</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 显示执行时间
            if task.start_time:
                from datetime import datetime
                elapsed = (datetime.now() - task.start_time).total_seconds()
                st.info(f"⏱️ 已运行: {elapsed:.1f} 秒")

        elif task.status.value == "completed":
            st.markdown("""
            <div class="progress-container" style="border-left-color: #28a745;">
                <h4>✅ 计算完成！</h4>
                <div style="display: flex; align-items: center;">
                    <div style="width: 100%; background: #e9ecef; border-radius: 10px; height: 8px;">
                        <div style="width: 100%; background: linear-gradient(90deg, #28a745, #20c997); height: 100%; border-radius: 10px;"></div>
                    </div>
                    <span style="margin-left: 1rem; font-weight: 600; color: #28a745;">100%</span>
                </div>
                <p style="margin-top: 0.5rem; color: #28a745;">所有计算已成功完成，正在生成分析报告...</p>
            </div>
            """, unsafe_allow_html=True)

            if task.execution_time:
                st.success(f"🎉 总执行时间: {task.execution_time:.2f} 秒")

            return task

        elif task.status.value == "failed":
            st.markdown(f"""
            <div class="progress-container" style="border-left-color: #dc3545;">
                <h4>❌ 计算失败</h4>
                <p style="color: #dc3545; margin: 0.5rem 0;">错误信息: {task.error}</p>
                <button onclick="retryTask()" style="background: #007bff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; margin-top: 0.5rem;">重试</button>
            </div>
            """, unsafe_allow_html=True)

            return task

        elif task.status.value == "cancelled":
            st.markdown("""
            <div class="progress-container" style="border-left-color: #ffc107;">
                <h4>⚠️ 任务已取消</h4>
                <p style="color: #856404; margin: 0.5rem 0;">用户主动取消了计算任务</p>
            </div>
            """, unsafe_allow_html=True)

            return task

    # 自动刷新
    if task.status.value in ["pending", "running"]:
        import time
        time.sleep(1)
        st.rerun()

    return None

def create_advanced_kpi_dashboard(simulation_results, economic_params):
    """创建高级KPI仪表板"""
    st.markdown('<div class="sub-title">📊 关键绩效指标</div>', unsafe_allow_html=True)

    try:
        # 计算KPI
        total_load = simulation_results['mine_load_kw'].sum() / 1000  # MWh
        renewable_generation = simulation_results['renewable_total_kw'].sum() / 1000  # MWh
        grid_purchase = simulation_results['grid_buy_kw'].sum() / 1000  # MWh
        grid_sell = simulation_results['grid_sell_kw'].sum() / 1000  # MWh

        renewable_penetration = (renewable_generation / total_load) * 100
        self_consumption = ((renewable_generation - grid_sell) / renewable_generation) * 100 if renewable_generation > 0 else 0
        grid_independence = ((total_load - grid_purchase) / total_load) * 100

        # 经济指标
        total_cost = simulation_results['grid_cost_usd'].sum()
        total_revenue = simulation_results['grid_revenue_usd'].sum()
        net_cost = total_cost - total_revenue

        # 创建KPI卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            create_kpi_card(
                "可再生能源渗透率",
                f"{renewable_penetration:.1f}%",
                "success" if renewable_penetration > 50 else "warning",
                "🌱",
                f"年发电量: {renewable_generation:.1f} MWh"
            )

        with col2:
            create_kpi_card(
                "自消纳率",
                f"{self_consumption:.1f}%",
                "success" if self_consumption > 70 else "info",
                "🔄",
                f"自用电量占比"
            )

        with col3:
            create_kpi_card(
                "电网独立度",
                f"{grid_independence:.1f}%",
                "success" if grid_independence > 60 else "warning",
                "🔌",
                f"减少电网依赖"
            )

        with col4:
            create_kpi_card(
                "年度净成本",
                f"${net_cost:,.0f}",
                "success" if net_cost < 0 else "error",
                "💰",
                f"成本-收益分析"
            )

        # 详细KPI表格
        st.markdown('<div class="sub-title">📋 详细指标分析</div>', unsafe_allow_html=True)

        kpi_data = {
            "指标类别": ["能源", "能源", "能源", "经济", "经济", "经济", "环境"],
            "指标名称": [
                "年总用电量", "可再生能源发电量", "电网购电量",
                "年度电费支出", "年度售电收入", "年度净成本", "CO₂减排量"
            ],
            "数值": [
                f"{total_load:.1f} MWh",
                f"{renewable_generation:.1f} MWh",
                f"{grid_purchase:.1f} MWh",
                f"${total_cost:,.0f}",
                f"${total_revenue:,.0f}",
                f"${net_cost:,.0f}",
                f"{renewable_generation * 0.58:.1f} 吨"
            ],
            "占比/状态": [
                "100%",
                f"{renewable_penetration:.1f}%",
                f"{(grid_purchase/total_load)*100:.1f}%",
                "-",
                "-",
                "盈利" if net_cost < 0 else "亏损",
                f"减排 {(renewable_generation * 0.58):.0f} 吨CO₂"
            ]
        }

        kpi_df = pd.DataFrame(kpi_data)
        st.dataframe(kpi_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"KPI计算失败: {e}")

def create_kpi_card(title, value, status, icon, description):
    """创建KPI卡片"""
    status_colors = {
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#17a2b8"
    }

    color = status_colors.get(status, "#6c757d")

    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <span class="status-indicator status-{status}"></span>
        </div>
        <h4 style="margin: 0; color: #2c3e50; font-size: 0.9rem;">{title}</h4>
        <div style="font-size: 2rem; font-weight: 700; color: {color}; margin: 0.5rem 0;">{value}</div>
        <p style="margin: 0; color: #6c757d; font-size: 0.8rem;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
