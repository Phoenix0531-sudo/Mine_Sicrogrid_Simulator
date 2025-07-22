# -*- coding: utf-8 -*-
"""
矿区可再生能源与微电网规划模拟器
专业的微电网规划分析工具 - 主应用入口
"""

import streamlit as st

# 导入模块化功能
from modules.ui_components import create_sidebar, create_main_header, create_default_info
from modules.validation import validate_inputs
from modules.data_handler import load_mine_load_profile, get_weather_data
from modules.simulation_engine import calculate_solar_power, calculate_wind_power, run_simulation
from modules.results_analyzer import display_results

# 导入新的优化模块
from modules.async_processor import task_manager, create_progress_ui, async_computation
from modules.error_handler import with_error_handling, create_error_recovery_ui, RetryConfig
from modules.memory_optimizer import create_memory_monitor_ui, optimize_for_memory, MemoryMonitor

# 导入高级UI模块
from modules.advanced_ui import (
    create_advanced_header, create_status_dashboard, create_advanced_sidebar,
    create_advanced_progress_display, create_advanced_kpi_dashboard
)
from modules.advanced_visualization import (
    create_3d_energy_flow_chart, create_animated_daily_profile,
    create_heatmap_analysis, create_radar_chart_comparison, create_waterfall_chart
)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="智能微电网规划分析平台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 主应用逻辑 ====================

def main():
    """主应用函数 - 高级UI版本"""

    # 1. 创建高级页面头部
    create_advanced_header()

    # 2. 创建状态仪表板
    create_status_dashboard()

    # 3. 创建高级侧边栏并获取用户输入
    user_inputs = create_advanced_sidebar()

    # 4. 添加传统的监控UI（在侧边栏底部）
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 系统监控")
    create_memory_monitor_ui()
    create_error_recovery_ui()
    
    # 3. 验证用户输入
    input_warnings, input_errors = validate_inputs(user_inputs)
    
    # 4. 显示输入验证结果
    if input_warnings:
        st.sidebar.markdown("### ⚠️ 输入验证警告")
        for warning in input_warnings:
            st.sidebar.warning(warning)
        st.sidebar.markdown("---")

    if input_errors:
        st.sidebar.markdown("### ❌ 输入验证错误")
        for error in input_errors:
            st.sidebar.error(error)
        st.sidebar.markdown("---")

    # 5. 主操作按钮
    run_button_disabled = len(input_warnings) > 0 or len(input_errors) > 0
    
    if st.sidebar.button(
        "🚀 运行模拟分析",
        type="primary",
        use_container_width=True,
        help="点击开始运行微电网规划模拟分析" if not run_button_disabled else "请先解决上述输入问题",
        disabled=run_button_disabled
    ):
        # 6. 执行模拟分析流程
        run_simulation_workflow(user_inputs)
    
    else:
        # 7. 显示默认信息
        create_default_info()

@with_error_handling(
    retry_config=RetryConfig(max_attempts=2, delay=1.0),
    show_user_message=True
)
@optimize_for_memory
def run_simulation_workflow(user_inputs):
    """执行模拟分析工作流程 - 带错误处理和内存优化"""

    # 内存监控
    memory_monitor = MemoryMonitor()
    initial_memory = memory_monitor.get_memory_stats()

    # 第一步：验证用户输入
    st.subheader("🔍 输入验证")
    validation_warnings, validation_errors = validate_inputs(user_inputs)
    
    # 显示警告信息
    if validation_warnings:
        st.markdown("### ⚠️ 输入验证警告")
        for warning in validation_warnings:
            st.warning(warning)
        st.markdown("---")
    
    # 显示错误信息并终止执行
    if validation_errors:
        st.markdown("### ❌ 输入验证错误")
        for error in validation_errors:
            st.error(error)
        st.error("🚫 检测到致命错误，无法继续执行模拟计算。请修正上述错误后重试。")
        st.stop()
    
    # 显示验证状态
    if validation_warnings and not validation_errors:
        st.info("⚠️ 检测到输入警告，但不影响计算。将继续执行模拟分析。")
    elif not validation_warnings and not validation_errors:
        st.success("✅ 输入验证通过，所有参数设置合理。")
    
    st.markdown("---")
    
    # 检查是否有正在运行的任务
    if 'current_task_id' in st.session_state:
        task_result = create_advanced_progress_display(st.session_state.current_task_id, "智能微电网规划计算")

        if task_result and task_result.status.value in ['completed', 'failed', 'cancelled']:
            # 任务完成，清理状态
            del st.session_state.current_task_id

            if task_result.status.value == 'completed':
                # 显示高级结果分析
                display_advanced_results(task_result.result['simulation_results'], task_result.result['economic_params'])
                return
            else:
                st.error("模拟计算失败，请重试")
                return
        else:
            # 任务仍在进行中
            return

    # 启动异步模拟
    st.info("🚀 启动异步模拟计算...")
    task_id = start_async_simulation(user_inputs)
    st.session_state.current_task_id = task_id
    st.rerun()

