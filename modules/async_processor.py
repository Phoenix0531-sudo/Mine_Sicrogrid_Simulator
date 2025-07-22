# -*- coding: utf-8 -*-
"""
异步处理模块 - 提升用户体验的异步计算架构
包含任务队列、进度跟踪、后台处理等功能
"""

import asyncio
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """任务结果数据类"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """
        提交异步任务
        
        参数:
        - func: 要执行的函数
        - args, kwargs: 函数参数
        
        返回:
        - str: 任务ID
        """
        task_id = str(uuid.uuid4())
        
        with self._lock:
            self.tasks[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.PENDING,
                start_time=datetime.now()
            )
        
        # 创建并启动线程
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_id, func, args, kwargs),
            daemon=True,
            name=f"task_{task_id}"  # 设置线程名称以便进度跟踪
        )
        
        self.running_tasks[task_id] = thread
        thread.start()
        
        logger.info(f"任务 {task_id} 已提交")
        return task_id
    
    def _execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict):
        """执行任务的内部方法"""
        try:
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.RUNNING
                    self.tasks[task_id].start_time = datetime.now()
            
            logger.info(f"开始执行任务 {task_id}")
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 更新任务状态
            end_time = datetime.now()
            with self._lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.end_time = end_time
                    task.progress = 1.0
                    if task.start_time:
                        task.execution_time = (end_time - task.start_time).total_seconds()
            
            logger.info(f"任务 {task_id} 执行完成")
            
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")
            
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.FAILED
                    self.tasks[task_id].error = str(e)
                    self.tasks[task_id].end_time = datetime.now()
        
        finally:
            # 清理线程引用
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        with self._lock:
            return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self.tasks and self.tasks[task_id].status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                self.tasks[task_id].end_time = datetime.now()
                
                # 尝试停止线程（注意：Python线程无法强制停止）
                if task_id in self.running_tasks:
                    logger.warning(f"任务 {task_id} 已标记为取消，但线程可能仍在运行")
                
                return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的旧任务"""
        current_time = datetime.now()
        to_remove = []
        
        with self._lock:
            for task_id, task in self.tasks.items():
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                    and task.end_time 
                    and (current_time - task.end_time).total_seconds() > max_age_hours * 3600):
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
        
        if to_remove:
            logger.info(f"清理了 {len(to_remove)} 个过期任务")

# 全局任务管理器实例
task_manager = AsyncTaskManager()

def async_computation(func: Callable):
    """
    异步计算装饰器
    
    使用方法:
    @async_computation
    def heavy_computation():
        # 耗时计算
        return result
    """
    def wrapper(*args, **kwargs):
        return task_manager.submit_task(func, *args, **kwargs)
    return wrapper

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.current_step = 0
        self.total_steps = 100
    
    def update_progress(self, step: int, total: int = None, message: str = ""):
        """更新进度"""
        if total:
            self.total_steps = total
        self.current_step = step
        
        progress = min(step / self.total_steps, 1.0)
        
        with task_manager._lock:
            if self.task_id in task_manager.tasks:
                task_manager.tasks[self.task_id].progress = progress
        
        if message:
            logger.info(f"任务 {self.task_id}: {message} ({progress*100:.1f}%)")

def create_progress_ui(task_id: str, title: str = "处理中..."):
    """
    创建进度显示UI
    
    参数:
    - task_id: 任务ID
    - title: 显示标题
    
    返回:
    - TaskResult: 任务结果（如果完成）
    """
    task = task_manager.get_task_status(task_id)
    
    if not task:
        st.error("任务不存在")
        return None
    
    # 创建进度显示
    if task.status == TaskStatus.PENDING:
        st.info("⏳ 任务等待中...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("准备开始...")
        
    elif task.status == TaskStatus.RUNNING:
        st.info(f"🔄 {title}")
        progress_bar = st.progress(task.progress)
        status_text = st.empty()
        
        if task.start_time:
            elapsed = (datetime.now() - task.start_time).total_seconds()
            status_text.text(f"已运行 {elapsed:.1f} 秒 - 进度: {task.progress*100:.1f}%")
        else:
            status_text.text(f"进度: {task.progress*100:.1f}%")
        
        # 添加取消按钮
        if st.button("❌ 取消任务", key=f"cancel_{task_id}"):
            if task_manager.cancel_task(task_id):
                st.warning("任务已取消")
                st.rerun()
        
    elif task.status == TaskStatus.COMPLETED:
        st.success("✅ 任务完成！")
        if task.execution_time:
            st.info(f"⏱️ 执行时间: {task.execution_time:.2f} 秒")
        return task
        
    elif task.status == TaskStatus.FAILED:
        st.error(f"❌ 任务失败: {task.error}")
        return task
        
    elif task.status == TaskStatus.CANCELLED:
        st.warning("⚠️ 任务已取消")
        return task
    
    # 自动刷新页面以更新进度
    if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        time.sleep(1)
        st.rerun()
    
    return None

def batch_processor(items: list, process_func: Callable, batch_size: int = 100, task_id: str = None):
    """
    批处理器 - 分批处理大数据集
    
    参数:
    - items: 要处理的项目列表
    - process_func: 处理函数
    - batch_size: 批处理大小
    - task_id: 任务ID（用于进度跟踪）
    
    返回:
    - list: 处理结果列表
    """
    results = []
    total_batches = len(items) // batch_size + (1 if len(items) % batch_size else 0)
    
    tracker = ProgressTracker(task_id) if task_id else None
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = []
        
        for item in batch:
            try:
                result = process_func(item)
                batch_results.append(result)
            except Exception as e:
                logger.error(f"批处理项目失败: {e}")
                batch_results.append(None)
        
        results.extend(batch_results)
        
        # 更新进度
        if tracker:
            current_batch = i // batch_size + 1
            tracker.update_progress(
                current_batch, 
                total_batches, 
                f"已处理 {current_batch}/{total_batches} 批次"
            )
    
    return results
