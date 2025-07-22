# -*- coding: utf-8 -*-
"""
内存优化策略模块 - 解决大数据集处理问题
包含数据分块、内存监控、垃圾回收、数据压缩等功能
"""

import gc
import psutil
import pandas as pd
import numpy as np
import pickle
import gzip
import tempfile
import os
from typing import Any, Iterator, List, Optional, Union, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import streamlit as st
import logging

logger = logging.getLogger(__name__)

@dataclass
class MemoryStats:
    """内存统计信息"""
    total_mb: float
    used_mb: float
    available_mb: float
    percent_used: float
    process_mb: float

class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, warning_threshold: float = 80.0, critical_threshold: float = 90.0):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.initial_memory = self.get_memory_stats()
    
    def get_memory_stats(self) -> MemoryStats:
        """获取当前内存统计"""
        try:
            # 系统内存
            memory = psutil.virtual_memory()
            
            # 当前进程内存
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return MemoryStats(
                total_mb=memory.total / 1024 / 1024,
                used_mb=memory.used / 1024 / 1024,
                available_mb=memory.available / 1024 / 1024,
                percent_used=memory.percent,
                process_mb=process_memory
            )
        except Exception as e:
            logger.error(f"获取内存统计失败: {e}")
            return MemoryStats(0, 0, 0, 0, 0)
    
    def check_memory_status(self) -> str:
        """检查内存状态"""
        stats = self.get_memory_stats()
        
        if stats.percent_used >= self.critical_threshold:
            return "critical"
        elif stats.percent_used >= self.warning_threshold:
            return "warning"
        else:
            return "normal"
    
    def get_memory_usage_delta(self) -> float:
        """获取内存使用变化"""
        current = self.get_memory_stats()
        return current.process_mb - self.initial_memory.process_mb