@async_computation
def start_async_simulation(user_inputs):
    """异步模拟计算函数"""

    # 使用内存限制上下文和进度跟踪
    from modules.memory_optimizer import memory_limit
    from modules.async_processor import ProgressTracker
    import threading

    # 获取当前任务ID（从线程名称中提取）
    task_id = threading.current_thread().name.split('_')[-1] if '_' in threading.current_thread().name else "unknown"
    tracker = ProgressTracker(task_id)

    with memory_limit(500):  # 限制500MB内存使用

        # 准备经济参数
        economic_params = {
            'grid_purchase_price': user_inputs['grid_purchase_price'],
            'grid_sell_price': user_inputs['grid_sell_price']
        }

        # 第二步：生成负荷数据
        tracker.update_progress(1, 6, "生成负荷数据...")
        load_data = load_mine_load_profile(
            user_inputs['load_type'],
            user_inputs['annual_consumption']
        )

        if load_data is None:
            raise ValueError("负荷数据生成失败")
        
        # 第三步：获取气象数据
        tracker.update_progress(2, 6, "获取气象数据...")
        weather_data = get_weather_data(
            user_inputs['latitude'],
            user_inputs['longitude'],
            user_inputs['analysis_year']
        )

        if weather_data is None:
            raise ConnectionError("气象数据获取失败")

        # 第四步：计算光伏发电
        tracker.update_progress(3, 6, "计算光伏发电...")
        solar_power = calculate_solar_power(
            weather_data,
            user_inputs['pv_capacity'],
            user_inputs['latitude'],
            user_inputs['longitude']
        )

        if solar_power is None:
            raise ValueError("光伏发电计算失败")

        # 第五步：计算风力发电
        tracker.update_progress(4, 6, "计算风力发电...")
        wind_power = calculate_wind_power(
            weather_data,
            user_inputs['wind_turbine_model'],
            user_inputs['wind_turbine_count']
        )

        if wind_power is None:
            raise ValueError("风力发电计算失败")

        # 第六步：进行调度模拟
        tracker.update_progress(5, 6, "进行微电网调度模拟...")
        simulation_results = run_simulation(
            load_data,
            solar_power,
            wind_power,
            user_inputs['battery_capacity'],
            user_inputs['battery_power'],
            grid_purchase_price=user_inputs['grid_purchase_price'],
            grid_sell_price=user_inputs['grid_sell_price']
        )

        if simulation_results is None:
            raise ValueError("微电网调度模拟失败")

        # 完成计算
        tracker.update_progress(6, 6, "计算完成！")

        # 返回结果
        return {
            'simulation_results': simulation_results,
            'economic_params': economic_params
        }

def display_advanced_results(simulation_results, economic_params):
    """显示高级结果分析"""
    st.markdown('<div class="sub-title">🎉 计算完成 - 智能分析结果</div>', unsafe_allow_html=True)

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 KPI仪表板", "📈 高级图表", "🌐 3D分析", "🔥 热力图", "💧 能量流"
    ])

    with tab1:
        # KPI仪表板
        create_advanced_kpi_dashboard(simulation_results, economic_params)

    with tab2:
        # 雷达图和动画图表
        st.markdown("### 📊 系统性能雷达图")
        radar_fig = create_radar_chart_comparison(simulation_results)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)

        st.markdown("### 📅 动画日负荷曲线")
        animated_fig = create_animated_daily_profile(simulation_results)
        if animated_fig:
            st.plotly_chart(animated_fig, use_container_width=True)

    with tab3:
        # 3D分析
        st.markdown("### 🌐 3D能量流动轨迹")
        st.info("💡 提示：可以拖拽旋转3D图表，滚轮缩放，双击重置视角")

        flow_3d_fig = create_3d_energy_flow_chart(simulation_results)
        if flow_3d_fig:
            st.plotly_chart(flow_3d_fig, use_container_width=True)

    with tab4:
        # 热力图分析
        st.markdown("### 🔥 年度运行热力图")
        st.info("💡 提示：热力图显示全年8760小时的运行模式，颜色越深表示数值越大")

        heatmap_fig = create_heatmap_analysis(simulation_results)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)

    with tab5:
        # 瀑布图
        st.markdown("### 💧 年度能量平衡瀑布图")
        st.info("💡 提示：瀑布图显示能量的来源和去向，绿色表示能量输入，红色表示能量输出")

        waterfall_fig = create_waterfall_chart(simulation_results)
        if waterfall_fig:
            st.plotly_chart(waterfall_fig, use_container_width=True)

    # 传统详细结果（可折叠）
    with st.expander("📋 查看详细数据表格", expanded=False):
        display_results(simulation_results, economic_params)

# 运行主应用
if __name__ == "__main__":
    # 检查是否在Streamlit环境中运行
    try:
        # 尝试获取Streamlit的运行时上下文
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()

        if ctx is None:
            # 不在Streamlit环境中，显示提示信息
            print("=" * 60)
            print("🚀 智能微电网规划分析平台")
            print("=" * 60)
            print()
            print("请使用以下命令启动应用:")
            print("streamlit run app.py")
            print()
            print("或者在浏览器中访问:")
            print("http://localhost:8501")
            print()
            print("=" * 60)
        else:
            # 在Streamlit环境中，正常运行
            main()

    except ImportError:
        # Streamlit未安装或版本不兼容
        print("错误: 请确保已安装Streamlit")
        print("安装命令: pip install streamlit")
    except Exception as e:
        # 其他错误，仍然尝试运行主应用
        print(f"警告: {e}")
        main()
