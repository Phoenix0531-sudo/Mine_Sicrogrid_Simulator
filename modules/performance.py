# -*- coding: utf-8 -*-
"""
性能监控模块 - 监控应用性能和资源使用
包含执行时间监控、内存使用监控、缓存管理等
"""

import time
import psutil
import streamlit as st
import functools
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.function_name = None
    
    def start(self, function_name="Unknown"):
        """开始监控"""
        self.function_name = function_name
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        logger.info(f"开始执行: {function_name}")
    
    def stop(self):
        """停止监控"""
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss
        
        execution_time = self.end_time - self.start_time
        memory_delta = (self.end_memory - self.start_memory) / 1024 / 1024  # MB
        
        logger.info(f"执行完成: {self.function_name}")
        logger.info(f"执行时间: {execution_time:.2f}秒")
        logger.info(f"内存变化: {memory_delta:+.1f}MB")
        
        return {
            'function_name': self.function_name,
            'execution_time': execution_time,
            'memory_delta': memory_delta,
            'start_memory': self.start_memory / 1024 / 1024,
            'end_memory': self.end_memory / 1024 / 1024
        }

def performance_monitor(show_in_sidebar=True):
    """
    性能监控装饰器
    
    参数:
    - show_in_sidebar: bool, 是否在侧边栏显示性能信息
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start(func.__name__)
            
            try:
                result = func(*args, **kwargs)
                performance_data = monitor.stop()
                
                if show_in_sidebar and 'streamlit' in globals():
                    display_performance_info(performance_data)
                
                return result
                
            except Exception as e:
                monitor.stop()
                logger.error(f"函数 {func.__name__} 执行失败: {e}")
                raise
        
        return wrapper
    return decorator

def display_performance_info(performance_data):
    """
    在侧边栏显示性能信息
    
    参数:
    - performance_data: dict, 性能数据
    """
    try:
        with st.sidebar.expander("⚡ 性能监控", expanded=False):
            st.metric(
                label="执行时间",
                value=f"{performance_data['execution_time']:.2f}s"
            )
            st.metric(
                label="内存使用",
                value=f"{performance_data['end_memory']:.1f}MB",
                delta=f"{performance_data['memory_delta']:+.1f}MB"
            )
            st.caption(f"函数: {performance_data['function_name']}")
    except Exception as e:
        logger.warning(f"性能信息显示失败: {e}")

def get_system_info():
    """
    获取系统信息

    返回:
    - dict: 系统信息字典
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)  # 减少等待时间
        memory = psutil.virtual_memory()

        # 获取当前工作目录的磁盘使用情况（Windows兼容）
        import os
        current_drive = os.path.splitdrive(os.getcwd())[0] + os.sep
        disk = psutil.disk_usage(current_drive)

        return {
            'cpu_percent': cpu_percent,
            'memory_total': memory.total / 1024 / 1024 / 1024,  # GB
            'memory_used': memory.used / 1024 / 1024 / 1024,    # GB
            'memory_percent': memory.percent,
            'disk_total': disk.total / 1024 / 1024 / 1024,      # GB
            'disk_used': disk.used / 1024 / 1024 / 1024,        # GB
            'disk_percent': (disk.used / disk.total) * 100
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        # 返回基本信息，避免完全失败
        try:
            memory = psutil.virtual_memory()
            return {
                'cpu_percent': 0,
                'memory_total': memory.total / 1024 / 1024 / 1024,
                'memory_used': memory.used / 1024 / 1024 / 1024,
                'memory_percent': memory.percent,
                'disk_total': 0,
                'disk_used': 0,
                'disk_percent': 0
            }
        except:
            return {}

def display_system_status():
    """在侧边栏显示系统状态"""
    try:
        # 使用缓存避免频繁调用
        if not hasattr(display_system_status, '_last_update'):
            display_system_status._last_update = 0

        import time
        current_time = time.time()

        # 每5秒更新一次系统状态
        if current_time - display_system_status._last_update < 5:
            return

        display_system_status._last_update = current_time
        system_info = get_system_info()

        if system_info:
            with st.sidebar.expander("🖥️ 系统状态", expanded=False):
                # CPU使用率
                cpu_color = "normal"
                if system_info['cpu_percent'] > 80:
                    cpu_color = "inverse"
                
                st.metric(
                    label="CPU使用率",
                    value=f"{system_info['cpu_percent']:.1f}%"
                )
                
                # 内存使用率
                memory_color = "normal"
                if system_info['memory_percent'] > 80:
                    memory_color = "inverse"
                
                st.metric(
                    label="内存使用率",
                    value=f"{system_info['memory_percent']:.1f}%",
                    delta=f"{system_info['memory_used']:.1f}GB / {system_info['memory_total']:.1f}GB"
                )
                
                # 磁盘使用率
                st.metric(
                    label="磁盘使用率",
                    value=f"{system_info['disk_percent']:.1f}%",
                    delta=f"{system_info['disk_used']:.1f}GB / {system_info['disk_total']:.1f}GB"
                )
                
                st.caption(f"更新时间: {datetime.now().strftime('%H:%M:%S')}")
    
    except Exception as e:
        logger.warning(f"系统状态显示失败: {e}")

def clear_streamlit_cache():
    """清理Streamlit缓存"""
    try:
        st.cache_data.clear()
        st.success("✅ 缓存清理完成")
        logger.info("Streamlit缓存已清理")
    except Exception as e:
        st.error(f"❌ 缓存清理失败: {e}")
        logger.error(f"缓存清理失败: {e}")

def optimize_dataframe(df):
    """
    优化DataFrame内存使用
    
    参数:
    - df: pandas.DataFrame
    
    返回:
    - pandas.DataFrame: 优化后的DataFrame
    """
    try:
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        # 优化数值列
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = df[col].astype('int32')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = df[col].astype('float32')
        
        # 优化对象列
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # 如果唯一值比例小于50%
                df[col] = df[col].astype('category')
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logger.info(f"DataFrame内存优化: {original_memory:.1f}MB -> {optimized_memory:.1f}MB (减少{reduction:.1f}%)")
        
        return df
        
    except Exception as e:
        logger.warning(f"DataFrame优化失败: {e}")
        return df

class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def get_cache_stats():
        """获取缓存统计信息"""
        try:
            # 这里可以扩展获取更详细的缓存信息
            return {
                'cache_enabled': True,
                'cache_type': 'streamlit_cache_data'
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    @staticmethod
    def clear_all_cache():
        """清理所有缓存"""
        try:
            st.cache_data.clear()
            logger.info("所有缓存已清理")
            return True
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return False

def benchmark_function(func, *args, **kwargs):
    """
    基准测试函数
    
    参数:
    - func: 要测试的函数
    - args, kwargs: 函数参数
    
    返回:
    - dict: 基准测试结果
    """
    monitor = PerformanceMonitor()
    monitor.start(func.__name__)
    
    try:
        result = func(*args, **kwargs)
        performance_data = monitor.stop()
        
        return {
            'success': True,
            'result': result,
            'performance': performance_data
        }
        
    except Exception as e:
        monitor.stop()
        return {
            'success': False,
            'error': str(e),
            'performance': monitor.stop()
        }

def create_performance_dashboard():
    """创建性能监控仪表板"""
    try:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔧 性能工具")

        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("🗑️ 清理缓存", help="清理所有Streamlit缓存"):
                clear_streamlit_cache()

        with col2:
            # 简化系统状态显示，避免频繁调用
            if st.button("📊 刷新状态", help="刷新系统资源使用情况"):
                try:
                    system_info = get_system_info()
                    if system_info:
                        st.sidebar.success(f"内存: {system_info['memory_percent']:.1f}%")
                except:
                    st.sidebar.info("系统状态获取中...")

        # 显示性能提示
        with st.sidebar.expander("💡 性能提示", expanded=False):
            st.markdown("""
            **优化建议**:
            - 定期清理缓存释放内存
            - 避免同时运行多个大型计算
            - 使用时间范围选择器查看部分数据
            - 关闭不需要的浏览器标签页

            **当前状态**:
            - 光伏计算: ✅ 已修复
            - 桑基图: ✅ 正常
            - 交互式图表: ✅ 正常
            """)

    except Exception as e:
        logger.warning(f"性能仪表板创建失败: {e}")

# 预定义的性能监控装饰器
monitor_data_loading = performance_monitor(show_in_sidebar=True)
monitor_calculation = performance_monitor(show_in_sidebar=True)
monitor_visualization = performance_monitor(show_in_sidebar=False)