class DataFrameOptimizer:
    """DataFrame内存优化器"""
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame, aggressive: bool = False) -> pd.DataFrame:
        """
        优化DataFrame数据类型
        
        参数:
        - df: 要优化的DataFrame
        - aggressive: 是否使用激进优化
        
        返回:
        - pd.DataFrame: 优化后的DataFrame
        """
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        optimized_df = df.copy()
        
        # 优化数值列
        for col in optimized_df.select_dtypes(include=['int64']).columns:
            col_min = optimized_df[col].min()
            col_max = optimized_df[col].max()
            
            if col_min >= -128 and col_max <= 127:
                optimized_df[col] = optimized_df[col].astype('int8')
            elif col_min >= -32768 and col_max <= 32767:
                optimized_df[col] = optimized_df[col].astype('int16')
            elif col_min >= -2147483648 and col_max <= 2147483647:
                optimized_df[col] = optimized_df[col].astype('int32')
        
        for col in optimized_df.select_dtypes(include=['float64']).columns:
            if aggressive:
                # 检查是否可以转换为int
                if optimized_df[col].fillna(0) % 1 == 0:
                    optimized_df[col] = optimized_df[col].astype('Int32')
                else:
                    optimized_df[col] = optimized_df[col].astype('float32')
            else:
                optimized_df[col] = optimized_df[col].astype('float32')
        
        # 优化对象列
        for col in optimized_df.select_dtypes(include=['object']).columns:
            if optimized_df[col].dtype == 'object':
                # 如果唯一值比例小于50%，转换为category
                if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                    optimized_df[col] = optimized_df[col].astype('category')
        
        optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logger.info(f"DataFrame内存优化: {original_memory:.1f}MB -> {optimized_memory:.1f}MB (减少{reduction:.1f}%)")
        
        return optimized_df
    
    @staticmethod
    def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """
        将DataFrame分块处理
        
        参数:
        - df: 要分块的DataFrame
        - chunk_size: 每块的大小
        
        返回:
        - Iterator[pd.DataFrame]: DataFrame块的迭代器
        """
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]
    
    @staticmethod
    def reduce_memory_usage(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        减少特定列的内存使用
        
        参数:
        - df: DataFrame
        - columns: 要优化的列名列表，None表示所有列
        
        返回:
        - pd.DataFrame: 优化后的DataFrame
        """
        if columns is None:
            columns = df.columns.tolist()
        
        for col in columns:
            if col in df.columns:
                col_type = df[col].dtype
                
                if col_type != 'object':
                    c_min = df[col].min()
                    c_max = df[col].max()
                    
                    if str(col_type)[:3] == 'int':
                        if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                            df[col] = df[col].astype(np.int8)
                        elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                            df[col] = df[col].astype(np.int16)
                        elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                            df[col] = df[col].astype(np.int32)
                    
                    elif str(col_type)[:5] == 'float':
                        if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            df[col] = df[col].astype(np.float32)
        
        return df

class ChunkedProcessor:
    """分块处理器"""
    
    def __init__(self, chunk_size: int = 10000, memory_limit_mb: float = 500):
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.monitor = MemoryMonitor()
    
    def process_large_dataset(self, 
                            data: Union[pd.DataFrame, List], 
                            process_func: Callable,
                            combine_func: Optional[Callable] = None) -> Any:
        """
        处理大数据集
        
        参数:
        - data: 要处理的数据
        - process_func: 处理函数
        - combine_func: 结果合并函数
        
        返回:
        - Any: 处理结果
        """
        results = []
        
        if isinstance(data, pd.DataFrame):
            chunks = DataFrameOptimizer.chunk_dataframe(data, self.chunk_size)
        else:
            chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        
        for i, chunk in enumerate(chunks):
            # 检查内存状态
            memory_status = self.monitor.check_memory_status()
            
            if memory_status == "critical":
                logger.warning("内存使用率过高，触发垃圾回收")
                gc.collect()
                
                # 再次检查
                memory_status = self.monitor.check_memory_status()
                if memory_status == "critical":
                    raise MemoryError("内存不足，无法继续处理")
            
            # 处理当前块
            try:
                result = process_func(chunk)
                results.append(result)
                
                logger.info(f"已处理块 {i + 1}, 内存使用: {self.monitor.get_memory_stats().process_mb:.1f}MB")
                
            except Exception as e:
                logger.error(f"处理块 {i + 1} 失败: {e}")
                raise
        
        # 合并结果
        if combine_func:
            return combine_func(results)
        elif results and isinstance(results[0], pd.DataFrame):
            return pd.concat(results, ignore_index=True)
        else:
            return results

class MemoryCache:
    """内存缓存管理器"""
    
    def __init__(self, max_size_mb: float = 100):
        self.max_size_mb = max_size_mb
        self.cache = {}
        self.access_times = {}
        self.sizes = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        if key in self.cache:
            self.access_times[key] = pd.Timestamp.now()
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any):
        """添加缓存项"""
        # 估算大小
        size_mb = self._estimate_size(value)
        
        # 检查是否需要清理
        while self._get_total_size() + size_mb > self.max_size_mb and self.cache:
            self._evict_lru()
        
        self.cache[key] = value
        self.access_times[key] = pd.Timestamp.now()
        self.sizes[key] = size_mb
    
    def _estimate_size(self, obj: Any) -> float:
        """估算对象大小（MB）"""
        try:
            if isinstance(obj, pd.DataFrame):
                return obj.memory_usage(deep=True).sum() / 1024 / 1024
            else:
                return len(pickle.dumps(obj)) / 1024 / 1024
        except:
            return 1.0  # 默认1MB
    
    def _get_total_size(self) -> float:
        """获取总缓存大小"""
        return sum(self.sizes.values())
    
    def _evict_lru(self):
        """移除最近最少使用的项"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        del self.cache[lru_key]
        del self.access_times[lru_key]
        del self.sizes[lru_key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
        self.sizes.clear()

@contextmanager
def memory_limit(limit_mb: float):
    """内存限制上下文管理器"""
    monitor = MemoryMonitor()
    initial_memory = monitor.get_memory_stats().process_mb
    
    try:
        yield monitor
    finally:
        current_memory = monitor.get_memory_stats().process_mb
        memory_used = current_memory - initial_memory
        
        if memory_used > limit_mb:
            logger.warning(f"内存使用超出限制: {memory_used:.1f}MB > {limit_mb}MB")
            gc.collect()

def optimize_for_memory(func: Callable):
    """内存优化装饰器"""
    def wrapper(*args, **kwargs):
        # 执行前清理
        gc.collect()
        
        monitor = MemoryMonitor()
        initial_stats = monitor.get_memory_stats()
        
        try:
            result = func(*args, **kwargs)
            
            # 如果结果是DataFrame，尝试优化
            if isinstance(result, pd.DataFrame):
                result = DataFrameOptimizer.optimize_dtypes(result)
            
            return result
            
        finally:
            # 执行后清理
            final_stats = monitor.get_memory_stats()
            memory_delta = final_stats.process_mb - initial_stats.process_mb
            
            if memory_delta > 50:  # 如果内存增长超过50MB
                logger.info(f"函数 {func.__name__} 内存增长: {memory_delta:.1f}MB，执行垃圾回收")
                gc.collect()
    
    return wrapper

def create_memory_monitor_ui():
    """创建内存监控UI"""
    monitor = MemoryMonitor()
    stats = monitor.get_memory_stats()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 内存监控")
    
    # 内存使用率
    memory_color = "normal"
    if stats.percent_used > 90:
        memory_color = "red"
    elif stats.percent_used > 80:
        memory_color = "orange"
    else:
        memory_color = "green"
    
    st.sidebar.metric(
        label="系统内存使用率",
        value=f"{stats.percent_used:.1f}%",
        delta=f"{stats.used_mb:.0f}MB / {stats.total_mb:.0f}MB"
    )
    
    st.sidebar.metric(
        label="进程内存使用",
        value=f"{stats.process_mb:.1f}MB"
    )
    
    # 内存优化按钮
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🗑️ 垃圾回收", help="强制执行垃圾回收"):
            gc.collect()
            st.sidebar.success("垃圾回收完成")
    
    with col2:
        if st.button("📊 内存详情", help="显示详细内存信息"):
            show_memory_details(stats)

def show_memory_details(stats: MemoryStats):
    """显示内存详情"""
    with st.sidebar.expander("📊 内存详情", expanded=True):
        st.write(f"**系统总内存**: {stats.total_mb:.0f} MB")
        st.write(f"**已使用内存**: {stats.used_mb:.0f} MB")
        st.write(f"**可用内存**: {stats.available_mb:.0f} MB")
        st.write(f"**进程内存**: {stats.process_mb:.1f} MB")
        
        # 内存使用率进度条
        st.progress(stats.percent_used / 100)
        
        # 内存优化建议
        if stats.percent_used > 80:
            st.warning("💡 建议：内存使用率较高，考虑减少数据集大小或重启应用")
        elif stats.percent_used > 60:
            st.info("💡 建议：定期执行垃圾回收以释放内存")
        else:
            st.success("💡 内存使用正常")
